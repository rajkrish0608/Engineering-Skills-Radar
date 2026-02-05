"""
Student API Endpoints
REST API for student operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
import uuid

from utils.database import get_db
from services.student_service import StudentService
from services.skill_service import SkillService
from services.role_service import RoleService

router = APIRouter(prefix="/api/students", tags=["Students"])


# Pydantic models for request/response
class StudentCreate(BaseModel):
    roll_number: str = Field(..., max_length=20)
    full_name: str = Field(..., max_length=100)
    email: EmailStr
    branch: str = Field(..., pattern="^(CS|IT|Mechanical|Civil|Electrical|ECE)$")
    batch_year: int = Field(..., ge=2000, le=2100)
    current_semester: int = Field(1, ge=1, le=8)
    cgpa: float = Field(0.0, ge=0.0, le=10.0)


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    current_semester: Optional[int] = Field(None, ge=1, le=8)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    account_status: Optional[str] = None


# Endpoints

@router.post("/", status_code=201)
async def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """Create a new student"""
    try:
        # Check if already exists
        existing = StudentService.get_student_by_roll(db, student.roll_number)
        if existing:
            raise HTTPException(status_code=400, detail="Student with this roll number already exists")
        
        # Create student
        new_student = StudentService.create_student(db, student.dict())
        
        return JSONResponse(content={
            'status': 'success',
            'message': 'Student created successfully',
            'student': {
                'id': str(new_student.id),
                'roll_number': new_student.roll_number,
                'full_name': new_student.full_name,
                'email': new_student.email,
                'branch': new_student.branch
            }
        }, status_code=201)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_students(
    branch: Optional[str] = Query(None),
    batch_year: Optional[int] = Query(None),
    semester: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get students with optional filters and pagination"""
    students = StudentService.get_students(
        db,
        branch=branch,
        batch_year=batch_year,
        semester=semester,
        skip=skip,
        limit=limit
    )
    
    return JSONResponse(content={
        'status': 'success',
        'count': len(students),
        'students': [
            {
                'id': str(s.id),
                'roll_number': s.roll_number,
                'full_name': s.full_name,
                'email': s.email,
                'branch': s.branch,
                'batch_year': s.batch_year,
                'current_semester': s.current_semester,
                'cgpa': float(s.cgpa) if s.cgpa else 0.0,
                'account_status': s.account_status
            }
            for s in students
        ]
    })


