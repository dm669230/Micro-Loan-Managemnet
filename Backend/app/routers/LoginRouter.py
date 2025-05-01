
from fastapi import APIRouter, Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from app.db.session import get_db
from app.schemas import auth_schema as auth_schema
from app.contollers.LoginController import register_new_user,login



router = APIRouter()

@router.post("/login")
def login_fun(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db:Session=Depends(get_db)):
    response = login(form_data, db)
    return response

@router.post("/registration")
def user_register(new_user_schema:auth_schema.NewUserRegisterSchema, db:Session=Depends(get_db)):
    response = register_new_user(new_user_schema,db)
    return response
