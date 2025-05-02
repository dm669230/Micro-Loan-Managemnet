from fastapi import APIRouter, Depends,Body, Request
from app.db.session import get_db, get_redis_client
import jwt
from jwt import PyJWTError
import time
from app.schemas.loan_manage_schema import NewLoanApplySchema, UpdateLoanStatusSchema
from sqlalchemy.orm import Session
from app.contollers.LoanManageController import apply_new_loan, get_loan_status, update_loan_status
from app.models import model as mdl
from fastapi.responses import JSONResponse
from functools import wraps
from app.config import config

setting = config.Settings()

router = APIRouter()

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        req = kwargs.get("req")
        db = kwargs.get("db")
        headers =  req.headers
        print("headers999", req.headers)
        if not headers or not headers.get("Authorization"):
            return JSONResponse({"message":"Authentication Credentials were Not Provided"})
        token = headers.get('Authorization').split(' ')[1]
        
        try:
            decoded = jwt.decode(token, setting.SECRET_KEY, algorithms=["HS256"])

            
            print("decoded username id", decoded)
        except PyJWTError:
            return JSONResponse({"message": "Invalid token"}, status_code=401)
        exp = decoded.get("exp")
        if exp < int(time.time()):
            return JSONResponse({"message": "Token Expired"}, status_code=401)
        username = decoded.get("username")

        user_id = decoded.get("user_id")
        exist_user = db.query(mdl.UsersModel).filter(mdl.UsersModel.id == user_id).first()
        if exist_user and exist_user.email == username:
            # req.user = exist_user
            req.state.user = exist_user  # ✅ Set user in req.stateassign req.user
            return func(*args, **kwargs)
        return JSONResponse({"message": "user does not exist"})
    return wrapper

@router.get("/loan_management")
def loan_management():
    print("hi loan management dashboard !")

@router.post("/loan_application")
@login_required
def loan_apply(req : Request, loan_apply_schema: NewLoanApplySchema, 
               redis_client:Session=Depends(get_redis_client), db:Session=Depends(get_db)):
    response = apply_new_loan(req, loan_apply_schema, redis_client, db)
    return response

@router.get("/get_all_loans")
@login_required
def get_loans(req : Request, redis_client:Session=Depends(get_redis_client), db:Session=Depends(get_db)):
    response = get_loan_status(req, redis_client, db)
    return response

@router.patch("/update/{loan_id}")
@login_required
def loan_status(loan_id : int, req : Request, loan_status : UpdateLoanStatusSchema , db:Session = Depends(get_db)):
    response = update_loan_status(req, loan_id, loan_status, db)
    return response
