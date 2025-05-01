from pydantic import BaseModel
from typing import Optional, List, Dict, Union

class NewUserRegisterSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None