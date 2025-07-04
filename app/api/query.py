from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from app.services.lake_query_engine import run_query_on_dataset

router = APIRouter()

class QueryRequest(BaseModel):
    sql: str

@router.post("/query")
def query_dataset(payload: QueryRequest):
    try:
        results = run_query_on_dataset(payload.sql)
        return {"rows": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))