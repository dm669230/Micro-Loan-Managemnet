from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from app.config.config import settings
import urllib.parse

DB_PASSWORD_PARSE = urllib.parse.quote_plus(settings.DB_PASSWORD)
DATABASE_URL = f"postgresql://{settings.DB_USER}:{DB_PASSWORD_PARSE}@{settings.SERVER_HOST}:{settings.SERVER_PORT}/{settings.DB_NAME}"

print("DATABASE_URL", DATABASE_URL)
engine = create_engine(DATABASE_URL)
Base = declarative_base()
