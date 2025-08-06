import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select


class Base(DeclarativeBase):
    pass


# Database configuration from environment variables (injected by docker-compose)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "fitcore")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "fitcorepass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "auth")
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

print(f"Using DATABASE_URL: {DATABASE_URL}")

# Create async engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_initial_positions():
    """Seed initial positions with base salaries"""
    from app.models import Position
    
    initial_positions = [
        {
            "name": "MANAGER",
            "description": "Gerente/Proprietário da academia",
            "base_salary": 0.0  # Manager não recebe salário, é o próprio dono
        },
        {
            "name": "PERSONAL_TRAINER",
            "description": "Personal Trainer especializado",
            "base_salary": 3500.0
        },
        {
            "name": "RECEPTIONIST",
            "description": "Recepcionista da academia",
            "base_salary": 1800.0
        },
        {
            "name": "CLEANER",
            "description": "Funcionário de limpeza",
            "base_salary": 1400.0
        }
    ]
    
    async with async_session_maker() as session:
        try:
            # Check if positions already exist
            for position_data in initial_positions:
                result = await session.execute(
                    select(Position).where(Position.name == position_data["name"])
                )
                existing_position = result.scalar_one_or_none()
                
                if not existing_position:
                    new_position = Position(**position_data)
                    session.add(new_position)
                    print(f"✅ Created initial position: {position_data['name']} - R$ {position_data['base_salary']}")
                else:
                    print(f"⚠️  Position already exists: {position_data['name']}")
            
            await session.commit()
            print("🎉 Initial positions seeded successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding initial positions: {e}")
        finally:
            await session.close()


async def get_db_session():
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
