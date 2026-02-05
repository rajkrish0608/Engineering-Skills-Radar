"""
Authentication API Endpoints
Handles login, registration, token refresh, and password management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from utils.database import get_db
from services.auth_service import AuthService
from utils.auth_middleware import get_current_user, get_current_active_user
from models.database_models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = Field(..., pattern="^(student|tpo|faculty|admin)$")
    department: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class TokenRefresh(BaseModel):
    refresh_token: str


# Endpoints

@router.post("/register", status_code=201)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Note: In production, this should be restricted or require admin approval
    """
    # Check if username already exists
    existing_user = AuthService.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = AuthService.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    try:
        user = AuthService.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role,
            full_name=user_data.full_name,
            department=user_data.department
        )
        
        return JSONResponse(content={
            'status': 'success',
            'message': 'User registered successfully',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }, status_code=201)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/login")
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login and get access and refresh tokens
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    token_data = {
        "sub": user.username,
        "user_id": str(user.id),
        "role": user.role
    }
    
    access_token = AuthService.create_access_token(token_data)
    refresh_token = AuthService.create_refresh_token({"sub": user.username, "user_id": str(user.id)})
    
    return JSONResponse(content={
        'status': 'success',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name
        }
    })


@router.post("/refresh")
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    payload = AuthService.verify_token(token_data.refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Get user
    username = payload.get("sub")
    user = AuthService.get_user_by_username(db, username)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    token_data_new = {
        "sub": user.username,
        "user_id": str(user.id),
        "role": user.role
    }
    
    access_token = AuthService.create_access_token(token_data_new)
    
    return JSONResponse(content={
        'status': 'success',
        'access_token': access_token,
        'token_type': 'bearer'
    })


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information
    """
    return JSONResponse(content={
        'status': 'success',
        'user': {
            'id': str(current_user.id),
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'full_name': current_user.full_name,
            'department': current_user.department,
            'is_active': current_user.is_active,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }
    })


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    """
    success = AuthService.change_password(
        db,
        str(current_user.id),
        password_data.old_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    return JSONResponse(content={
        'status': 'success',
        'message': 'Password changed successfully'
    })


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout (client-side token invalidation)
    
    Note: With JWT, logout is typically handled client-side by removing the token.
    For server-side logout, implement token blacklisting.
    """
    return JSONResponse(content={
        'status': 'success',
        'message': 'Logged out successfully'
    })
