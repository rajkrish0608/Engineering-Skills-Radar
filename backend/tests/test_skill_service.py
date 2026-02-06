"""
Unit tests for SkillService
"""
import pytest
from services.skill_service import SkillService
from models.database_models import (
    Skill, StudentSkill, Project, Certification, 
    Course, Internship, Assessment
)
from datetime import datetime, timedelta


@pytest.mark.unit
class TestSkillService:
    def test_calculate_time_decay(self):
        """Test time decay calculation"""
        # Recent activity (0 months old)
        recent_date = datetime.now()
        recent_decay = SkillService._calculate_time_decay(recent_date)
        assert recent_decay == 1.0  # No decay
        
        # 12 months old
        old_date = datetime.now() - timedelta(days=365)
        old_decay = SkillService._calculate_time_decay(old_date)
        assert old_decay == 0.8  # 20% decay
        
        # 24 months old
        very_old_date = datetime.now() - timedelta(days=730)
        very_old_decay = SkillService._calculate_time_decay(very_old_date)
        assert very_old_decay == 0.6  # 40% decay
    
    def test_calculate_credibility_weight_certification(self):
        """Test credibility weighting for certifications"""
        # High credibility provider
        high_weight = SkillService._calculate_credibility_weight('certification', 'AWS')
        assert high_weight >= 0.9
        
        # Medium credibility provider
        medium_weight = SkillService._calculate_credibility_weight('certification', 'Coursera')
        assert 0.7 <= medium_weight < 0.9
        
        # Unknown provider
        low_weight = SkillService._calculate_credibility_weight('certification', 'Unknown Provider')
        assert low_weight == 0.6
    
    def test_calculate_credibility_weight_evidence_types(self):
        """Test credibility weights for different evidence types"""
        assert SkillService._calculate_credibility_weight('project') == 0.8
        assert SkillService._calculate_credibility_weight('course') == 0.7
        assert SkillService._calculate_credibility_weight('internship') == 0.9
        assert SkillService._calculate_credibility_weight('assessment') == 1.0
    
    def test_aggregate_skill_evidence(self, test_db, sample_student, sample_skill):
        """Test evidence aggregation for a skill"""
        # Add project evidence
        project = Project(
            student_id=sample_student.id,
            title="Python Web App",
            description="Built with Django and Python",
            tech_stack=["Python", "Django"],
            extracted_skills=[{"skill_name": "Python", "confidence": 0.9}],
            completion_date=datetime.now()
        )
        test_db.add(project)
        
        # Add certification evidence
        cert = Certification(
            student_id=sample_student.id,
            certification_name="Python Expert",
            provider="Coursera",
            skills_mapped=["Python"],
            issue_date=datetime.now()
        )
        test_db.add(cert)
        test_db.commit()
        
        evidence = SkillService.aggregate_skill_evidence(test_db, sample_student.id, "Python")
        
        assert len(evidence) >= 2
        assert any(e['source'] == 'project' for e in evidence)
        assert any(e['source'] == 'certification' for e in evidence)
    
    def test_calculate_skill_score_single_evidence(self, test_db, sample_student):
        """Test skill score calculation with single piece of evidence"""
        # Create assessment
        skill = Skill(
            skill_name="JavaScript",
            skill_category="Core Technical",
            benchmark_score=70.0
        )
        test_db.add(skill)
        test_db.commit()
        
        assessment = Assessment(
            student_id=sample_student.id,
            skill_id=skill.id,
            score=85.0,
            assessment_type="mcq",
            completed_at=datetime.now()
        )
        test_db.add(assessment)
        test_db.commit()
        
        score_data = SkillService.calculate_skill_score(test_db, sample_student.id, skill.id)
        
        assert score_data['proficiency_score'] == 85.0  # Same as assessment
        assert score_data['confidence_score'] == 1.0  # Assessment has max credibility
        assert 'evidence_count' in score_data
    
    def test_calculate_skill_score_multiple_evidence(self, test_db, sample_student):
        """Test skill score with multiple evidence sources"""
        skill = Skill(
            skill_name="React",
            skill_category="Tools",
            benchmark_score=65.0
        )
        test_db.add(skill)
        test_db.commit()
        
        # Add project
        project = Project(
            student_id=sample_student.id,
            title="React Dashboard",
            tech_stack=["React"],
            extracted_skills=[{"skill_name": "React", "confidence": 0.8}],
            completion_date=datetime.now()
        )
        test_db.add(project)
        
        # Add course
        course = Course(
            student_id=sample_student.id,
            course_name="React Fundamentals",
            skills_mapped=["React"],
            completion_date=datetime.now()
        )
        test_db.add(course)
        test_db.commit()
        
        score_data = SkillService.calculate_skill_score(test_db, sample_student.id, skill.id)
        
        assert score_data['proficiency_score'] > 0
        assert score_data['evidence_count'] >= 2
        assert 0 < score_data['confidence_score'] <= 1.0
    
    def test_recalculate_student_skills(self, test_db, sample_student, sample_skill):
        """Test bulk recalculation of all student skills"""
        # Add evidence
        project = Project(
            student_id=sample_student.id,
            title="Data Analysis",
            tech_stack=["Python"],
            extracted_skills=[{"skill_name": "Python", "confidence": 0.9}],
            completion_date=datetime.now()
        )
        test_db.add(project)
        test_db.commit()
        
        result = SkillService.recalculate_student_skills(test_db, sample_student.id)
        
        assert result['status'] == 'success'
        assert result['skills_updated'] >= 0
    
    def test_get_skill_statistics(self, test_db, sample_skill, sample_student_skill):
        """Test skill statistics generation"""
        stats = SkillService.get_skill_statistics(test_db, sample_skill.id)
        
        assert 'skill_name' in stats
        assert 'avg_proficiency' in stats
        assert 'student_count' in stats
        assert stats['student_count'] >= 1
