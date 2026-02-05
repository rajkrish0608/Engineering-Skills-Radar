"""
Roles API Endpoints
REST API for role management and matching
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from utils.database import get_db
from services.role_service import RoleService

router = APIRouter(prefix="/api/roles", tags=["Roles"])


@router.get("/")
async def get_roles(
    category: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all roles with optional filters"""
    roles = RoleService.get_all_roles(db, category=category, branch=branch)
    
    return JSONResponse(content={
        'status': 'success',
        'count': len(roles),
        'roles': [
            {
                'id': str(r.id),
                'role_title': r.role_title,
                'category': r.role_category,
                'description': r.description,
                'avg_ctc': float(r.avg_ctc) if r.avg_ctc else None,
                'demand_score': r.demand_score,
                'eligible_branches': r.eligible_branches,
                'typical_companies': r.typical_companies
            }
            for r in roles
        ]
    })


@router.get("/{role_id}")
async def get_role(
    role_id: str,
    db: Session = Depends(get_db)
):
    """Get role by ID with full details"""
    try:
        role = RoleService.get_role_by_id(db, uuid.UUID(role_id))
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return JSONResponse(content={
            'status': 'success',
            'role': {
                'id': str(role.id),
                'role_title': role.role_title,
                'category': role.role_category,
                'description': role.description,
                'required_skills': role.required_skills,
                'eligible_branches': role.eligible_branches,
                'avg_ctc': float(role.avg_ctc) if role.avg_ctc else None,
                'demand_score': role.demand_score,
                'typical_companies': role.typical_companies
            }
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role ID format")
