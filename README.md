# 🧊 Personal Data Lake-as-a-Service

A lightweight, containerized data lake solution that lets you upload, store, query, and export structured data files (CSV, JSON, Parquet) via a modern web interface. Now with automatic semantic embedding and vector search support!

## ✨ Features

- 📤 Upload structured files (CSV, JSON, Parquet)
- 📁 Manage uploaded datasets backed by AWS S3
- 🧠 **Automatic semantic embeddings:**
  - Embeddings are created for all S3 files at backend startup (if not already present)
  - Embeddings are created on upload as before
  - Robust to unsupported or malformed files (skips and logs them)
- 🔎 Semantic search powered by Postgres + pgvector
- 🧾 Vector store for fast similarity search
- 🔄 Backend uses FastAPI lifespan event for startup tasks (no deprecated on_event)
- 🖼️ Streamlit frontend with logo, custom sidebar arrow hiding, and improved navigation (e.g., back button in chat)
- 📄 Download or export query results to S3
- 🌐 Streamlit frontend + FastAPI backend
- 🐳 Fully Dockerized for local and cloud deployment
- 🔐 Now supports **dynamic user S3 credentials via `.env` or UI authentication**

---

## 📦 Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
- **Storage:** AWS S3
- **Query Engine:** DuckDB (via FastAPI)
- **Vector Store:** Postgres + [pgvector](https://github.com/pgvector/pgvector)
- **Embeddings:** Sentence Transformers
- **Containerization:** Docker & Docker Compose
- **Communication:** REST (FastAPI <-> Streamlit)
- **Auth Mode:** Environment-based AWS credentials

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/personal-data-lake.git
cd personal-data-lake
```

### 2. Add your AWS Credentials
Create a .env file in the root directory with the following content:
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=your-s3-bucket-region
S3_BUCKET_NAME=your-s3-bucket-name
OPENAI_API_KEY=your-openai-api-secret
DB_URL=postgresql://postgres:postgres@localhost:5432/data_lake
```

### 3. Build and Start the Containers
```bash
docker-compose up --build
```
This launches:
- 🚀 FastAPI backend at http://localhost:8000
- 🧊 Streamlit frontend at http://localhost:8501

## 🖥️ Project Structure
```text
personal-data-lake/
│
├── app/                      # FastAPI backend & embedding logic
│   ├── main.py               # API entry point (with startup embedding sync)
│   ├── api/                  # Upload, export, query endpoints
│   ├── services/             # Logic for S3, SQL, and embeddings
│   └── sync_embeddings.py    # Embedding sync logic (run at startup)
│
├── ui/                       # Streamlit frontend
│   ├── app.py                # Main app UI (with logo, sidebar tweaks)
│   └── pages/                # Multipage Streamlit (e.g., chat)
│
├── scripts/                  # (Optional) Standalone scripts
│
├── .env                      # AWS credentials (not committed)
├── docker-compose.yml        # Docker orchestration
└── README.md
```

## 🧪 How It Works

1. Visit http://localhost:8501
2. Land on the homepage with your logo and navigation
3. On backend startup, all S3 files are checked for embeddings; missing ones are processed and added to the vector store
4. Uploading a new file also triggers embedding creation
5. View and interact with your S3 data securely
6. Upload files, run SQL queries, semantic search, and download/export results

## 🧠 Embedding Sync & Vector Store
- On backend startup, all files in S3 are checked for embeddings in the vector store (Postgres + pgvector).
- If a file is missing embeddings, it is downloaded, parsed, and embedded (CSV, JSON, Parquet supported by default).
- Unsupported or malformed files are skipped and logged.
- Embeddings are also created immediately on file upload.
- The backend uses FastAPI's lifespan event for startup tasks (no deprecated on_event).

## 📝 Extending File Type Support
- To support text files (.txt), add logic to read and chunk text, then convert to a DataFrame for embedding.
- To support PDFs, use a library like PyPDF2 to extract text, then chunk and embed.
- See `app/sync_embeddings.py` for extension points.

## 📋 Logging & Monitoring
- All embedding sync actions are logged to stdout (visible in Docker logs).
- Skipped or failed files are logged with reasons.
- You can add more advanced logging or monitoring as needed.

## 🔄 API Endpoints (Backend)
- POST /upload: Upload a dataset to S3 (triggers embedding)
- GET /datasets: List datasets in your S3 bucket
- POST /query: Run SQL on uploaded datasets
- POST /export: Save query result back to S3
- DELETE /datasets/cleanup: Clean up metadata (if needed)

## 🛠️ Development Tips
- Modify UI logic in `ui/app.py` and `ui/pages/`
- Modify API and embedding behavior in `app/main.py` and `app/services/`
- Add new REST endpoints in `app/api/`
- Add or extend embedding logic in `app/sync_embeddings.py`
- Sample data lives in sample/ folder for easy customization

## 🧾 Troubleshooting
- **Import errors:** Ensure your `PYTHONPATH` includes the project root, especially in Docker.
- **File type errors:** Only CSV, JSON, and Parquet are supported by default for embeddings. Others are skipped and logged.
- **Malformed files:** Files that cannot be parsed are skipped and logged.
- **Vector store issues:** Ensure Postgres is running and has the `pgvector` extension enabled.
- **Environment variables:** Make sure your `.env` is loaded and all required variables are set.

## 📈 Roadmap
- Add user auth with login/session support
- Use AWS STS temporary credentials for enhanced security
- Deployable on ECS, EC2, or Kubernetes
- Integration with Superset or Grafana for visual exploration
- More file type support for embeddings (text, PDF, etc.)

## 🧾 License
MIT License

Copyright (c) 2025 Sucharith

## 🤝 Contributing
If you’d like to contribute, fork the repo and submit a PR!
Issues, suggestions, and discussions are always welcome.
