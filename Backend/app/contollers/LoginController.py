# from app.config.db import  get_db
from sqlalchemy.orm import Session
import bcrypt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import base64, hashlib
from psycopg2 import Binary
from datetime import timedelta, timezone, datetime
from typing import Annotated
from pydantic import BaseModel
import jwt
from app.schemas import auth_schema as auth_schema
from app.models import model as mdl
from app.utils import utils
from fastapi import Depends, HTTPException, status
import traceback
from app.config import config
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(override=True)
# from app.config.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

settings = config.Settings()


class Token(BaseModel):
    access_token: str
    token_type: str

def hash_password(password: str) -> (str, str):
    # Generate a salt and hash the password with bcrypt
    salt = bcrypt.gensalt(rounds=14)
    bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Now, hash the bcrypt result with SHA-256 to make it longer
    sha256_hash = hashlib.sha256(bcrypt_hash).hexdigest()

    # Return the SHA-256 hash and the base64-encoded salt
    return sha256_hash, base64.b64encode(salt).decode('utf-8')

def validate_password(entered_password: str, stored_hash: str, stored_salt: str) -> bool:
    # Decode the stored salt back to bytes
    salt_bytes = base64.b64decode(stored_salt)
    
    # Hash the entered password using the stored salt
    bcrypt_hash = bcrypt.hashpw(entered_password.encode('utf-8'), salt_bytes)
    
    # Hash the bcrypt result with SHA-256 to match the stored hash
    sha256_hash = hashlib.sha256(bcrypt_hash).hexdigest()
        
    # Compare the result with the stored hash
    return sha256_hash == stored_hash

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def register_new_user(new_user_schema:auth_schema.NewUserRegisterSchema, db):
    try:
        has_pass, has_salt = hash_password(new_user_schema.password_hash)
        print('hash_pass : ', has_pass)
        db_user = mdl.UsersModel(name=new_user_schema.name, 
                            email = new_user_schema.email,
                            # phone_no = new_user_schema.phone_no,
                            # username = new_user_schema.username,
                            password_hash = has_pass,
                            salt = has_salt)
        
        db.add(db_user)
        db.commit()

        return "User Added Sucessfully"
    except Exception as e:
        traceback.print_exc()
        print(f"Error occured due to : {e}")
        return f"Error occured due to : {e}"
    

def login(form_data, db):
    email = form_data.username
    user_record = db.query(mdl.UsersModel).filter(mdl.UsersModel.email == email).first()
    
    if not user_record:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    entered_password = form_data.password
    
    # Get the stored password salt hash
    stored_hash = user_record.password_hash
    stored_salt = user_record.salt
    is_exist = validate_password(entered_password, stored_hash=stored_hash,stored_salt=stored_salt )

    # Compare the double hashed entered password with the stored hash
    if not is_exist:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"name": user_record.name,
                                             "username": user_record.email, 
                                             "user_id":user_record.id,
                                             "is_admin" : user_record.is_admin
                                             }, 
                                             expires_delta=access_token_expires)
    # If the credentials are correct
    
    response = utils.HttpResponseFormatter(data=[Token(access_token=access_token, token_type="bearer")], response_code=200, message="User Login Successfull")
    return response





    