from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models import Expense, ManualExpense, EmployeePaymentStatus, Position
from app.schemas import ExpenseCreate
import random


class ExpenseService:
    """Serviço para gerenciar a tabela unificada de expenses"""
    
    @staticmethod
    async def create_expense(db: AsyncSession, expense_data: ExpenseCreate) -> Expense:
        """Cria uma nova despesa na tabela expenses"""
        expense = Expense(**expense_data.model_dump())
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return expense
    
    @staticmethod
    async def create_manual_expense_entry(
        db: AsyncSession, 
        manual_expense: ManualExpense
    ) -> Expense:
        """Cria entrada na tabela expenses baseada em um gasto manual"""
        expense_data = ExpenseCreate(
            description=f"Gasto Manual - {manual_expense.category}" + (
                f": {manual_expense.description}" if manual_expense.description else ""
            ),
            amount=manual_expense.value,
            expense_date=manual_expense.date,
            expense_type="manual",
            reference_id=manual_expense.id
        )
        return await ExpenseService.create_expense(db, expense_data)
    
    @staticmethod
    async def create_employee_payment_entry(
        db: AsyncSession,
        employee_id: str,
        amount: float,
        position_name: Optional[str] = None,
        payment_date: Optional[date] = None
    ) -> Expense:
        """Cria entrada na tabela expenses baseada em pagamento de funcionário"""
        if payment_date is None:
            payment_date = date.today()
            
        # Buscar o ID do status de pagamento para usar como referência
        result = await db.execute(
            select(EmployeePaymentStatus).where(
                EmployeePaymentStatus.employee_id == employee_id
            )
        )
        payment_status = result.scalar_one_or_none()
        
        description = f"Pagamento Funcionário - {employee_id}"
        if position_name:
            description += f" ({position_name})"
            
        expense_data = ExpenseCreate(
            description=description,
            amount=amount,
            expense_date=payment_date,
            expense_type="employee_payment",
            reference_id=payment_status.id if payment_status else None
        )
        return await ExpenseService.create_expense(db, expense_data)
    
    @staticmethod
    async def get_all_expenses(
        db: AsyncSession,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Expense]:
        """Retorna todas as despesas com paginação opcional"""
        query = select(Expense).order_by(Expense.expense_date.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
            
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def delete_expense_by_reference(
        db: AsyncSession,
        expense_type: str,
        reference_id: int
    ) -> bool:
        """Remove uma despesa baseada no tipo e ID de referência"""
        result = await db.execute(
            select(Expense).where(
                Expense.expense_type == expense_type,
                Expense.reference_id == reference_id
            )
        )
        expense = result.scalar_one_or_none()
        
        if expense:
            await db.delete(expense)
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def seed_demo_expenses(db: AsyncSession) -> int:
        """
        Popula a tabela expenses com dados simulados de uma academia
        Retorna o número de registros criados
        """
        # Verificar se já existem dados
        result = await db.execute(select(Expense))
        existing_expenses = result.scalars().all()
        
        if len(existing_expenses) >= 10:
            print(f"✅ Expenses table already has {len(existing_expenses)} records - skipping demo data")
            return 0
        
        # Dados simulados para uma academia
        demo_expenses = [
            # Gastos com equipamentos
            {
                "description": "Compra de Halteres - Set Completo",
                "amount": 2500.00,
                "expense_date": date(2025, 8, 1),
                "expense_type": "equipment",
                "reference_id": None
            },
            {
                "description": "Manutenção Esteira Ergométrica",
                "amount": 350.00,
                "expense_date": date(2025, 8, 2),
                "expense_type": "maintenance",
                "reference_id": None
            },
            # Gastos operacionais
            {
                "description": "Conta de Energia Elétrica",
                "amount": 1200.50,
                "expense_date": date(2025, 8, 3),
                "expense_type": "utilities",
                "reference_id": None
            },
            {
                "description": "Produtos de Limpeza e Higiene",
                "amount": 180.00,
                "expense_date": date(2025, 8, 3),
                "expense_type": "cleaning",
                "reference_id": None
            },
            # Pagamentos de funcionários simulados
            {
                "description": "Pagamento Funcionário - Personal Trainer João",
                "amount": 3500.00,
                "expense_date": date(2025, 8, 1),
                "expense_type": "employee_payment",
                "reference_id": 1001
            },
            {
                "description": "Pagamento Funcionário - Recepcionista Maria",
                "amount": 2200.00,
                "expense_date": date(2025, 8, 1),
                "expense_type": "employee_payment", 
                "reference_id": 1002
            },
            {
                "description": "Pagamento Funcionário - Instrutor Carlos",
                "amount": 2800.00,
                "expense_date": date(2025, 8, 1),
                "expense_type": "employee_payment",
                "reference_id": 1003
            },
            # Gastos com suplementos/loja
            {
                "description": "Estoque Suplementos - Whey Protein",
                "amount": 1500.00,
                "expense_date": date(2025, 8, 4),
                "expense_type": "inventory",
                "reference_id": None
            },
            {
                "description": "Marketing Digital - Redes Sociais",
                "amount": 800.00,
                "expense_date": date(2025, 8, 5),
                "expense_type": "marketing",
                "reference_id": None
            },
            # Gastos diversos
            {
                "description": "Toalhas e Uniformes - Reposição",
                "amount": 450.00,
                "expense_date": date(2025, 8, 5),
                "expense_type": "supplies",
                "reference_id": None
            },
            {
                "description": "Sistema de Som - Upgrade",
                "amount": 1200.00,
                "expense_date": date(2025, 8, 6),
                "expense_type": "equipment",
                "reference_id": None
            },
            {
                "description": "Água Mineral - Estoque Mensal", 
                "amount": 320.00,
                "expense_date": date(2025, 8, 6),
                "expense_type": "supplies",
                "reference_id": None
            }
        ]
        
        created_count = 0
        for expense_data in demo_expenses:
            expense = Expense(**expense_data)
            db.add(expense)
            created_count += 1
        
        await db.commit()
        print(f"🎯 Created {created_count} demo expense records for the gym")
        return created_count
