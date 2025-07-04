from fastapi import FastAPI
from app.api import upload, query
from app.api.export import router as export_router

app = FastAPI()
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(export_router)