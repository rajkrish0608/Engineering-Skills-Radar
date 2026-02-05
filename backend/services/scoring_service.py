"""
Scoring Service
Multi-source evidence aggregation with credibility weighting and time decay
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from models.database_models import (
    Student, Skill, StudentSkill, Project, Certification, 
    Course, StudentCourse, Internship, SkillAssessment
)
from services.skill_extraction_service import SkillExtractionService
from services.certification_mapper import CertificationMapper
from services.course_skill_mapper import CourseSkillMapper

@dataclass
class Evidence:
    """Represents a piece of evidence for a skill"""
    source_type: str  # 'project', 'certification', 'course', 'internship', 'assessment'
    source_id: str
    skill_id: str
    skill_name: str
    confidence: float  # 0-1
    date: datetime
    evidence_text: str
    
class ScoringService:
    """
    Evidence-based skill scoring with multi-source aggregation
    """
    
    # Credibility weights for different evidence sources
    CREDIBILITY_WEIGHTS = {
        'certification': 1.0,
        'internship': 0.95,
        'project': 0.85,
        'assessment': 0.80,
        'course': 0.70
    }
    
    def __init__(self, db: Session):
        """
        Initialize scoring service
        
        Args:
            db: Database session
        """
        self.db = db
        self.extraction_service = SkillExtractionService(db)
        self.cert_mapper = CertificationMapper(db)
        self.course_mapper = CourseSkillMapper(db)
    
    def calculate_time_decay(self, evidence_date: datetime) -> float:
        """
        Calculate time decay factor based on evidence age
        
        Args:
            evidence_date: Date of evidence
            
        Returns:
            Decay factor (0.7-1.0)
        """
        if not evidence_date:
            return 1.0
        
        now = datetime.now()
        months_old = (now - evidence_date).days / 30.0
        
        # Linear decay: 1.0 - (months_old / 24) * 0.3
        # Caps at 0.7 (30% decay after 24 months)
        decay = max(0.7, 1.0 - (months_old / 24.0) * 0.3)
        
        return decay
    
    def collect_evidence_from_projects(self, student_id: uuid.UUID) -> List[Evidence]:
        """Collect skill evidence from student projects"""
        evidence = []
        
        projects = self.db.query(Project).filter(
            Project.student_id == student_id
        ).all()
        
        for project in projects:
            # Extract skills from project description
            if project.description:
                skill_matches = self.extraction_service.extract_from_project(
                    project.description
                )
                
                for match in skill_matches:
                    evidence.append(Evidence(
                        source_type='project',
                        source_id=str(project.id),
                        skill_id=match.skill_id,
                        skill_name=match.skill_name,
                        confidence=match.confidence,
                        date=project.end_date or project.start_date,
                        evidence_text=f"Project: {project.title}"
                    ))
        
        return evidence
    
    def collect_evidence_from_certifications(self, student_id: uuid.UUID) -> List[Evidence]:
        """Collect skill evidence from certifications"""
        evidence = []
        
        certs = self.db.query(Certification).filter(
            Certification.student_id == student_id
        ).all()
        
        for cert in certs:
            # Map certification to skills
            skill_matches = self.cert_mapper.map_certification(
                cert_title=cert.certification_name,
                provider=cert.issuing_organization
            )
            
            for match in skill_matches:
                evidence.append(Evidence(
                    source_type='certification',
                    source_id=str(cert.id),
                    skill_id=match['skill_id'],
                    skill_name=match['skill_name'],
                    confidence=match['confidence'],
                    date=cert.issue_date,
                    evidence_text=f"Certification: {cert.certification_name}"
                ))
        
        return evidence
    
    def collect_evidence_from_courses(self, student_id: uuid.UUID) -> List[Evidence]:
        """Collect skill evidence from courses"""
        evidence = []
        
        student_courses = self.db.query(StudentCourse, Course).join(
            Course, StudentCourse.course_id == Course.id
        ).filter(
            StudentCourse.student_id == student_id
        ).all()
        
        for student_course, course in student_courses:
            # Map course to skills
            skill_matches = self.course_mapper.map_course(
                course_code=course.course_code,
                course_name=course.course_name
            )
            
            for match in skill_matches:
                evidence.append(Evidence(
                    source_type='course',
                    source_id=str(course.id),
                    skill_id=match['skill_id'],
                    skill_name=match['skill_name'],
                    confidence=match['confidence'],
                    date=student_course.completed_date or datetime.now(),
                    evidence_text=f"Course: {course.course_name}"
                ))
        
        return evidence
    
    def collect_evidence_from_internships(self, student_id: uuid.UUID) -> List[Evidence]:
        """Collect skill evidence from internships"""
        evidence = []
        
        internships = self.db.query(Internship).filter(
            Internship.student_id == student_id
        ).all()
        
        for internship in internships:
            # Extract skills from description
            if internship.description:
                skill_matches = self.extraction_service.extract_skills(
                    text=internship.description,
                    source='internship'
                )
                
                for match in skill_matches:
                    evidence.append(Evidence(
                        source_type='internship',
                        source_id=str(internship.id),
                        skill_id=match.skill_id,
                        skill_name=match.skill_name,
                        confidence=match.confidence,
                        date=internship.end_date or internship.start_date,
                        evidence_text=f"Internship: {internship.company_name}"
                    ))
        
        return evidence
    
    def collect_evidence_from_assessments(self, student_id: uuid.UUID) -> List[Evidence]:
        """Collect skill evidence from direct assessments"""
        evidence = []
        
        assessments = self.db.query(SkillAssessment, Skill).join(
            Skill, SkillAssessment.skill_id == Skill.id
        ).filter(
            SkillAssessment.student_id == student_id
        ).all()
        
        for assessment, skill in assessments:
            # Direct score (convert 0-100 to 0-1 confidence)
            evidence.append(Evidence(
                source_type='assessment',
                source_id=str(assessment.id),
                skill_id=str(skill.id),
                skill_name=skill.skill_name,
                confidence=assessment.score / 100.0,
                date=assessment.completed_at,
                evidence_text=f"Assessment: {assessment.assessment_type}"
            ))
        
        return evidence
    
    def collect_all_evidence(self, student_id: uuid.UUID) -> List[Evidence]:
        """
        Collect all evidence for a student from all sources
        
        Args:
            student_id: Student UUID
            
        Returns:
            List of all evidence pieces
        """
        all_evidence = []
        
        all_evidence.extend(self.collect_evidence_from_projects(student_id))
        all_evidence.extend(self.collect_evidence_from_certifications(student_id))
        all_evidence.extend(self.collect_evidence_from_courses(student_id))
        all_evidence.extend(self.collect_evidence_from_internships(student_id))
        all_evidence.extend(self.collect_evidence_from_assessments(student_id))
        
        return all_evidence
    
    def calculate_skill_score(
        self,
        student_id: uuid.UUID,
        skill_id: uuid.UUID
    ) -> Tuple[float, List[Evidence]]:
        """
        Calculate weighted score for a specific skill
        
        Args:
            student_id: Student UUID
            skill_id: Skill UUID
            
        Returns:
            Tuple of (final_score, evidence_list)
        """
        # Collect all evidence
        all_evidence = self.collect_all_evidence(student_id)
        
        # Filter for this skill
        skill_evidence = [
            e for e in all_evidence
            if e.skill_id == str(skill_id)
        ]
        
        if not skill_evidence:
            return 0.0, []
        
        # Calculate weighted score
        total_score = 0.0
        total_weight = 0.0
        
        for evidence in skill_evidence:
            # Base score (0-100)
            base_score = evidence.confidence * 100
            
            # Credibility weight
            credibility = self.CREDIBILITY_WEIGHTS.get(evidence.source_type, 0.5)
            
            # Time decay
            time_decay = self.calculate_time_decay(evidence.date)
            
            # Weighted contribution
            weighted_score = base_score * credibility * time_decay
            
            total_score += weighted_score
            total_weight += credibility
        
        # Final score
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        
        return min(100.0, final_score), skill_evidence
    
    def aggregate_all_skills(self, student_id: uuid.UUID) -> Dict[str, Dict]:
        """
        Calculate scores for all skills a student has evidence for
        
        Args:
            student_id: Student UUID
            
        Returns:
            Dictionary mapping skill_id to score details
        """
        # Collect all evidence
        all_evidence = self.collect_all_evidence(student_id)
        
        # Group by skill
        skills_map = {}
        for evidence in all_evidence:
            if evidence.skill_id not in skills_map:
                skills_map[evidence.skill_id] = {
                    'skill_name': evidence.skill_name,
                    'evidence': []
                }
            skills_map[evidence.skill_id]['evidence'].append(evidence)
        
        # Calculate score for each skill
        results = {}
        for skill_id, data in skills_map.items():
            evidence_list = data['evidence']
            
            # Calculate weighted score
            total_score = 0.0
            total_weight = 0.0
            
            for evidence in evidence_list:
                base_score = evidence.confidence * 100
                credibility = self.CREDIBILITY_WEIGHTS.get(evidence.source_type, 0.5)
                time_decay = self.calculate_time_decay(evidence.date)
                
                weighted_score = base_score * credibility * time_decay
                total_score += weighted_score
                total_weight += credibility
            
            final_score = total_score / total_weight if total_weight > 0 else 0.0
            
            results[skill_id] = {
                'skill_name': data['skill_name'],
                'score': min(100.0, final_score),
                'evidence_count': len(evidence_list),
                'last_updated': max(e.date for e in evidence_list if e.date)
            }
        
        return results
    
    def update_student_skill_scores(self, student_id: uuid.UUID) -> int:
        """
        Update all skill scores for a student in database
        
        Args:
            student_id: Student UUID
            
        Returns:
            Number of skills updated
        """
        # Calculate all scores
        skill_scores = self.aggregate_all_skills(student_id)
        
        # Update or create StudentSkill records
        updated_count = 0
        for skill_id, data in skill_scores.items():
            student_skill = self.db.query(StudentSkill).filter(
                StudentSkill.student_id == student_id,
                StudentSkill.skill_id == uuid.UUID(skill_id)
            ).first()
            
            if student_skill:
                # Update existing
                student_skill.proficiency_score = data['score']
                student_skill.last_assessed = datetime.now()
            else:
                # Create new
                student_skill = StudentSkill(
                    student_id=student_id,
                    skill_id=uuid.UUID(skill_id),
                    proficiency_score=data['score'],
                    last_assessed=datetime.now()
                )
                self.db.add(student_skill)
            
            updated_count += 1
        
        self.db.commit()
        return updated_count
