from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Dataset
from app.services.lake_ingestor import store_file_and_metadata
from app.services.lake_query_engine import run_query_on_dataset
import boto3, os
import pandas as pd
from io import BytesIO
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/export")
def export_query_to_s3(
    sql: str = Body(...),
    output_format: str = Body("csv"),
    filename: str = Body(default=None),
    db: Session = Depends(get_db)
):
    try:
        rows = run_query_on_dataset(sql)
        if not rows:
            raise HTTPException(status_code=400, detail="Query returned no data")

        # Generate filename
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
        else:
            filename = f"{filename}.{output_format}"

        s3_key = f"{filename}"
        bucket = os.getenv("S3_BUCKET_NAME")
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL")
        )

        # Convert DataFrame to chosen format
        df = pd.DataFrame(rows)
        buf = BytesIO()
        if output_format == "csv":
            df.to_csv(buf, index=False)
        elif output_format == "parquet":
            df.to_parquet(buf, index=False)
        elif output_format == "json":
            buf.write(df.to_json(orient="records", indent=2).encode("utf-8"))
        else:
            raise HTTPException(status_code=400, detail="Invalid format")

        # Upload to S3
        buf.seek(0)
        s3.put_object(Bucket=bucket, Key=s3_key, Body=buf.getvalue())

        # file_size_kb = len(buf.getvalue()) / 1024
        # dataset = Dataset(
        #     id=str(uuid.uuid4()),
        #     name=filename,
        #     s3_key=s3_key,
        #     schema=str(dict(df.dtypes.apply(lambda x: x.name))),
        #     upload_time=datetime.now(),
        #     file_size_kb=round(file_size_kb, 2)
        # )
        # db.add(dataset)
        # db.commit()
        file_url = store_file_and_metadata(filename, df, str(dict(df.dtypes.apply(lambda x: x.name))))


        return {"status": "success", "file_url": file_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))