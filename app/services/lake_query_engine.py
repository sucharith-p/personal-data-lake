import boto3
import os
import duckdb
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from app.db.session import get_db
from app.db.models import Dataset


load_dotenv()

def run_query_on_dataset(sql: str):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    )

    bucket = os.getenv("S3_BUCKET_NAME")
    db = next(get_db())

    # Get all dataset metadata from Postgres
    datasets = db.query(Dataset).all()

    con = duckdb.connect()

    for ds in datasets:
        # Download each file from S3
        obj = s3.get_object(Bucket=bucket, Key=ds.s3_key)
        df = pd.read_csv(BytesIO(obj["Body"].read()))

        # Use the dataset name (without extension) as table name
        table_name = ds.name.rsplit(".", 1)[0].replace(" ", "_")
        con.register(table_name, df)

    result = con.execute(sql).fetchall()
    col_names = [desc[0] for desc in con.description]
    return [dict(zip(col_names, row)) for row in result]