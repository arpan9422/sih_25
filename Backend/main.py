from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import Base, engine
import models
from routes import profiles, measurements
from fastapi.middleware.cors import CORSMiddleware
from llm import query_ocean_data  # <-- fix import
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db  # <-- your session dependency

# Create DB tables (for dev only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="🌊 Argo Backend API")

class QueryRequest(BaseModel):
    query: str

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
app.include_router(measurements.router, prefix="/measurements", tags=["Measurements"])

@app.get("/")
def root():
    return {"message": "🌊 Argo Backend API is running"}

# 👇 use app.post instead of router.post
@app.post("/query", tags=["LLM"])
def run_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        result = query_ocean_data(request.query, db)  # pass db session
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
