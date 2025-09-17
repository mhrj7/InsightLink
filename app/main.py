import os
import shortuuid
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

import redis
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- Application Setup ---
app = FastAPI(title="InsightLink")

# --- Database Setup ---
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Redis Setup ---
REDIS_HOST = os.environ.get("REDIS_HOST")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# --- Database Models ---
class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True)
    long_url = Column(String)

class Click(Base):
    __tablename__ = "clicks"
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String, nullable=True)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# --- Pydantic Models ---
class URLCreate(BaseModel):
    url: str

class ClickInfo(BaseModel):
    timestamp: datetime
    user_agent: str | None = None

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    short_code: str
    click_count: int
    clicks: List[ClickInfo]

# --- Helper Function ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to InsightLink URL Shortener"}

@app.post("/url", status_code=201)
def create_url(url_data: URLCreate):
    db = next(get_db())
    short_code = shortuuid.uuid()[:8]

    db_url = URL(short_code=short_code, long_url=url_data.url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # Cache the new URL
    redis_client.set(db_url.short_code, db_url.long_url)

    return {"long_url": db_url.long_url, "short_url": f"http://localhost:8001/{db_url.short_code}"}

@app.get("/{short_code}")
def redirect_url(short_code: str, request: Request):
    db = next(get_db())

    # 1. Check cache first
    cached_url = redis_client.get(short_code)
    if cached_url:
        print("Cache hit!")
        click_event = Click(short_code=short_code, user_agent=request.headers.get("user-agent"))
        db.add(click_event)
        db.commit()
        return RedirectResponse(url=cached_url, status_code=302)

    # 2. If not in cache, check the database
    print("Cache miss!")
    db_url = db.query(URL).filter(URL.short_code == short_code).first()

    # Raise an HTTPException if the URL is not found
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    # 3. Create a new click event before redirecting
    click_event = Click(short_code=short_code, user_agent=request.headers.get("user-agent"))
    db.add(click_event)
    db.commit()

    # 4. Store in cache for next time and redirect
    redis_client.set(db_url.short_code, db_url.long_url)
    return RedirectResponse(url=db_url.long_url, status_code=302)


@app.get("/analytics/{short_code}", response_model=AnalyticsResponse)
def get_analytics(short_code: str):
    db = next(get_db())

    # Check if the link exists
    db_url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    # Query for all clicks and count them
    clicks = db.query(Click).filter(Click.short_code == short_code).order_by(Click.timestamp.desc()).all()
    click_count = len(clicks)

    return {
        "short_code": short_code,
        "click_count": click_count,
        "clicks": clicks
    }

