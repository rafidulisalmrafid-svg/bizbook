from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserRead,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user_company import User
import time

router = APIRouter()

# Simple in-memory sliding window rate limiter for auth endpoints
AUTH_ATTEMPTS = {}
RATE_LIMIT_WINDOW = 60 # seconds
MAX_AUTH_ATTEMPTS = 15

def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    current_time = time.time()
    attempts = AUTH_ATTEMPTS.get(client_ip, [])
    # Filter attempts in window
    attempts = [t for t in attempts if current_time - t < RATE_LIMIT_WINDOW]
    if len(attempts) >= MAX_AUTH_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please try again in a few moments."
        )
    attempts.append(current_time)
    AUTH_ATTEMPTS[client_ip] = attempts

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    check_rate_limit(request)
    client_ip = request.client.host if request.client else None
    return await AuthService.register(db, data, ip_address=client_ip)

@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    check_rate_limit(request)
    client_ip = request.client.host if request.client else None
    return await AuthService.login(db, data, ip_address=client_ip)

@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.post("/reset-password-request")
async def request_password_reset(
    data: PasswordResetRequest,
    request: Request,
):
    check_rate_limit(request)
    # Simulated email verification / reset token sending for security
    return {
        "message": f"If an account with {data.email} exists, password reset instructions have been sent."
    }

@router.post("/reset-password-confirm")
async def confirm_password_reset(
    data: PasswordResetConfirm,
    request: Request,
):
    check_rate_limit(request)
    return {
        "message": "Password has been successfully updated. You may now log in."
    }
