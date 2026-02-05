"""
Analytics API
Data insights and statistics for TPO dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import uuid

from utils.database import get_db
from models.database_models import (
    Student, Skill, StudentSkill, IndustryRole, 
    StudentRoleMatch, RoleSkill
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/skill-distribution")
async def get_skill_distribution(
    branch: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get distribution of skills across students
    
    Returns top N skills with average proficiency and student count
    """
    try:
        # Base query
        query = db.query(
            Skill.skill_name,
            Skill.skill_category,
            func.avg(StudentSkill.proficiency_score).label('avg_score'),
            func.count(StudentSkill.student_id).label('student_count')
        ).join(
            StudentSkill, Skill.id == StudentSkill.skill_id
        )
        
        # Filter by branch if specified
        if branch:
            query = query.join(
                Student, StudentSkill.student_id == Student.id
            ).filter(Student.branch == branch)
        
        # Group and order
        results = query.group_by(
            Skill.id, Skill.skill_name, Skill.skill_category
        ).order_by(
            func.count(StudentSkill.student_id).desc()
        ).limit(limit).all()
        
        return JSONResponse(content={
            'status': 'success',
            'skills': [
                {
                    'skill_name': r.skill_name,
                    'category': r.skill_category,
                    'avg_score': round(float(r.avg_score), 1) if r.avg_score else 0.0,
                    'student_count': r.student_count
                }
                for r in results
            ]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/branch-stats")
async def get_branch_statistics(
    db: Session = Depends(get_db)
):
    """
    Get statistics by branch
    
    Returns student count, avg CGPA, avg skill score, placement readiness per branch
    """
    try:
        branches = ['CS', 'IT', 'Mechanical', 'Civil', 'Electrical', 'ECE']
        
        stats = []
        for branch in branches:
            # Get student count
            student_count = db.query(func.count(Student.id)).filter(
                Student.branch == branch
            ).scalar()
            
            if student_count == 0:
                continue
            
            # Get avg CGPA
            avg_cgpa = db.query(func.avg(Student.cgpa)).filter(
                Student.branch == branch
            ).scalar()
            
            # Get avg skill score
            avg_skill_score = db.query(
                func.avg(StudentSkill.proficiency_score)
            ).join(
                Student, StudentSkill.student_id == Student.id
            ).filter(
                Student.branch == branch
            ).scalar()
            
            # Get students with high match scores (>70%)
            high_match_count = db.query(
                func.count(func.distinct(StudentRoleMatch.student_id))
            ).join(
                Student, StudentRoleMatch.student_id == Student.id
            ).filter(
                Student.branch == branch,
                StudentRoleMatch.compatibility_score >= 70.0
            ).scalar()
            
            stats.append({
                'branch': branch,
                'total_students': student_count,
                'avg_cgpa': round(float(avg_cgpa), 2) if avg_cgpa else 0.0,
                'avg_skill_score': round(float(avg_skill_score), 1) if avg_skill_score else 0.0,
                'placement_ready': high_match_count,
                'placement_ready_percentage': round((high_match_count / student_count) * 100, 1) if student_count > 0 else 0.0
            })
        
        return JSONResponse(content={
            'status': 'success',
            'branches': stats
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/role-demand")
async def get_role_demand_stats(
    db: Session = Depends(get_db)
):
    """
    Get role demand vs supply statistics
    
    Returns roles with opening count vs qualified student count
    """
    try:
        roles = db.query(IndustryRole).all()
        
        stats = []
        for role in roles:
            # Get qualified students (compatibility >= 70%)
            qualified_count = db.query(
                func.count(StudentRoleMatch.student_id)
            ).filter(
                StudentRoleMatch.role_id == role.id,
                StudentRoleMatch.compatibility_score >= 70.0
            ).scalar()
            
            # Get highly qualified students (compatibility >= 85%)
            highly_qualified = db.query(
                func.count(StudentRoleMatch.student_id)
            ).filter(
                StudentRoleMatch.role_id == role.id,
                StudentRoleMatch.compatibility_score >= 85.0
            ).scalar()
            
            stats.append({
                'role_id': str(role.id),
                'role_title': role.role_title,
                'company': role.company,
                'ctc_range': role.ctc_range,
                'openings': role.openings if hasattr(role, 'openings') else 0,
                'qualified_students': qualified_count or 0,
                'highly_qualified': highly_qualified or 0
            })
        
        # Sort by demand-supply gap
        stats.sort(key=lambda x: x['qualified_students'], reverse=True)
        
        return JSONResponse(content={
            'status': 'success',
            'roles': stats
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db)
):
    """
    Get high-level dashboard metrics
    """
    try:
        # Total students
        total_students = db.query(func.count(Student.id)).scalar()
        
        # Total roles
        total_roles = db.query(func.count(IndustryRole.id)).scalar()
        
        # Avg placement rate (students with at least one high match)
        placed_students = db.query(
            func.count(func.distinct(StudentRoleMatch.student_id))
        ).filter(
            StudentRoleMatch.compatibility_score >= 70.0
        ).scalar()
        
        placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0.0
        
        # Avg skill proficiency across all students
        avg_skill_score = db.query(
            func.avg(StudentSkill.proficiency_score)
        ).scalar()
        
        return JSONResponse(content={
            'status': 'success',
            'metrics': {
                'total_students': total_students or 0,
                'total_roles': total_roles or 0,
                'placement_ready_percentage': round(placement_rate, 1),
                'avg_skill_score': round(float(avg_skill_score), 1) if avg_skill_score else 0.0,
                'active_recruitments': total_roles or 0  # Placeholder
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-students")
async def get_top_students(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get top students by average skill score
    """
    try:
        # Get students with avg skill scores
        results = db.query(
            Student.id,
            Student.roll_number,
            Student.full_name,
            Student.branch,
            Student.cgpa,
            func.avg(StudentSkill.proficiency_score).label('avg_score'),
            func.count(StudentSkill.skill_id).label('skill_count')
        ).join(
            StudentSkill, Student.id == StudentSkill.student_id
        ).group_by(
            Student.id
        ).order_by(
            func.avg(StudentSkill.proficiency_score).desc()
        ).limit(limit).all()
        
        return JSONResponse(content={
            'status': 'success',
            'students': [
                {
                    'student_id': str(r.id),
                    'roll_number': r.roll_number,
                    'full_name': r.full_name,
                    'branch': r.branch,
                    'cgpa': float(r.cgpa) if r.cgpa else 0.0,
                    'avg_skill_score': round(float(r.avg_score), 1) if r.avg_score else 0.0,
                    'skill_count': r.skill_count
                }
                for r in results
            ]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
