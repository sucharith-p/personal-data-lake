from sentence_transformers import SentenceTransformer
import psycopg2
import pgvector
import hashlib

model = SentenceTransformer("all-MiniLM-L6-v2")  # or your choice

def process_file_and_store_embeddings(filename, df):
    texts = df.astype(str).apply(lambda row: " | ".join(row), axis=1).tolist()
    embeddings = model.encode(texts).tolist()

    conn = psycopg2.connect(
        dbname="data_lake",
        user="postgres",
        password="postgres",
        host="db",
        port=5432
    )  # Connect to your pgvector-enabled Postgres
    cur = conn.cursor()

    for i, (text, emb) in enumerate(zip(texts, embeddings)):
        uid = hashlib.md5(f"{filename}_{i}".encode()).hexdigest()
        cur.execute("""
            INSERT INTO vector_store (id, filename, chunk_text, embedding)
            VALUES (%s, %s, %s, %s::vector)
            ON CONFLICT (id) DO NOTHING;
        """, (uid, filename, text, emb))

    conn.commit()
    conn.close()