@router.get("/search")
async def search_students(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """Search students by roll number, name, or email"""
    students = StudentService.search_students(db, q)
    
    return JSONResponse(content={
        'status': 'success',
        'count': len(students),
        'students': [
            {
                'id': str(s.id),
                'roll_number': s.roll_number,
                'full_name': s.full_name,
                'email': s.email,
                'branch': s.branch
            }
            for s in students
        ]
    })


@router.get("/{student_id}")
async def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Get student by ID"""
    try:
        student = StudentService.get_student_by_id(db, uuid.UUID(student_id))
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return JSONResponse(content={
            'status': 'success',
            'student': {
                'id': str(student.id),
                'roll_number': student.roll_number,
                'full_name': student.full_name,
                'email': student.email,
                'branch': student.branch,
                'batch_year': student.batch_year,
                'current_semester': student.current_semester,
                'cgpa': float(student.cgpa) if student.cgpa else 0.0,
                'account_status': student.account_status,
                'created_at': student.created_at.isoformat() if student.created_at else None
            }
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")


@router.put("/{student_id}")
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    """Update student information"""
    try:
        # Filter out None values
        update_data = {k: v for k, v in student_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_student = StudentService.update_student(
            db,
            uuid.UUID(student_id),
            update_data
        )
        
        if not updated_student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return JSONResponse(content={
            'status': 'success',
            'message': 'Student updated successfully',
            'student': {
                'id': str(updated_student.id),
                'roll_number': updated_student.roll_number,
                'full_name': updated_student.full_name
            }
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")


@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Delete student (cascade deletes all related records)"""
    try:
        success = StudentService.delete_student(db, uuid.UUID(student_id))
        
        if not success:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return JSONResponse(content={
            'status': 'success',
            'message': 'Student deleted successfully'
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")


@router.get("/{student_id}/skills")
async def get_student_skills(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Get all skills for a student"""
    try:
        skills = StudentService.get_student_skills(db, uuid.UUID(student_id))
        
        return JSONResponse(content={
            'status': 'success',
            'count': len(skills),
            'skills': [
                {
                    'skill_id': str(ss.skill_id),
                    'skill_name': ss.skill.skill_name,
                    'category': ss.skill.skill_category,
                    'weighted_score': float(ss.weighted_score),
                    'confidence': float(ss.confidence_level),
                    'evidence_count': len(ss.evidence_sources) if ss.evidence_sources else 0,
                    'last_updated': ss.last_updated.isoformat() if ss.last_updated else None
                }
                for ss in skills
            ]
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")


@router.get("/{student_id}/role-matches")
async def get_role_matches(
    student_id: str,
    top_n: int = Query(10, ge=1, le=50),
    recalculate: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get top role matches for a student
    
    Args:
        student_id: Student UUID
        top_n: Number of top matches to return
        recalculate: Whether to recalculate matches (default: use cached)
    """
    try:
        if recalculate:
            # Recalculate and save matches
            matches = RoleService.match_student_to_roles(
                db, 
                uuid.UUID(student_id),
                top_n=top_n,
                save_to_db=True
            )
        else:
            # Get cached matches
            matches = StudentService.get_student_role_matches(db, uuid.UUID(student_id), top_n)
            matches = [
                {
                    'role_id': str(m.role.id),
                    'role_title': m.role.role_title,
                    'role_category': m.role.role_category,
                    'match_score': float(m.match_score),
                    'missing_skills': m.missing_skills,
                    'avg_ctc': float(m.role.avg_ctc) if m.role.avg_ctc else None,
                    'demand_score': m.role.demand_score,
                    'calculated_at': m.calculated_at.isoformat() if m.calculated_at else None
                }
                for m in matches
            ]
        
        return JSONResponse(content={
            'status': 'success',
            'student_id': student_id,
            'count': len(matches),
            'matches': matches
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")


@router.get("/{student_id}/role-gap/{role_id}")
async def get_role_gaps(
    student_id: str,
    role_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed gap analysis for student-role combination"""
    try:
        gaps = RoleService.get_role_gaps(
            db,
            uuid.UUID(student_id),
            uuid.UUID(role_id)
        )
        
        if 'error' in gaps:
            raise HTTPException(status_code=404, detail=gaps['error'])
        
        return JSONResponse(content={
            'status': 'success',
            'gap_analysis': gaps
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")


@router.get("/{student_id}/projects")
async def get_student_projects(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Get all projects for a student"""
    try:
        projects = StudentService.get_student_projects(db, uuid.UUID(student_id))
        
        return JSONResponse(content={
            'status': 'success',
            'count': len(projects),
            'projects': [
                {
                    'id': str(p.id),
                    'title': p.project_title,
                    'type': p.project_type,
                    'semester': p.semester,
                    'tech_stack': p.tech_stack,
                    'document_url': p.document_url
                }
                for p in projects
            ]
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")


@router.get("/{student_id}/certifications")
async def get_student_certifications(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Get all certifications for a student"""
    try:
        certs = StudentService.get_student_certifications(db, uuid.UUID(student_id))
        
        return JSONResponse(content={
            'status': 'success',
            'count': len(certs),
            'certifications': [
                {
                    'id': str(c.id),
                    'title': c.certification_title,
                    'provider': c.provider,
                    'credibility': float(c.provider_credibility) if c.provider_credibility else 0.7,
                    'completion_date': c.completion_date.isoformat() if c.completion_date else None,
                    'certificate_url': c.certificate_url
                }
                for c in certs
            ]
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
