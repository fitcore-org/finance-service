from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db_session
from app.models import EmployeePaymentStatus, Position, PaymentCycleConfig
from app.schemas import (
    EmployeePaymentStatus as EmployeePaymentStatusSchema,
    PaymentConfirmation,
    PaymentCycleConfig as PaymentCycleConfigSchema,
    PaymentCycleConfigCreate,
    PaymentCycleConfigUpdate,
    PaymentCycleReset
)
from app.messaging import publish_message
from app.services.payment_cycle import PaymentCycleService

router = APIRouter()


@router.get("/status", response_model=List[EmployeePaymentStatusSchema])
async def get_payment_status(
    db: AsyncSession = Depends(get_db_session)
):
    """Status de pagamento de todos os funcionários"""
    result = await db.execute(select(EmployeePaymentStatus))
    payment_statuses = result.scalars().all()
    return payment_statuses


@router.patch("/{employee_id}/pay", response_model=EmployeePaymentStatusSchema)
async def confirm_payment(
    employee_id: str,
    payment_data: PaymentConfirmation,
    db: AsyncSession = Depends(get_db_session)
):
    """Confirma pagamento de funcionário"""
    # Validate that employee_id matches
    if payment_data.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID mismatch"
        )
    
    # Find employee payment status
    result = await db.execute(
        select(EmployeePaymentStatus).where(
            EmployeePaymentStatus.employee_id == employee_id
        )
    )
    payment_status = result.scalar_one_or_none()
    
    if not payment_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee payment status not found"
        )
    
    # Get salary amount based on position
    salary_amount = 0.0
    position_log = "Position not found"
    
    if payment_status.position_name:
        # Look up the position to get the salary
        position_result = await db.execute(
            select(Position).where(Position.name == payment_status.position_name)
        )
        position = position_result.scalar_one_or_none()
        
        if position:
            salary_amount = position.base_salary
            position_log = f"Position '{payment_status.position_name}' found with salary: {salary_amount}"
        else:
            position_log = f"Position '{payment_status.position_name}' not found in positions table, using default amount: 0.0"
    else:
        position_log = "Employee has no position assigned, using default amount: 0.0"
    
    print(f"Payment calculation for employee {employee_id}: {position_log}")

    # Update payment status
    payment_status.paid = True
    payment_status.last_payment = datetime.utcnow()
    payment_status.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(payment_status)
    
    # Publish employee paid event
    current_date = datetime.utcnow()
    await publish_message(
        "employee-paid-queue",
        {
            "id": employee_id,
            "amount": salary_amount,
            "position": payment_status.position_name,
            "month": current_date.month,
            "year": current_date.year,
            "paid_at": payment_status.last_payment.isoformat()
        }
    )

    await publish_message(
        "analytics-employee-status-changed-queue",
        {
            "id": employee_id,
            "active": True
        }
    )

    await publish_message(
        "user-employee-status-changed-queue",
        {
            "id": employee_id,
            "active": True
        }
    )
    
    return payment_status


@router.post("/{employee_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Endpoint para demitir funcionário"""
    # Check if employee exists
    result = await db.execute(
        select(EmployeePaymentStatus).where(
            EmployeePaymentStatus.employee_id == employee_id
        )
    )
    payment_status = result.scalar_one_or_none()
    
    if not payment_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Update payment status to mark as dismissed (reset payment status)
    payment_status.paid = False
    payment_status.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(payment_status)
    
    # Publish employee status change event (deactivation)
    await publish_message(
        "analytics-employee-status-changed-queue",
        {
            "id": employee_id,
            "active": False
        }
    )

    await publish_message(
        "user-employee-status-changed-queue",
        {
            "id": employee_id,
            "active": False
        }
    )
    
    # Also publish to employee-dismissed-queue for other services
    await publish_message(
        "employee-dismissed-queue",
        {
            "id": employee_id,
            "dismissed_at": datetime.utcnow().isoformat(),
            "position": payment_status.position_name
        }
    )


# =============================================================================
# PAYMENT CYCLE MANAGEMENT ROUTES
# =============================================================================

@router.get("/cycle/config", response_model=PaymentCycleConfigSchema)
async def get_payment_cycle_config(
    db: AsyncSession = Depends(get_db_session)
):
    """Obtém a configuração atual do ciclo de pagamentos"""
    config = await PaymentCycleService.get_or_create_config(db)
    return config


@router.put("/cycle/config", response_model=PaymentCycleConfigSchema)
async def update_payment_cycle_config(
    config_data: PaymentCycleConfigUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Atualiza a configuração do ciclo de pagamentos"""
    # Validar dia do mês
    if config_data.reset_day < 1 or config_data.reset_day > 31:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset day must be between 1 and 31"
        )
    
    config = await PaymentCycleService.update_config(db, config_data.reset_day)
    return config


@router.get("/cycle/next-reset")
async def get_next_reset_date(
    db: AsyncSession = Depends(get_db_session)
):
    """Obtém a próxima data de reset dos pagamentos"""
    next_reset = await PaymentCycleService.get_next_reset_date(db)
    config = await PaymentCycleService.get_or_create_config(db)
    
    return {
        "next_reset_date": next_reset.isoformat(),
        "reset_day": config.reset_day,
        "last_reset_date": config.last_reset_date.isoformat() if config.last_reset_date else None
    }


@router.post("/cycle/reset", response_model=PaymentCycleReset)
async def manual_reset_payment_cycle(
    db: AsyncSession = Depends(get_db_session)
):
    """Reset manual de todos os status de pagamento"""
    employees_reset = await PaymentCycleService.reset_all_payment_status(db)
    
    return PaymentCycleReset(
        message=f"Payment cycle reset completed successfully",
        reset_date=date.today(),
        employees_reset=employees_reset
    )


@router.post("/cycle/check-auto-reset")
async def check_auto_reset(
    db: AsyncSession = Depends(get_db_session)
):
    """Verifica e executa reset automático se necessário"""
    employees_reset = await PaymentCycleService.check_and_auto_reset(db)
    
    if employees_reset is not None:
        return {
            "reset_executed": True,
            "employees_reset": employees_reset,
            "reset_date": date.today().isoformat(),
            "message": "Automatic reset executed successfully"
        }
    else:
        config = await PaymentCycleService.get_or_create_config(db)
        next_reset = await PaymentCycleService.get_next_reset_date(db)
        
        return {
            "reset_executed": False,
            "message": "No reset needed at this time",
            "next_reset_date": next_reset.isoformat(),
            "reset_day": config.reset_day
        }
