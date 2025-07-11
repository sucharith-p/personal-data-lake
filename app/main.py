from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import upload, query
from app.api.export import router as export_router
from app.sync_embeddings import sync_embeddings_from_s3
import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    threading.Thread(target=sync_embeddings_from_s3, daemon=True).start()
    yield
    # (Optional) Shutdown logic here

app = FastAPI(lifespan=lifespan)
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(export_router)