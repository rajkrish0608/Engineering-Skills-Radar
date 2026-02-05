"""
Data Ingestion API Endpoints
Handles CSV uploads and file uploads
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io

from services.csv_upload_service import CSVUploadService, CSVValidationError
from services.file_storage_service import FileStorageService
from utils.database import get_db

router = APIRouter(prefix="/api/ingestion", tags=["Data Ingestion"])

# Initialize services
csv_service = CSVUploadService(max_rows=1000)
storage_service = FileStorageService()


@router.post("/csv/validate")
async def validate_csv(
    file: UploadFile = File(...),
    upload_type: str = Form(...)
):
    """
    Validate CSV file without importing
    
    Args:
        file: CSV file to validate
        upload_type: One of: students, courses, projects, certifications, internships
    
    Returns:
        Validation report with valid/error counts
    """
    # Validate upload type
    valid_types = ['students', 'courses', 'projects', 'certifications', 'internships']
    if upload_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid upload type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Check file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate CSV
        result = csv_service.validate_upload(file_content, upload_type)
        
        return JSONResponse(content={
            'status': 'success',
            'validation_result': {
                'upload_type': result['upload_type'],
                'total_rows': result['total_rows'],
                'valid_count': result['valid_count'],
                'error_count': result['error_count'],
                'success_rate': result['success_rate'],
                'error_records': result['error_records'][:10]  # Show first 10 errors
            },
            'ready_for_import': result['error_count'] == 0
        })
    
    except CSVValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")


@router.post("/csv/import")
async def import_csv(
    file: UploadFile = File(...),
    upload_type: str = Form(...),
    skip_duplicates: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Import CSV data into database
    
    Args:
        file: CSV file to import
        upload_type: Data type to import
        skip_duplicates: Whether to skip duplicate records
        db: Database session
    
    Returns:
        Import result with success/failure counts
    """
    # Validate upload type
    valid_types = ['students', 'courses', 'projects', 'certifications', 'internships']
    if upload_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid upload type")
    
    try:
        # Read and validate file
        file_content = await file.read()
        validation_result = csv_service.validate_upload(file_content, upload_type)
        
        if validation_result['error_count'] > 0:
            return JSONResponse(
                status_code=400,
                content={
                    'status': 'validation_failed',
                    'message': f"CSV has {validation_result['error_count']} validation errors",
                    'error_records': validation_result['error_records']
                }
            )
        
        # TODO: Implement actual database insertion
        # This will be implemented in Phase 7 (Backend API Development)
        # For now, return success with validation data
        
        return JSONResponse(content={
            'status': 'success',
            'message': f"Successfully validated {validation_result['valid_count']} records",
            'imported_count': validation_result['valid_count'],
            'skipped_count': 0,
            'note': 'Database insertion will be implemented in Phase 7'
        })
    
    except CSVValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")


@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(...),  # syllabi, projects, certificates
    student_roll: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload document file (PDF, DOCX) to storage
    
    Args:
        file: File to upload
        category: File category (syllabi, projects, certificates)
        student_roll: Optional student roll number
        description: Optional file description
    
    Returns:
        Upload result with file URL
    """
    # Validate file
    file_size = 0
    file_content = await file.read()
    file_size = len(file_content)
    
    is_valid, error_msg = storage_service.validate_file(file.filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Upload to storage
    metadata = {}
    if description:
        metadata['description'] = description
    if student_roll:
        metadata['student_roll'] = student_roll
    
    result = storage_service.upload_file(
        file_content=io.BytesIO(file_content),
        filename=file.filename,
        category=category,
        student_roll=student_roll,
        metadata=metadata
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return JSONResponse(content={
        'status': 'success',
        'file_url': result['file_url'],
        'object_name': result['object_name'],
        'bucket': result['bucket'],
        'uploaded_at': result['uploaded_at']
    })


@router.get("/files/list")
async def list_files(
    category: Optional[str] = None,
    student_roll: Optional[str] = None
):
    """
    List uploaded files
    
    Args:
        category: Filter by category
        student_roll: Filter by student
    
    Returns:
        List of files
    """
    prefix = ""
    if category:
        prefix = f"{category}/"
    if student_roll and category:
        prefix = f"{category}/{student_roll}"
    
    files = storage_service.list_files(prefix=prefix)
    
    return JSONResponse(content={
        'status': 'success',
        'count': len(files),
        'files': files
    })


@router.get("/templates/download")
async def download_template(template_type: str):
    """
    Download CSV template
    
    Args:
        template_type: Template to download (students, courses, etc.)
    
    Returns:
        CSV file
    """
    from fastapi.responses import FileResponse
    import os
    
    template_path = f"data_templates/{template_type}_template.csv"
    
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Template not found")
    
    return FileResponse(
        path=template_path,
        media_type='text/csv',
        filename=f"{template_type}_template.csv"
    )
