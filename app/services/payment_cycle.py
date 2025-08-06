from datetime import date, datetime
from typing import Optional, List
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import PaymentCycleConfig, EmployeePaymentStatus, Position
from app.messaging import publish_message


class PaymentCycleService:
    """Serviço para gerenciar ciclos de pagamento mensal"""
    
    @staticmethod
    async def get_or_create_config(db: AsyncSession) -> PaymentCycleConfig:
        """Busca ou cria a configuração de ciclo de pagamento"""
        result = await db.execute(select(PaymentCycleConfig))
        config = result.scalar_one_or_none()
        
        if not config:
            # Criar configuração padrão
            config = PaymentCycleConfig(
                reset_day=10,  # Dia 10 como padrão
                last_reset_date=None
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)
            
        return config
    
    @staticmethod
    async def update_config(db: AsyncSession, reset_day: int) -> PaymentCycleConfig:
        """Atualiza a configuração do ciclo de pagamento"""
        config = await PaymentCycleService.get_or_create_config(db)
        config.reset_day = reset_day
        config.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(config)
        
        return config
    
    @staticmethod
    async def should_reset_payments(db: AsyncSession) -> bool:
        """Verifica se os pagamentos devem ser resetados"""
        config = await PaymentCycleService.get_or_create_config(db)
        today = date.today()
        
        # Se nunca foi resetado, e já passou do dia configurado neste mês
        if config.last_reset_date is None:
            if today.day >= config.reset_day:
                return True
            return False
        
        # Se o último reset foi em outro mês, e já passou do dia configurado
        if (config.last_reset_date.year != today.year or 
            config.last_reset_date.month != today.month):
            if today.day >= config.reset_day:
                return True
        
        return False
    
    @staticmethod
    async def reset_all_payment_status(db: AsyncSession) -> int:
        """Reset todos os status de pagamento para False"""
        # Contar quantos funcionários serão afetados
        count_result = await db.execute(
            select(EmployeePaymentStatus).where(EmployeePaymentStatus.paid == True)
        )
        employees_to_reset = count_result.scalars().all()
        count = len(employees_to_reset)
        
        # Reset dos status
        await db.execute(
            update(EmployeePaymentStatus)
            .where(EmployeePaymentStatus.paid == True)
            .values(paid=False, updated_at=datetime.utcnow())
        )
        
        # Atualizar a data do último reset
        config = await PaymentCycleService.get_or_create_config(db)
        config.last_reset_date = date.today()
        config.updated_at = datetime.utcnow()
        
        await db.commit()
        
        print(f"Payment cycle reset completed: {count} employees affected")
        
        return count
    
    @staticmethod
    async def get_next_reset_date(db: AsyncSession) -> date:
        """Calcula a próxima data de reset"""
        config = await PaymentCycleService.get_or_create_config(db)
        today = date.today()
        
        # Se ainda não passou do dia neste mês
        if today.day < config.reset_day:
            return date(today.year, today.month, config.reset_day)
        
        # Se já passou, será no próximo mês
        if today.month == 12:
            return date(today.year + 1, 1, config.reset_day)
        else:
            return date(today.year, today.month + 1, config.reset_day)
    
    @staticmethod
    async def check_and_auto_reset(db: AsyncSession) -> Optional[int]:
        """Verifica e executa reset automático se necessário"""
        if await PaymentCycleService.should_reset_payments(db):
            return await PaymentCycleService.reset_all_payment_status(db)
        return None
    
    @staticmethod
    async def initialize_demo_payments(db: AsyncSession) -> int:
        """Paga 50% dos funcionários para demonstração do sistema"""
        
        # Buscar todos os funcionários não pagos
        result = await db.execute(
            select(EmployeePaymentStatus).where(EmployeePaymentStatus.paid == False)
        )
        unpaid_employees = result.scalars().all()
        
        if not unpaid_employees:
            print("No unpaid employees found for demo initialization")
            return 0
        
        # Calcular 50% dos funcionários (pelo menos 1 se houver funcionários)
        total_employees = len(unpaid_employees)
        employees_to_pay = max(1, total_employees // 2)
        
        # Selecionar aleatoriamente 50% dos funcionários
        selected_employees = random.sample(unpaid_employees, employees_to_pay)
        
        paid_count = 0
        
        for employee in selected_employees:
            # Buscar salário baseado na posição
            salary_amount = 0.0
            position_log = "Position not found"
            
            if employee.position_name:
                position_result = await db.execute(
                    select(Position).where(Position.name == employee.position_name)
                )
                position = position_result.scalar_one_or_none()
                
                if position:
                    salary_amount = position.base_salary
                    position_log = f"Position '{employee.position_name}' found with salary: {salary_amount}"
                else:
                    position_log = f"Position '{employee.position_name}' not found, using default: 0.0"
            else:
                position_log = "No position assigned, using default: 0.0"
            
            # Atualizar status de pagamento
            employee.paid = True
            employee.last_payment = datetime.utcnow()
            employee.updated_at = datetime.utcnow()
            
            # Publicar evento de pagamento
            current_date = datetime.utcnow()
            await publish_message(
                "employee-paid-queue",
                {
                    "id": employee.employee_id,
                    "amount": salary_amount,
                    "position": employee.position_name,
                    "month": current_date.month,
                    "year": current_date.year,
                    "paid_at": employee.last_payment.isoformat()
                }
            )
            
            paid_count += 1
            print(f"Demo payment processed for employee {employee.employee_id}: {position_log}")
        
        await db.commit()
        
        print(f"Demo initialization completed: {paid_count}/{total_employees} employees paid (50%)")
        return paid_count
