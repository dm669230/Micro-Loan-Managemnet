from pydantic import BaseModel
from typing import Optional

class NewLoanApplySchema(BaseModel):
    loan_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    loan_status: Optional[str] = "Pending"

class UpdateLoanStatusSchema(BaseModel):
    loan_status: str
