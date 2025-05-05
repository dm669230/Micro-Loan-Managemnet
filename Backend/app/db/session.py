from sqlalchemy.orm import sessionmaker
from app.db.base import engine
import redis

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis_client():
    client = redis.Redis(host="localhost", port=6379, db=0)
    return client



