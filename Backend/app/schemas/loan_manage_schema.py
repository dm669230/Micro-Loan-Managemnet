from pydantic import BaseModel
from typing import Optional, List, Dict, Union

class NewLoanRegisterSchema(BaseModel):
    # user_id: Optional[int] = None
    loan_amount: Optional[float] = None
    start_date: Optional[str] = "YYYY-MM-DD"
    end_date: Optional[str] = "YYYY-MM-DD"

class NewLoanApplySchema(BaseModel):
    loan_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    start_date: Optional[str] = "YYYY-MM-DD"
    end_date: Optional[str] = "YYYY-MM-DD"

class UpdateLoanStatusSchema(BaseModel):
    loan_status: Optional[str] = "Pending"


