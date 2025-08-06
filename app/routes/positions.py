from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db_session
from app.models import Position
from app.schemas import Position as PositionSchema, PositionCreate, PositionUpdate

router = APIRouter()


@router.get("/", response_model=List[PositionSchema])
async def get_positions(db: AsyncSession = Depends(get_db_session)):
    """Lista todos os cargos"""
    result = await db.execute(select(Position))
    positions = result.scalars().all()
    return positions


@router.post("/", response_model=PositionSchema, status_code=status.HTTP_201_CREATED)
async def create_position(
    position_data: PositionCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Cria um novo cargo"""
    # Check if position name already exists
    result = await db.execute(select(Position).where(Position.name == position_data.name))
    existing_position = result.scalar_one_or_none()
    
    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position with this name already exists"
        )
    
    new_position = Position(**position_data.model_dump())
    db.add(new_position)
    await db.commit()
    await db.refresh(new_position)
    
    return new_position


@router.put("/{position_id}", response_model=PositionSchema)
async def update_position(
    position_id: int,
    position_data: PositionUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Atualiza um cargo existente"""
    result = await db.execute(select(Position).where(Position.id == position_id))
    position = result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    
    # Check if new name conflicts with existing position (if name is being changed)
    if position_data.name != position.name:
        result = await db.execute(select(Position).where(Position.name == position_data.name))
        existing_position = result.scalar_one_or_none()
        
        if existing_position:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Position with this name already exists"
            )
    
    # Update position fields
    for field, value in position_data.model_dump().items():
        setattr(position, field, value)
    
    await db.commit()
    await db.refresh(position)
    
    return position


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Remove um cargo"""
    result = await db.execute(select(Position).where(Position.id == position_id))
    position = result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    
    await db.delete(position)
    await db.commit()
