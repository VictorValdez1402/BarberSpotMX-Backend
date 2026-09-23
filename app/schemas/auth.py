from pydantic import BaseModel, EmailStr, model_validator
from app.models import RoleEnum


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str
    role: RoleEnum

    @model_validator(mode="after")
    def verify_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Las contraseñas no coinciden")
        if len(self.password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return self


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: RoleEnum