from fastapi import APIRouter, UploadFile, File
from app.services.file_parser import parse_and_infer
from app.services.lake_ingestor import store_file_and_metadata
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db
from app.db.models import Dataset
import boto3
import os
import pytz

router = APIRouter()

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    df, schema = await parse_and_infer(file)
    file_url = store_file_and_metadata(file.filename, df, schema)
    return {"status": "success", "file_url": file_url}


@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL")
    )
    bucket_name = os.getenv("S3_BUCKET_NAME")

    try:
        s3_objects = s3.list_objects_v2(Bucket=bucket_name).get("Contents", [])
        s3_keys = [obj["Key"] for obj in s3_objects]
        sizes = {obj["Key"]: obj["Size"] for obj in s3_objects}
        last_modified = {obj["Key"]: obj["LastModified"] for obj in s3_objects}
    except Exception as e:
        return {"error": f"Failed to list objects in S3: {str(e)}"}

    datasets = db.query(Dataset).filter(Dataset.s3_key.in_(s3_keys)).all()

    local_tz = pytz.timezone("America/New_York")  # replace with your timezone

    return [
        {
            "dataset_name": ds.name,
            "upload_time": last_modified[ds.s3_key].astimezone(local_tz).strftime("%Y-%m-%d %I:%M %p"),
            "file_size_kb": round(sizes[ds.s3_key] / 1024, 2),
        }
        for ds in datasets
    ]

from fastapi.responses import JSONResponse

@router.delete("/datasets/cleanup")
def cleanup_orphaned_metadata(db: Session = Depends(get_db)):
    # Setup S3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL")
    )
    bucket_name = os.getenv("S3_BUCKET_NAME")

    try:
        s3_objects = s3.list_objects_v2(Bucket=bucket_name).get("Contents", [])
        existing_keys = set(obj["Key"] for obj in s3_objects)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"S3 list failed: {str(e)}"})

    all_datasets = db.query(Dataset).all()
    deleted = []

    for ds in all_datasets:
        if ds.s3_key not in existing_keys:
            deleted.append(ds.name)
            db.delete(ds)

    db.commit()

    return {
        "deleted_count": len(deleted),
        "deleted_datasets": deleted
    }