# from app.config.db import  get_db
from sqlalchemy.orm import Session
import json
import redis.exceptions
from datetime import datetime, timedelta
import time
from fastapi import Depends, HTTPException, status
import traceback
import jwt
from sqlalchemy import desc, update
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.schemas import loan_manage_schema as LM_schema
from app.models import model as mdl
from app.utils import utils
from app.config import config

setting = config.Settings()
from dotenv import load_dotenv

load_dotenv(override=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def apply_new_loan(req, loan_apply_schema, redis_client, db):
    try:
        user_record_from_token = req.state.user
        print("user_record_from_token", user_record_from_token)
        user_id = user_record_from_token.id
        new_loan = mdl.LoansModel(
            user_id=user_id,
            loan_amount=loan_apply_schema.loan_amount, 
            interest_rate=loan_apply_schema.interest_rate,
            start_date=loan_apply_schema.start_date,
            end_date=loan_apply_schema.end_date,
            updated_at=datetime.utcnow() 
        )
        
        db.add(new_loan)
        db.commit()
        
        latest_loans = db.query(mdl.LoansModel).filter(mdl.LoansModel.user_id == user_id).order_by(desc(mdl.LoansModel.created_at)).all()

        loan_data = []
        for loan in latest_loans:
            loan_data.append(
                {
                    "user_id": loan.user_id,
                    "user_name": user_record_from_token.name,
                    "user_email": user_record_from_token.email,   
                    "loan_id": loan.id,
                    "loan_amount": loan.loan_amount,
                    "interest_rate": loan.interest_rate,
                    "loan_status": loan.loan_status,
                }
            )
        
        try:
            redis_key = f"loan_data:{user_id}"
            redis_client.set(redis_key, json.dumps(loan_data), ex=600) 
        except redis.exceptions.RedisError as e:
            print(f"Error occurred while interacting with Redis: {e}")

        return utils.HttpResponseFormatter(response_code=200,
                                           message="Loan Request added successfully",
                                           data=loan_data)
    except Exception as e:
        traceback.print_exc()
        print(f"Error occurred due to: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred due to: {e}")

def get_loan_status(req, redis_client, db):
    user_record_from_token = req.state.user
    print("user_record_from_token", user_record_from_token)
    user_id = user_record_from_token.id

    if user_record_from_token.is_admin:
        all_loans = db.query(mdl.LoansModel, mdl.UsersModel.name, mdl.UsersModel.email).join(mdl.UsersModel, mdl.UsersModel.id == mdl.LoansModel.user_id).all()
        loan_data = []
        for loan in all_loans:
            loan_data.append(
                {
                    "user_id": loan.LoansModel.user_id,
                    "user_name": loan.name,
                    "user_email": loan.email,   
                    "loan_id": loan.LoansModel.id,
                    "loan_amount": loan.LoansModel.loan_amount,
                    "interest_rate": loan.LoansModel.interest_rate,
                    "start_date": loan.LoansModel.start_date.strftime("%Y-%m-%d"),
                    "end_date": loan.LoansModel.end_date.strftime("%Y-%m-%d"),
                    "loan_status": loan.LoansModel.loan_status,
                }
            )
        return {
            "data": loan_data,
            "source": "db"
        }

    redis_key = f"loan_data:{user_id}"
    try:
        cached_loan_data = redis_client.get(redis_key)

        if cached_loan_data:
            loan_data = json.loads(cached_loan_data)
            return {
                "data": loan_data,
                "source": "redis"
            }

    except redis.exceptions.RedisError as e:
        print(f"Error occurred while interacting with Redis: {e}")

    all_loans = db.query(mdl.LoansModel).filter(mdl.LoansModel.user_id == user_id).all()
    if not all_loans:
        raise HTTPException(status_code=404, detail="Loan not found")

    loan_data = []
    for loan in all_loans:
        loan_data.append({
        "user_id": loan.user_id,
        "user_name": user_record_from_token.name,
        "user_email": user_record_from_token.email,  
        "loan_id": loan.id,
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "start_date": loan.start_date.strftime("%Y-%m-%d"),
        "end_date": loan.end_date.strftime("%Y-%m-%d"),
        "loan_status": loan.loan_status,
    })

    try:
        redis_client.set(redis_key, json.dumps(loan_data), ex=600)
    except redis.exceptions.RedisError as e:
        print(f"Error occurred while interacting with Redis: {e}")

    return {
        "data": loan_data,
        "source": "db"
    }

def update_loan_status(req, loan_id , update_body, db:Session):
    try:
        user_record_from_token = req.state.user
        if not user_record_from_token and not user_record_from_token.is_admin:
            return utils.HttpResponseFormatter(response_code=400, message="User didn't have admin rights")

        update_status = update( mdl.LoansModel).where(mdl.LoansModel.id == loan_id).values(loan_status =  update_body.loan_status)
        db.execute(update_status)
        db.commit()
        return utils.HttpResponseFormatter(response_code=200,
                                           message="Loan Status updated sucessfully",
                                           data={
                                                "data":  update_body.loan_status
                                                })
    except Exception as e:
        traceback.print_exc()
        print(f"Error occured due to : {e}")
        return f"Error occured due to:{e}"
