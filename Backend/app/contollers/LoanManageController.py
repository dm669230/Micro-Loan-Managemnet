# from app.config.db import  get_db
from sqlalchemy.orm import Session
import bcrypt
import base64, hashlib
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

def register_new_loan(req, new_loan_schema:LM_schema.NewLoanRegisterSchema, db):
    try:
        user_id = req.state.user.id
        new_loan = mdl.LoansModel(user_id=user_id,
                            loan_amount=new_loan_schema.loan_amount, 
                            loan_status = new_loan_schema.loan_status,
                            interest_rate = new_loan_schema.interest_rate,
                            start_date = new_loan_schema.start_date,
                            end_date = new_loan_schema.end_date,
                            )
        
        db.add(new_loan)
        db.commit()
        redis_key = f"loan_status:{new_loan.id}"
        redis_client.set(redis_key, new_loan.loan_status, ex=600)  # optional TTL

        return utils.HttpResponseFormatter(response_code=200,
                                           message="Loan added sucessfully",
                                           data={
                                                "status": "Added new Loan"
                                                }
                                    )
    except Exception as e:
        traceback.print_exc()
        print(f"Error occured due to : {e}")
        return f"Error occured due to : {e}"
    
def get_current_user(req, token: str = Depends(oauth2_scheme), db =None):
    try:
        token = req.headers.get("Authorization").split(" ")[1]
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authentication")
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=["HS256"])

        #for Testing Purpose assign hard code token
        # payload = jwt.decode ( "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidmliaHUiLCJ1c2VybmFtZSI6ImRtNjY5MjMwQGdtYWlsLmNvbSIsInVzZXJfaWQiOjEsImlzX2FkbWluIjpmYWxzZSwiZXhwIjoxNzQ2MTAyNTMwfQ.wauN4x5S4Gzo-8-narcR6U3YJlDmx7K8v0zk2pjkccE", setting.SECRET_KEY,  algorithms=["HS256"])

        print("payload :", payload)
        user_id = payload.get("user_id")
        print("apni_user_id :", user_id)
        user = db.query(mdl.UsersModel).filter(mdl.UsersModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authentication")
        return user
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authentication")
    
def apply_new_loan(req, loan_apply_schema:LM_schema.NewLoanApplySchema, db:Session):
    try:
        user_record_from_token = get_current_user(req, db=db)
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
        
        latest_loan = (
                db.query(mdl.LoansModel)
                .filter(mdl.LoansModel.user_id == user_id)
                .order_by(desc(mdl.LoansModel.created_at))
                .first()
                        )

        return utils.HttpResponseFormatter(response_code=200,
                                           message="Loan Request added sucessfully",
                                           data={"loan_id": latest_loan.id,
                                                "status": f"Added new Loan Request from : {user_record_from_token.name}"
                                                })
    except Exception as e:
        traceback.print_exc()
        print(f"Error occured due to : {e}")
        return f"Error occured due to : {e}"

def all_loans(db:Session):
    try:
        user_record_from_token = get_current_user(db=db)
        user_id = user_record_from_token.id
        name = user_record_from_token.name
        # user_id = 3
        # name = "Vaibhav Srivastava"
        
        all_loan = (
                db.query(mdl.LoansModel)
                .filter(mdl.LoansModel.user_id == user_id)
                .all()
                        )

        return utils.HttpResponseFormatter(response_code=200,
                                           message="Loan Request added sucessfully",
                                           data={"data": all_loan,
                                                "status": f"Loans Associated with Mr. : {name}"
                                                })
    except Exception as e:
        traceback.print_exc()
        print(f"Error occured due to : {e}")
        return f"Error occured due to : {e}"
    

def update_loan_status(loan_id ,loan_status, db:Session):
    try:
        user_record_from_token = get_current_user(db=db)
        if not user_record_from_token.is_admin:
            return utils.HttpResponseFormatter(response_code=400,
                                           message="User didn't have admin rights")
        new_loan_status = loan_status.loan_status
        # user_id = 3
        # name = "Vaibhav Srivastava"
        
        update_status = update( mdl.LoansModel).where(mdl.LoansModel.id == loan_id).values(loan_status = new_loan_status)

        db.execute(update_status)
        db.commit()
        return utils.HttpResponseFormatter(response_code=200,
                                           message="Loan Status updated sucessfully",
                                           data={
                                                "data": new_loan_status
                                                })
    except Exception as e:
        traceback.print_exc()
        print(f"Error occured due to : {e}")
        return f"Error occured due to : {e}"

@app.get("/loan-status/{loan_id}")
def get_loan_status(loan_id: int, db: Session = Depends(get_db)):
    redis_key = f"loan_status:{loan_id}"

    # Try Redis cache first
    cached_status = redis_client.get(redis_key)
    if cached_status:
        return {"loan_id": loan_id, "status": cached_status, "source": "cache"}

    # Fallback to DB
    loan = db.query(mdl.LoansModel).filter_by(id=loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    # Cache it again for future
    redis_client.set(redis_key, loan.loan_status, ex=600)

    return {"loan_id": loan_id, "status": loan.loan_status, "source": "db"}