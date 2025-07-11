import boto3
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from app.services.embeddings_util import process_file_and_store_embeddings

def embeddings_exist(filename):
    conn = psycopg2.connect(
        dbname="data_lake",
        user="postgres",
        password="postgres",
        host="db",
        port=5432
    )
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM vector_store WHERE filename = %s LIMIT 1", (filename,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def load_dataframe(filepath):
    import os
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(filepath)
        elif ext == ".json":
            return pd.read_json(filepath)
        elif ext == ".parquet":
            return pd.read_parquet(filepath)
        else:
            print(f"Skipping unsupported file type: {filepath}")
            return None
    except Exception as e:
        print(f"Failed to load {filepath}: {e}")
        return None

def sync_embeddings_from_s3():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        region_name=os.getenv("S3_REGION", "us-east-2")
    )
    bucket = os.getenv("S3_BUCKET_NAME")
    
    for obj in s3.list_objects_v2(Bucket=bucket).get('Contents', []):
        filename = obj['Key']
        if not embeddings_exist(filename):
            # Download file from S3
            local_path = f"/tmp/{filename}"
            s3.download_file(bucket, filename, local_path)
            # Load file into DataFrame
            df = load_dataframe(local_path)
            if df is not None:
                process_file_and_store_embeddings(filename, df)
                print(f"Added embeddings for: {filename}")
            else:
                print(f"Skipped (unsupported or failed to load): {filename}")
        
        else:
            print(f"Embeddings already exist for: {filename}")

if __name__ == "__main__":
    sync_embeddings_from_s3()