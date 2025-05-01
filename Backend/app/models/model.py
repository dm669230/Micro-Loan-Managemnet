from sqlalchemy import Integer, Float, Column, String, PrimaryKeyConstraint, Text, TIMESTAMP, Boolean, func, ForeignKey, Date
from app.db.base import Base as BASE
# from app.databases.query_mixin import QueryMixin


class UsersModel(BASE):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255))  
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_admin = Column(Boolean, default=False)
    salt = Column(String, nullable=False)

class LoansModel(BASE):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(UsersModel.id), index=True, nullable=False)

    loan_amount = Column(Float, nullable=False, index=True)
    loan_status = Column(String(100), nullable=False, index=True, default="Pending")
    interest_rate = Column(Float, nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, index=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=None, onupdate=func.now())
  # Auto-update on row updates
    


