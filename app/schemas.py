from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


# Position schemas
class PositionBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    base_salary: float = Field(..., ge=0)


class PositionCreate(PositionBase):
    pass


class PositionUpdate(PositionBase):
    pass


class Position(PositionBase):
    id: int
    
    class Config:
        from_attributes = True


# Manual Expense schemas
class ManualExpenseBase(BaseModel):
    date: date
    category: str = Field(..., max_length=100)
    description: Optional[str] = None
    value: float = Field(..., gt=0)
    responsible: str = Field(..., max_length=100)


class ManualExpenseCreate(ManualExpenseBase):
    pass


class ManualExpense(ManualExpenseBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Employee Payment Status schemas
class EmployeePaymentStatusBase(BaseModel):
    employee_id: str = Field(..., max_length=50)
    position_name: Optional[str] = Field(None, max_length=100)
    paid: bool = False
    last_payment: Optional[datetime] = None


class EmployeePaymentStatus(EmployeePaymentStatusBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Payment confirmation schema
class PaymentConfirmation(BaseModel):
    employee_id: str


# Employee events schemas (for RabbitMQ)
class EmployeeRegistered(BaseModel):
    id: str
    name: str
    cpf: str
    email: str
    phone: str
    birthDate: list  # [year, month, day]
    hireDate: list  # [year, month, day]
    role: str
    roleDescription: Optional[str] = None
    profile_url: Optional[str] = None
    profileUrl: Optional[str] = None
    registrationDate: list  # [year, month, day, hour, minute, second, microsecond]
    active: bool
    terminationDate: Optional[list] = None  # [year, month, day] or null


class EmployeeDeleted(BaseModel):
    id: str


class EmployeeRoleChanged(BaseModel):
    id: str
    name: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthDate: Optional[list] = None
    hireDate: Optional[list] = None
    role: str
    roleDescription: Optional[str] = None
    profile_url: Optional[str] = None
    profileUrl: Optional[str] = None
    registrationDate: Optional[list] = None
    active: Optional[bool] = None
    terminationDate: Optional[list] = None


class EmployeeStatusChanged(BaseModel):
    id: str
    active: bool


# Payment Cycle Configuration schemas
class PaymentCycleConfigBase(BaseModel):
    reset_day: int = Field(..., ge=1, le=31, description="Dia do mês para resetar status de pagamento")


class PaymentCycleConfigCreate(PaymentCycleConfigBase):
    pass


class PaymentCycleConfigUpdate(PaymentCycleConfigBase):
    pass


class PaymentCycleConfig(PaymentCycleConfigBase):
    id: int
    last_reset_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentCycleReset(BaseModel):
    """Schema para response do reset manual"""
    message: str
    reset_date: date
    employees_reset: int


# Expense schemas (tabela unificada)
class ExpenseBase(BaseModel):
    description: str = Field(..., max_length=255)
    amount: float = Field(..., gt=0)
    expense_date: date
    expense_type: str = Field(..., max_length=50)  # 'manual' ou 'employee_payment'
    reference_id: Optional[int] = None


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
