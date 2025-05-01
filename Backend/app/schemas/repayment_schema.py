from pydantic import BaseModel
from typing import Optional, List, Dict, Union

class NewRepayRegisterSchema(BaseModel):
    loan_id: Optional[int] = None
    user_id: Optional[int] = None
    repayment_date: Optional[str] = None
    repayment_amount: Optional[float] = None
    remaining_amount: Optional[float] = None

class NewRepayAddSchema(BaseModel):
    loan_id: Optional[int] = None
    user_id: Optional[int] = None
    repayment_date: Optional[str] = None
    repayment_amount: Optional[float] = None
    remaining_amount: Optional[float] = None