"""
Skill Management Service
Handles skill CRUD and student skill scoring
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models.database_models import Skill, StudentSkill, SkillAssessment


class SkillService:
    """Service for skill management"""
    
    @staticmethod
    def get_all_skills(
        db: Session,
        category: Optional[str] = None,
        branch: Optional[str] = None
    ) -> List[Skill]:
        """
        Get all skills with optional filters
        
        Args:
            db: Database session
            category: Filter by skill category
            branch: Filter by branch eligibility
        
        Returns:
            List of skills
        """
        query = db.query(Skill)
        
        if category:
            query = query.filter(Skill.skill_category == category)
        if branch:
            # Filter skills that include this branch in JSONB array
            query = query.filter(Skill.branches.contains([branch]))
        
        return query.all()
    
    @staticmethod
    def get_skill_by_id(db: Session, skill_id: uuid.UUID) -> Optional[Skill]:
        """Get skill by ID"""
        return db.query(Skill).filter(Skill.id == skill_id).first()
    
    @staticmethod
    def get_skill_by_name(db: Session, skill_name: str) -> Optional[Skill]:
        """Get skill by name"""
        return db.query(Skill).filter(Skill.skill_name == skill_name).first()
    
    @staticmethod
    def create_student_skill(
        db: Session,
        student_id: uuid.UUID,
        skill_id: uuid.UUID,
        evidence_sources: List[Dict[str, Any]]
    ) -> StudentSkill:
        """
        Create or update student skill score
        
        Args:
            db: Database session
            student_id: Student ID
            skill_id: Skill ID
            evidence_sources: List of evidence (quiz, project, cert, etc.)
        
        Returns:
            StudentSkill object with calculated scores
        """
        # Calculate weighted score from evidence
        weights = {
            "quiz": 0.4,
            "project": 0.35,
            "certification": 0.25,
            "internship": 0.20
        }
        
        source_scores = {}
        for evidence in evidence_sources:
            source_type = evidence.get("type")
            score = evidence.get("score", 0)
            source_scores[source_type] = min(100, max(0, score))
        
        # Weighted average (missing sources default to 50)
        total_score = sum(
            source_scores.get(source_type, 50) * weight
            for source_type, weight in weights.items()
        )
        
        # Confidence based on evidence count
        confidence = min(1.0, len(evidence_sources) * 0.2)
        
        # Check if student skill already exists
        existing = db.query(StudentSkill).filter(
            and_(
                StudentSkill.student_id == student_id,
                StudentSkill.skill_id == skill_id
            )
        ).first()
        
        if existing:
            # Update existing
            existing.raw_score = int(total_score)
            existing.weighted_score = round(total_score, 2)
            existing.confidence_level = round(confidence, 2)
            existing.evidence_sources = evidence_sources
            existing.last_updated = datetime.now()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new
            student_skill = StudentSkill(
                student_id=student_id,
                skill_id=skill_id,
                raw_score=int(total_score),
                weighted_score=round(total_score, 2),
                confidence_level=round(confidence, 2),
                evidence_sources=evidence_sources
            )
            db.add(student_skill)
            db.commit()
            db.refresh(student_skill)
            return student_skill
    
    @staticmethod
    def submit_assessment(
        db: Session,
        student_id: uuid.UUID,
        skill_id: uuid.UUID,
        assessment_type: str,
        score: int,
        metadata: Optional[Dict] = None
    ) -> SkillAssessment:
        """
        Submit a skill assessment
        
        Args:
            db: Database session
            student_id: Student ID
            skill_id: Skill ID
            assessment_type: Type (quiz, project, certification, etc.)
            score: Score (0-100)
            metadata: Additional metadata
        
        Returns:
            Created SkillAssessment
        """
        assessment = SkillAssessment(
            student_id=student_id,
            skill_id=skill_id,
            assessment_type=assessment_type,
            score=score,
            metadata=metadata or {}
        )
        
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        # Recalculate student skill score
        SkillService.recalculate_student_skill(db, student_id, skill_id)
        
        return assessment
    
    @staticmethod
    def recalculate_student_skill(
        db: Session,
        student_id: uuid.UUID,
        skill_id: uuid.UUID
    ) -> Optional[StudentSkill]:
        """
        Recalculate student skill score from all assessments
        
        Args:
            db: Database session
            student_id: Student ID
            skill_id: Skill ID
        
        Returns:
            Updated StudentSkill
        """
        # Get all assessments for this student-skill
        assessments = db.query(SkillAssessment).filter(
            and_(
                SkillAssessment.student_id == student_id,
                SkillAssessment.skill_id == skill_id
            )
        ).all()
        
        if not assessments:
            return None
        
        # Group evidence by type
        evidence_sources = []
        for assessment in assessments:
            evidence_sources.append({
                "type": assessment.assessment_type,
                "score": assessment.score,
                "assessed_at": assessment.completed_at.isoformat()
            })
        
        # Update student skill
        return SkillService.create_student_skill(
            db, student_id, skill_id, evidence_sources
        )
    
    @staticmethod
    def get_skill_statistics(db: Session, skill_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get statistics for a skill across all students
        
        Returns:
            Dictionary with avg score, min, max, student count
        """
        stats = db.query(
            func.avg(StudentSkill.weighted_score).label('avg_score'),
            func.min(StudentSkill.weighted_score).label('min_score'),
            func.max(StudentSkill.weighted_score).label('max_score'),
            func.count(StudentSkill.id).label('student_count')
        ).filter(StudentSkill.skill_id == skill_id).first()
        
        return {
            'skill_id': str(skill_id),
            'average_score': round(float(stats.avg_score or 0), 2),
            'min_score': float(stats.min_score or 0),
            'max_score': float(stats.max_score or 0),
            'student_count': stats.student_count or 0
        }
