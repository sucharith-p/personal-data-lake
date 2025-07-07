# 🧊 Personal Data Lake-as-a-Service

A lightweight, containerized data lake solution that lets you upload, store, query, and export structured data files (CSV, JSON, Parquet) via a modern web interface.

## ✨ Features

- 📤 Upload structured files (CSV, JSON, Parquet)
- 📁 Manage uploaded datasets backed by AWS S3
- 🧠 Run SQL queries using an embedded engine
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
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```

### 3. Build and Start the Containers
```bash
docker-compose up --build
```
This launches:
-	🚀 FastAPI backend at http://localhost:8000
-	🧊 Streamlit frontend at http://localhost:8501

## 🖥️ Project Structure

personal-data-lake/
│
├── backend/                # FastAPI backend
│   ├── main.py             # API entry point
│   ├── routes/             # Upload, export, query endpoints
│   └── services/           # Logic for S3 & SQL interaction
│
├── streamlit_app/          # Streamlit frontend
│   └── app.py              # Main app UI
│
├── sample/                 # Sample datasets for demo mode
│
├── .env                    # AWS credentials (not committed)
├── docker-compose.yml      # Docker orchestration
└── README.md

## 🧪 How It Works

1.	Visit http://localhost:8501
2.	Land on the Demo Mode homepage with sample data
3.	Click “Connect to Your S3” and input AWS credentials
4.	View and interact with your own S3 data securely
5.	Upload files, run SQL queries, and download/export results

## 🔐 Auth & Credential Management
- 🧪 Demo mode uses static sample data
- 🔑 Authenticated mode uses User-entered AWS credentials in .env file
- ✅ All requests from Streamlit to FastAPI include temporary headers for user-specific S3 interaction

## 🔄 API Endpoints (Backend)
- POST /upload: Upload a dataset to S3
- GET /datasets: List datasets in your S3 bucket
- POST /query: Run SQL on uploaded datasets
- POST /export: Save query result back to S3
- DELETE /datasets/cleanup: Clean up metadata (if needed)

## 🛠️ Development Tips
- Modify UI logic in streamlit_app/app.py
- Modify API behavior in backend/main.py and backend/services/
- Add new REST endpoints in backend/routes/
- Sample data lives in sample/ folder for easy customization

## 📈 Roadmap
- Add user auth with login/session support
- Use AWS STS temporary credentials for enhanced security
- Deployable on ECS, EC2, or Kubernetes
- Integration with Superset or Grafana for visual exploration

## 🧾 License
MIT License © 2025 [Sucharith P]

## 🤝 Contributing
If you’d like to contribute, fork the repo and submit a PR!
Issues, suggestions, and discussions are always welcome.
