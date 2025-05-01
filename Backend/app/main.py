from fastapi import FastAPI,APIRouter, Depends, HTTPException, Request
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.routers.LoginRouter import router as auth_router
from app.routers.AdminRouter import router as admin_router
from app.routers.LoanManageRouter import router as loan_manage_router
# from Backend.app.db.session import SessionLocal, get_db
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.base import Base, engine
from typing_extensions import Annotated
from .config import config
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(override=True)
# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
# Allow your frontend origin (e.g., React running on localhost:3000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or use ["*"] for all origins (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "Hello world !"}

@lru_cache
def get_settings():
    return config.Settings()

print("my_settings",get_settings())

@app.get("/info")
async def info(settings:Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.APP_NAME,
        "admin_email": settings.ADMIN_EMAIL,
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        print("Checking database connection...", db)
        db.execute("SELECT 1")  # Simple query to check DB connection
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

app.include_router(auth_router, prefix="/auth", tags=["AuthenticationAPI's"])
app.include_router(admin_router, prefix="/admin", tags=["AdminAPI's"])
app.include_router(loan_manage_router, prefix="/manageloan",tags=["LoanManageAPI's"])


