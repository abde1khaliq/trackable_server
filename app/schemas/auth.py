from pydantic import BaseModel, EmailStr

class RegistrationForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class LoginForm(BaseModel):
    email: EmailStr
    password: str

    