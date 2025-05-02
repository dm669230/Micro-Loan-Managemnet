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

# Load environment variables from the .env file
load_dotenv(override=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# def register_new_loan(req, redis_client, new_loan_schema:LM_schema.NewLoanRegisterSchema, db):
#     try:
#         user_id = req.state.user.id
#         new_loan = mdl.LoansModel(user_id=user_id,
#                             loan_amount=new_loan_schema.loan_amount,
#                             loan_status = new_loan_schema.loan_status,
#                             interest_rate = new_loan_schema.interest_rate,
#                             start_date = new_loan_schema.start_date,
#                             end_date = new_loan_schema.end_date,
#                             )

#         db.add(new_loan)
#         db.commit()

#         return utils.HttpResponseFormatter(response_code=200,
#                                            message="Loan added sucessfully",
#                                            data={
#                                                 "status": "Added new Loan"
#                                                 }
#                                     )
#     except Exception as e:
#         traceback.print_exc()
#         print(f"Error occured due to : {e}")
#         return f"Error occured due to : {e}"

# def get_current_user(req, token: str = Depends(oauth2_scheme), db =None):
#     try:
#         token = req.headers.get("Authorization").split(" ")[1]
#         if not token:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authentication")
#         payload = jwt.decode(token, setting.SECRET_KEY, algorithms=["HS256"])

#         #for Testing Purpose assign hard code token
#         # payload = jwt.decode ( "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidmliaHUiLCJ1c2VybmFtZSI6ImRtNjY5MjMwQGdtYWlsLmNvbSIsInVzZXJfaWQiOjEsImlzX2FkbWluIjpmYWxzZSwiZXhwIjoxNzQ2MTAyNTMwfQ.wauN4x5S4Gzo-8-narcR6U3YJlDmx7K8v0zk2pjkccE", setting.SECRET_KEY,  algorithms=["HS256"])

#         print("payload :", payload)
#         user_id = payload.get("user_id")
#         print("apni_user_id :", user_id)
#         user = db.query(mdl.UsersModel).filter(mdl.UsersModel.id == user_id).first()
#         if not user:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authentication")
#         return user
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authentication")

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
        
        # Retrieve the latest loan for the user from the DB
        latest_loans = db.query(mdl.LoansModel).filter(mdl.LoansModel.user_id == user_id).order_by(desc(mdl.LoansModel.created_at)).all()

        # Prepare the loan data to store in Redis
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
        
        # Attempt to store the loan data in Redis (with error handling)
        try:
            redis_key = f"loan_data:{user_id}"
            redis_client.set(redis_key, json.dumps(loan_data), ex=600)  # optional TTL
        except redis.exceptions.RedisError as e:
            print(f"Error occurred while interacting with Redis: {e}")
            # Optionally, log this or handle the error differently

        # Returning the loan data as a response
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
                    "start_date": loan.LoansModel.start_date,
                    "end_date": loan.LoansModel.end_date,
                    "loan_status": loan.LoansModel.loan_status,
                }
            )
        return {
            "data": loan_data,
            "source": "db"
        }

    redis_key = f"loan_data:{user_id}"
    try:
        # Check if the loan data exists in Redis
        cached_loan_data = redis_client.get(redis_key)

        if cached_loan_data:
            # Deserialize the JSON data from Redis
            loan_data = json.loads(cached_loan_data)
            return {
                "data": loan_data,
                "source": "redis"
            }

    except redis.exceptions.RedisError as e:
        print(f"Error occurred while interacting with Redis: {e}")
        # Optionally, log this or handle the error differently

    # Fallback to DB if not found in Redis
    all_loans = db.query(mdl.LoansModel).filter(mdl.LoansModel.user_id == user_id).all()
    if not all_loans:
        raise HTTPException(status_code=404, detail="Loan not found")

    # Prepare loan data to store in Redis
    loan_data = []
    for loan in all_loans:
        loan_data.append({
        "user_id": loan.user_id,
        "user_name": user_record_from_token.name,
        "user_email": user_record_from_token.email,  
        "loan_id": loan.id,
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "start_date": loan.start_date,
        "end_date": loan.end_date,
        "loan_status": loan.loan_status,
    })

    # Attempt to cache the loan data for future use
    try:
        redis_client.set(redis_key, json.dumps(loan_data), ex=600)
    except redis.exceptions.RedisError as e:
        print(f"Error occurred while interacting with Redis: {e}")
        # Optionally, log this or handle the error differently

    # Returning the loan data from DB
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
        return f"Error occured due to : {e}"
