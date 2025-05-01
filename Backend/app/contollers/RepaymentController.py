# from app.config.db import  get_db
from sqlalchemy.orm import Session
import bcrypt
import base64, hashlib
from app.schemas import repayment_schema as Reapay_schema
from app.models import model as mdl
from app.utils import utils
from fastapi import Depends
import traceback
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(override=True)

def add_new_repayment(new_repay_schema:Reapay_schema.NewRepayRegisterSchema, db):
    try:
        
        new_repayment = mdl.RepaymentsModel(
                                        loan_id=new_repay_schema.loan_id,
                                        user_id=new_repay_schema.user_id, 
                                        repayment_date = new_repay_schema.repayment_date,
                                        repayment_amount = new_repay_schema.repayment_amount,
                                        remaining_amount = new_repay_schema.remaining_amount,
                            )
        
        db.add(new_repayment)
        db.commit()

        return utils.HttpResponseFormatter(data= "Repayment Added Sucessfully")
    except Exception as e:
        traceback.print_exc()
        print(f"Error occured due to : {e}")
        return utils.HttpResponseFormatter(data= e, response_code=400)
    
def add_repayment(repay_schema:Reapay_schema.NewRepayAddSchema, db):
    try:
        
        new_repayment = mdl.RepaymentsModel(
                                        loan_id=repay_schema.loan_id,
                                        user_id=repay_schema.user_id,
                                        repayment_date = repay_schema.repayment_date,
                                        repayment_amount = repay_schema.repayment_amount,
                                        remaining_amount = repay_schema.remaining_amount,
                            )
        
        db.add(new_repayment)
        db.commit()

        return utils.HttpResponseFormatter(data= "Repayment Added Sucessfully")
    except Exception as e:
        traceback.print_exc()
        print(f"Error occured due to : {e}")
        return utils.HttpResponseFormatter(data= e, response_code=400)

    