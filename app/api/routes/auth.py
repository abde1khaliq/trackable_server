from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.auth import RegistrationForm, LoginForm
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register_user(form: RegistrationForm, db: AsyncSession = Depends(get_db)):
    return await AuthService.register_user(form, db)

@router.post("/login")
async def login_user(form: LoginForm, db: AsyncSession = Depends(get_db)):
    return await AuthService.login_user(form, db)
