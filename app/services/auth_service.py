from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models import User
from app.core.security import hash_password, verify_password
from app.core.jwt import jwt_handler
from app.schemas.auth import RegistrationForm, LoginForm

class AuthService:
    @staticmethod
    async def register_user(form: RegistrationForm, db: AsyncSession):
        # Check if user already exists
        user_exists = await db.execute(select(User).where(User.email == form.email))
        if user_exists.scalars().first():
            raise HTTPException(status_code=400, detail="User already exists")

        # Create new user
        user = User(
            first_name=form.first_name,
            last_name=form.last_name,
            username=form.username,
            email=form.email,
            password=hash_password(form.password)
        )

        db.add(user)
        await db.commit()
        return {"message": "User registered successfully"}

    @staticmethod
    async def login_user(form: LoginForm, db: AsyncSession):
        # Find user by email
        result = await db.execute(select(User).where(User.email == form.email))
        user = result.scalars().first()

        if not user or not verify_password(form.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Generate JWT
        access_token = jwt_handler.create_access_token(
            data={"user_id": user.id, "email": user.email}
        )
        return {"message": "Login successful", "access_token": access_token}
