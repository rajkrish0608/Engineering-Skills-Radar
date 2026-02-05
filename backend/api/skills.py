"""
Skills API Endpoints
REST API for skill management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid

from utils.database import get_db
from services.skill_service import SkillService

router = APIRouter(prefix="/api/skills", tags=["Skills"])


# Pydantic models
class AssessmentSubmit(BaseModel):
    student_id: str
    skill_id: str
    assessment_type: str = Field(..., pattern="^(quiz|project|certification|internship|course)$")
    score: int = Field(..., ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


@router.get("/")
async def get_skills(
    category: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all skills with optional filters"""
    skills = SkillService.get_all_skills(db, category=category, branch=branch)
    
    return JSONResponse(content={
        'status': 'success',
        'count': len(skills),
        'skills': [
            {
                'id': str(s.id),
                'skill_name': s.skill_name,
                'category': s.skill_category,
                'description': s.description,
                'branches': s.branches,
                'benchmark_score': s.benchmark_score
            }
            for s in skills
        ]
    })


@router.get("/{skill_id}")
async def get_skill(
    skill_id: str,
    db: Session = Depends(get_db)
):
    """Get skill by ID"""
    try:
        skill = SkillService.get_skill_by_id(db, uuid.UUID(skill_id))
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return JSONResponse(content={
            'status': 'success',
            'skill': {
                'id': str(skill.id),
                'skill_name': skill.skill_name,
                'category': skill.skill_category,
                'description': skill.description,
                'branches': skill.branches,
                'benchmark_score': skill.benchmark_score
            }
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")


@router.get("/{skill_id}/statistics")
async def get_skill_stats(
    skill_id: str,
    db: Session = Depends(get_db)
):
    """Get statistics for a skill across all students"""
    try:
        stats = SkillService.get_skill_statistics(db, uuid.UUID(skill_id))
        
        return JSONResponse(content={
            'status': 'success',
            'statistics': stats
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")


@router.post("/assessments")
async def submit_assessment(
    assessment: AssessmentSubmit,
    db: Session = Depends(get_db)
):
    """Submit a skill assessment"""
    try:
        created_assessment = SkillService.submit_assessment(
            db,
            student_id=uuid.UUID(assessment.student_id),
            skill_id=uuid.UUID(assessment.skill_id),
            assessment_type=assessment.assessment_type,
            score=assessment.score,
            metadata=assessment.metadata
        )
        
        return JSONResponse(content={
            'status': 'success',
            'message': 'Assessment submitted successfully',
            'assessment': {
                'id': str(created_assessment.id),
                'type': created_assessment.assessment_type,
                'score': created_assessment.score,
                'completed_at': created_assessment.completed_at.isoformat()
            }
        }, status_code=201)
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
