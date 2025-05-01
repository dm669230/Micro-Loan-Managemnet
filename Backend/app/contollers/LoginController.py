
import bcrypt
import base64, hashlib
from datetime import timedelta, timezone, datetime
from pydantic import BaseModel
import jwt
from app.schemas import auth_schema as auth_schema
from app.models import model as mdl
from app.utils import utils
from fastapi import HTTPException
import traceback
from app.config import config
from dotenv import load_dotenv

load_dotenv(override=True)

settings = config.Settings()


class Token(BaseModel):
    access_token: str
    token_type: str

def hash_password(password: str) -> (str, str):
    salt = bcrypt.gensalt(rounds=14)
    bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    sha256_hash = hashlib.sha256(bcrypt_hash).hexdigest()

    return sha256_hash, base64.b64encode(salt).decode('utf-8')

def validate_password(entered_password: str, stored_hash: str, stored_salt: str) -> bool:
    salt_bytes = base64.b64decode(stored_salt)
    bcrypt_hash = bcrypt.hashpw(entered_password.encode('utf-8'), salt_bytes)
    sha256_hash = hashlib.sha256(bcrypt_hash).hexdigest()
        
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

    if not is_exist:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"name": user_record.name,
                                             "username": user_record.email, 
                                             "user_id":user_record.id,
                                             "is_admin" : user_record.is_admin
                                             }, 
                                             expires_delta=access_token_expires)
    
    response = utils.HttpResponseFormatter(data=[Token(access_token=access_token, token_type="bearer")], response_code=200, message="User Login Successfull")
    return response





    