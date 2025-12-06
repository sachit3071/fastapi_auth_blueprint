from pydantic import BaseModel, Field, EmailStr


# Pydantic models for validation
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)


class SigninRequest(BaseModel):
    email: EmailStr
    password: str
