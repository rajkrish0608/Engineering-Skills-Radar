"""
Bulk Operations API
Batch processing endpoints for TPO dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

from utils.database import get_db
from services.scoring_service import ScoringService
from services.role_matching_service import RoleMatchingService
from models.database_models import Student

router = APIRouter(prefix="/api/bulk", tags=["Bulk Operations"])


# Pydantic models
class BulkExtractRequest(BaseModel):
    student_ids: Optional[List[str]] = None  # If None, process all students
    branch: Optional[str] = None
    batch_year: Optional[int] = None
    sources: List[str] = Field(default=["projects", "certifications", "courses", "internships"])

class BulkScoreRequest(BaseModel):
    student_ids: Optional[List[str]] = None
    branch: Optional[str] = None
    batch_year: Optional[int] = None

class BulkMatchRequest(BaseModel):
    student_ids: Optional[List[str]] = None
    branch: Optional[str] = None
    batch_year: Optional[int] = None
    min_compatibility: float = Field(60.0, ge=0.0, le=100.0)


def get_filtered_students(
    db: Session,
    student_ids: Optional[List[str]] = None,
    branch: Optional[str] = None,
    batch_year: Optional[int] = None
) -> List[Student]:
    """Get students based on filters"""
    query = db.query(Student)
    
    if student_ids:
        # Specific students
        uuid_list = [uuid.UUID(sid) for sid in student_ids]
        query = query.filter(Student.id.in_(uuid_list))
    else:
        # Filter by branch/batch
        if branch:
            query = query.filter(Student.branch == branch)
        if batch_year:
            query = query.filter(Student.batch_year == batch_year)
    
    return query.all()


@router.post("/calculate-scores")
async def bulk_calculate_scores(
    request: BulkScoreRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Bulk recalculate skill scores for multiple students
    
    This is a heavy operation, so it runs in the background
    """
    try:
        # Get students
        students = get_filtered_students(
            db,
            student_ids=request.student_ids,
            branch=request.branch,
            batch_year=request.batch_year
        )
        
        if not students:
            raise HTTPException(status_code=404, detail="No students found matching criteria")
        
        # Run scoring in background
        def process_scores():
            scoring_service = ScoringService(db)
            processed = 0
            
            for student in students:
                try:
                    scoring_service.update_student_skill_scores(student.id)
                    processed += 1
                except Exception as e:
                    print(f"Error processing student {student.id}: {str(e)}")
            
            print(f"Bulk scoring complete: {processed}/{len(students)} students")
        
        background_tasks.add_task(process_scores)
        
        return JSONResponse(content={
            'status': 'success',
            'message': f'Score calculation started for {len(students)} students',
            'student_count': len(students),
            'note': 'Processing in background. Scores will be updated shortly.'
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")


@router.post("/match-roles")
async def bulk_match_roles(
    request: BulkMatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Bulk match students to roles and save results
    """
    try:
        # Get students
        students = get_filtered_students(
            db,
            student_ids=request.student_ids,
            branch=request.branch,
            batch_year=request.batch_year
        )
        
        if not students:
            raise HTTPException(status_code=404, detail="No students found")
        
        # Run matching in background
        def process_matches():
            matching_service = RoleMatchingService(db)
            processed = 0
            
            for student in students:
                try:
                    matches = matching_service.find_matching_roles(
                        student.id,
                        min_compatibility=request.min_compatibility
                    )
                    matching_service.save_role_matches(student.id, matches)
                    processed += 1
                except Exception as e:
                    print(f"Error matching student {student.id}: {str(e)}")
            
            print(f"Bulk matching complete: {processed}/{len(students)} students")
        
        background_tasks.add_task(process_matches)
        
        return JSONResponse(content={
            'status': 'success',
            'message': f'Role matching started for {len(students)} students',
            'student_count': len(students),
            'min_compatibility': request.min_compatibility,
            'note': 'Processing in background. Matches will be saved shortly.'
        })
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")


@router.get("/status/{operation_id}")
async def get_bulk_operation_status(
    operation_id: str,
    db: Session = Depends(get_db)
):
    """
    Check status of a bulk operation
    
    Note: This is a placeholder. For production, you'd use a task queue
    like Celery with Redis to track actual progress.
    """
    return JSONResponse(content={
        'status': 'success',
        'operation_id': operation_id,
        'state': 'completed',
        'progress': 100,
        'note': 'Background task completed. Check updated records in database.'
    })


@router.post("/import-students")
async def bulk_import_students(
    students_data: List[dict],
    db: Session = Depends(get_db)
):
    """
    Bulk import students from CSV/JSON data
    
    Expected format:
    [
        {
            "roll_number": "CS2021001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "branch": "CS",
            "batch_year": 2021,
            "current_semester": 6,
            "cgpa": 8.5
        },
        ...
    ]
    """
    try:
        from services.student_service import StudentService
        
        created_count = 0
        errors = []
        
        for idx, student_data in enumerate(students_data):
            try:
                # Check if student already exists
                existing = StudentService.get_student_by_roll(db, student_data.get('roll_number'))
                if existing:
                    errors.append({
                        'row': idx + 1,
                        'roll_number': student_data.get('roll_number'),
                        'error': 'Student already exists'
                    })
                    continue
                
                # Create student
                StudentService.create_student(db, student_data)
                created_count += 1
                
            except Exception as e:
                errors.append({
                    'row': idx + 1,
                    'roll_number': student_data.get('roll_number'),
                    'error': str(e)
                })
        
        return JSONResponse(content={
            'status': 'success',
            'created_count': created_count,
            'total_rows': len(students_data),
            'errors': errors
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
