from pydantic import BaseModel, EmailStr

class RegistrationForm(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str

class LoginForm(BaseModel):
    email: EmailStr
    password: str

    