import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import load_local_env
from app.database import init_db, seed_initial_positions
from app.messaging import init_rabbitmq, close_rabbitmq, RABBITMQ_ENABLED
from app.consumers import start_consumers
from app.routes import positions, expenses, payments
from app.services.payment_cycle import PaymentCycleService
from app.services.expense_service import ExpenseService

# Carregar variáveis de ambiente para desenvolvimento local
load_local_env()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await seed_initial_positions()
    await init_rabbitmq()
    
    # Verificar e executar reset automático de pagamentos se necessário
    try:
        from app.database import async_session_maker
        async with async_session_maker() as db:
            # Primeiro verificar se precisa de reset automático
            reset_count = await PaymentCycleService.check_and_auto_reset(db)
            if reset_count is not None:
                print(f"🔄 Automatic payment cycle reset executed: {reset_count} employees affected")
            else:
                print("✅ Payment cycle check completed - no reset needed")
            
            # Depois verificar se há funcionários para demo
            demo_payments = await PaymentCycleService.initialize_demo_payments(db)
            if demo_payments > 0:
                print(f"🎯 Demo initialization: {demo_payments} employees marked as paid for demonstration")
            else:
                print("ℹ️  No employees available for demo payment initialization")
            
            # Inicializar dados demo da tabela expenses
            demo_expenses = await ExpenseService.seed_demo_expenses(db)
            if demo_expenses > 0:
                print(f"💰 Demo expenses created: {demo_expenses} expense records added")
                
    except Exception as e:
        print(f"⚠️  Error during startup initialization: {e}")
    
    # Start RabbitMQ consumers in background only if RabbitMQ is enabled
    consumer_task = None
    if RABBITMQ_ENABLED:
        try:
            consumer_task = asyncio.create_task(start_consumers())
        except Exception as e:
            print(f"Failed to start consumers: {e}")
    
    yield
    
    # Shutdown
    if consumer_task and not consumer_task.done():
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
    await close_rabbitmq()


app = FastAPI(
    title="Finance Service",
    description="Microserviço para gerenciar cargos, salários e gastos",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(positions.router, prefix="/positions", tags=["positions"])
app.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
