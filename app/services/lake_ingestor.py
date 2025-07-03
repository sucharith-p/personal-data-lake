import boto3
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid

from app.db.session import get_db
from app.db.models import Dataset

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    region_name=os.getenv("S3_REGION", "us-east-2")
)

def store_file_and_metadata(filename, df, schema):
    key = f"{uuid.uuid4()}_{filename}"
    csv_bytes = df.to_csv(index=False).encode("utf-8")

    s3.put_object(
        Bucket=os.getenv("S3_BUCKET_NAME"),
        Key=key,
        Body=csv_bytes
    )

    # Store metadata in DB
    db = next(get_db())
    dataset = Dataset(
        name=filename,
        s3_key=key,
        schema=str(schema),
        upload_time=datetime.now(timezone.utc)
    )
    db.add(dataset)
    db.commit()

    return key