import json
import asyncio
from datetime import datetime
from sqlalchemy import select, delete
from aio_pika.abc import AbstractIncomingMessage
from app.database import async_session_maker
from app.models import EmployeePaymentStatus
from app.messaging import get_queue, publish_message
from app.schemas import EmployeeRegistered, EmployeeDeleted, EmployeeRoleChanged


async def process_employee_registered(message: AbstractIncomingMessage):
    """Process new employee registration"""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            
            # Map employeeId to id if needed for schema compatibility
            if 'employeeId' in data and 'id' not in data:
                data['id'] = data['employeeId']
            
            employee_data = EmployeeRegistered(**data)
            
            async with async_session_maker() as session:
                # Check if employee already exists
                result = await session.execute(
                    select(EmployeePaymentStatus).where(
                        EmployeePaymentStatus.employee_id == employee_data.id
                    )
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    # Create new employee payment status
                    new_status = EmployeePaymentStatus(
                        employee_id=employee_data.id,
                        position_name=employee_data.role,
                        paid=False,
                        last_payment=None
                    )
                    session.add(new_status)
                    await session.commit()
                    print(f"Created payment status for employee {employee_data.id}")
                else:
                    print(f"Employee {employee_data.id} already exists")
                    
        except Exception as e:
            print(f"Error processing employee registration: {e}")


async def process_employee_deleted(message: AbstractIncomingMessage):
    """Process employee deletion"""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            
            # Map employeeId to id if needed for schema compatibility
            if 'employeeId' in data and 'id' not in data:
                data['id'] = data['employeeId']
            
            employee_data = EmployeeDeleted(**data)
            
            async with async_session_maker() as session:
                # Delete employee payment status
                await session.execute(
                    delete(EmployeePaymentStatus).where(
                        EmployeePaymentStatus.employee_id == employee_data.id
                    )
                )
                await session.commit()
                print(f"Deleted payment status for employee {employee_data.id}")
                
        except Exception as e:
            print(f"Error processing employee deletion: {e}")


async def process_employee_role_changed(message: AbstractIncomingMessage):
    """Process employee role change"""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            
            # Map employeeId to id if needed for schema compatibility
            if 'employeeId' in data and 'id' not in data:
                data['id'] = data['employeeId']
            
            employee_data = EmployeeRoleChanged(**data)
            
            async with async_session_maker() as session:
                # Update employee position name
                result = await session.execute(
                    select(EmployeePaymentStatus).where(
                        EmployeePaymentStatus.employee_id == employee_data.id
                    )
                )
                employee_status = result.scalar_one_or_none()
                
                if employee_status:
                    employee_status.position_name = employee_data.role
                    employee_status.updated_at = datetime.utcnow()
                    await session.commit()
                    print(f"Updated role for employee {employee_data.id} to {employee_data.role}")
                else:
                    print(f"Employee {employee_data.id} not found for role update")
                
        except Exception as e:
            print(f"Error processing employee role change: {e}")


async def start_consumers():
    """Start all RabbitMQ consumers"""
    try:
        # Get queues - usando a fila específica do finance-service para consumir da exchange
        employee_registered_queue = await get_queue("fincance-cadastro-funcionario-queue")
        employee_deleted_queue = await get_queue("fincance-employee-deleted-queue")
        employee_role_changed_queue = await get_queue("employee-role-changed-queue")
        
        # Check if all queues were created successfully
        if (employee_registered_queue is None or 
            employee_deleted_queue is None or 
            employee_role_changed_queue is None):
            print("Failed to create one or more queues")
            return
        
        # Start consuming (now we know all queues are not None)
        await employee_registered_queue.consume(process_employee_registered)
        await employee_deleted_queue.consume(process_employee_deleted)
        await employee_role_changed_queue.consume(process_employee_role_changed)
        
        print("RabbitMQ consumers started")
        
        # Keep consumers running
        await asyncio.Future()  # Run forever
        
    except Exception as e:
        print(f"Error starting consumers: {e}")
        raise
