"""
Example of Protected API Endpoints
Demonstrates how to use authentication and role-based access control
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from utils.database import get_db
from utils.auth_middleware import (
    get_current_user,
    get_current_active_user,
    require_admin,
    require_tpo,
    require_faculty,
    RoleChecker
)
from models.database_models import User

router = APIRouter(prefix="/api/protected", tags=["Protected Examples"])


@router.get("/public")
async def public_endpoint():
    """
    Public endpoint - no authentication required
    """
    return JSONResponse(content={
        'status': 'success',
        'message': 'This is a public endpoint, accessible to everyone'
    })


@router.get("/authenticated")
async def authenticated_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Authenticated endpoint - requires valid JWT token
    Accessible to any authenticated user regardless of role
    """
    return JSONResponse(content={
        'status': 'success',
        'message': f'Hello {current_user.full_name or current_user.username}!',
        'user_role': current_user.role
    })


@router.get("/admin-only")
async def admin_only_endpoint(
    current_user: User = Depends(require_admin)
):
    """
    Admin-only endpoint
    Only accessible to users with 'admin' role
    """
    return JSONResponse(content={
        'status': 'success',
        'message': 'Welcome Admin! This is an admin-only area.',
        'admin_username': current_user.username
    })


@router.get("/tpo-dashboard")
async def tpo_dashboard(
    current_user: User = Depends(require_tpo)
):
    """
    TPO Dashboard endpoint
    Accessible to TPO and Admin users
    """
    return JSONResponse(content={
        'status': 'success',
        'message': 'TPO Dashboard Access Granted',
        'user': {
            'username': current_user.username,
            'role': current_user.role,
            'department': current_user.department
        }
    })


@router.get("/faculty-tools")
async def faculty_tools(
    current_user: User = Depends(require_faculty)
):
    """
    Faculty Tools endpoint
    Accessible to Faculty and Admin users
    """
    return JSONResponse(content={
        'status': 'success',
        'message': 'Faculty Tools Access Granted',
        'user': {
            'username': current_user.username,
            'role': current_user.role
        }
    })


@router.get("/student-tpo-shared")
async def student_tpo_shared(
    current_user: User = Depends(RoleChecker(["student", "tpo", "admin"]))
):
    """
    Shared endpoint for multiple roles
    Accessible to Students, TPO, and Admin
    """
    return JSONResponse(content={
        'status': 'success',
        'message': 'Multi-role endpoint',
        'accessible_by': ['student', 'tpo', 'admin'],
        'your_role': current_user.role
    })
