from datetime import datetime
from datetime import date as date_type
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Position(Base):
    __tablename__ = "positions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    base_salary: Mapped[float] = mapped_column(Float, nullable=False)


class ManualExpense(Base):
    __tablename__ = "manual_expenses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    responsible: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EmployeePaymentStatus(Base):
    __tablename__ = "employee_payment_status"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    position_name: Mapped[str] = mapped_column(String(100), nullable=True)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    last_payment: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaymentCycleConfig(Base):
    __tablename__ = "payment_cycle_config"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reset_day: Mapped[int] = mapped_column(Integer, nullable=False, default=10)  # Dia do mês para reset
    last_reset_date: Mapped[date_type] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Expense(Base):
    __tablename__ = "expenses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    expense_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    expense_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'manual' ou 'employee_payment'
    reference_id: Mapped[int] = mapped_column(Integer, nullable=True)  # ID da tabela de origem
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
