from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db_session
from app.models import ManualExpense, Expense
from app.schemas import (
    ManualExpense as ManualExpenseSchema, 
    ManualExpenseCreate,
    Expense as ExpenseSchema
)
from app.messaging import publish_message
from app.services.expense_service import ExpenseService

router = APIRouter()


@router.get("/manual", response_model=List[ManualExpenseSchema])
async def get_manual_expenses(db: AsyncSession = Depends(get_db_session)):
    """Lista gastos manuais"""
    result = await db.execute(select(ManualExpense).order_by(ManualExpense.date.desc()))
    expenses = result.scalars().all()
    return expenses


@router.post("/manual", response_model=ManualExpenseSchema, status_code=status.HTTP_201_CREATED)
async def create_manual_expense(
    expense_data: ManualExpenseCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Registra gasto manual"""
    new_expense = ManualExpense(**expense_data.model_dump())
    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)
    
    # Criar entrada na tabela unificada de expenses
    await ExpenseService.create_manual_expense_entry(db, new_expense)
    
    # Publish expense registered event
    await publish_message(
        "finance.expense.registered",
        {
            "type": "expense.registered",
            "payload": {
                "amount": new_expense.value,
                "category": new_expense.category,
                "description": new_expense.description,
                "date": new_expense.date.isoformat(),
                "responsible": new_expense.responsible
            }
        }
    )
    
    return new_expense


@router.delete("/manual/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manual_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Remove um gasto manual"""
    result = await db.execute(select(ManualExpense).where(ManualExpense.id == expense_id))
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manual expense not found"
        )
    
    # Remover entrada correspondente na tabela expenses
    await ExpenseService.delete_expense_by_reference(db, "manual", expense_id)
    
    await db.delete(expense)
    await db.commit()
    
    # Publish deletion event if messaging is enabled
    await publish_message(
        "finance.expense.deleted",
        {
            "type": "expense.deleted",
            "payload": {
                "id": expense_id,
                "deleted_at": datetime.utcnow().isoformat()
            }
        }
    )


# =============================================================================
# UNIFIED EXPENSES ROUTES
# =============================================================================

@router.get("/", response_model=List[ExpenseSchema])
async def get_all_expenses(
    limit: int = Query(50, description="Limite de registros"),
    offset: int = Query(0, description="Offset para paginação"),
    db: AsyncSession = Depends(get_db_session)
):
    """Lista todas as despesas unificadas (manuais + pagamentos de funcionários)"""
    expenses = await ExpenseService.get_all_expenses(db, limit=limit, offset=offset)
    return expenses
