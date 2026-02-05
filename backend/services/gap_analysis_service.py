"""
Gap Analysis Service
Identifies skill gaps and provides recommendations
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
import uuid

from models.database_models import IndustryRole, Skill, RoleSkill, Certification
from services.scoring_service import ScoringService

@dataclass
class SkillGap:
    """Represents a skill gap for a target role"""
    skill_id: str
    skill_name: str
    current_score: float
    required_score: float
    gap: float
    priority: str  # 'Critical', 'High', 'Medium', 'Low'
    is_mandatory: bool

class GapAnalysisService:
    """
    Analyze skill gaps and provide recommendations
    """
    
    def __init__(self, db: Session):
        """
        Initialize gap analysis service
        
        Args:
            db: Database session
        """
        self.db = db
        self.scoring_service = ScoringService(db)
    
    def analyze_role_gap(
        self,
        student_id: uuid.UUID,
        role_id: uuid.UUID
    ) -> Dict:
        """
        Analyze skill gaps for a specific role
        
        Args:
            student_id: Student UUID
            role_id: Role UUID
            
        Returns:
            Gap analysis dictionary
        """
        # Get role details
        role = self.db.query(IndustryRole).filter(
            IndustryRole.id == role_id
        ).first()
        
        if not role:
            return {'error': 'Role not found'}
        
        # Get student's skill scores
        student_skills = self.scoring_service.aggregate_all_skills(student_id)
        
        # Get role requirements
        role_skills = self.db.query(RoleSkill, Skill).join(
            Skill, RoleSkill.skill_id == Skill.id
        ).filter(
            RoleSkill.role_id == role_id
        ).all()
        
        gaps = []
        strengths = []
        
        for role_skill, skill in role_skills:
            student_score = student_skills.get(str(skill.id), {}).get('score', 0.0)
            required_score = skill.benchmark_score
            gap_value = max(0, required_score - student_score)
            
            # Determine priority
            if role_skill.is_mandatory and gap_value > 0:
                priority = 'Critical'
            elif gap_value > 30:
                priority = 'High'
            elif gap_value > 15:
                priority = 'Medium'
            else:
                priority = 'Low'
            
            skill_data = {
                'skill_id': str(skill.id),
                'skill_name': skill.skill_name,
                'current_score': round(student_score, 1),
                'required_score': required_score,
                'gap': round(gap_value, 1),
                'priority': priority,
                'is_mandatory': role_skill.is_mandatory
            }
            
            if gap_value > 0:
                gaps.append(skill_data)
            else:
                strengths.append(skill_data)
        
        # Sort gaps by priority
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        gaps.sort(key=lambda x: (priority_order[x['priority']], -x['gap']))
        
        return {
            'role_id': str(role.id),
            'role_title': role.role_title,
            'company': role.company,
            'gaps': gaps,
            'strengths': strengths,
            'total_gaps': len(gaps),
            'total_strengths': len(strengths)
        }
    
    def get_recommendations(
        self,
        student_id: uuid.UUID,
        skill_gaps: List[Dict]
    ) -> Dict:
        """
        Get learning recommendations to fill skill gaps
        
        Args:
            student_id: Student UUID
            skill_gaps: List of skill gap dictionaries
            
        Returns:
            Recommendations dictionary
        """
        cert_recommendations = []
        course_recommendations = []
        
        # For each gap, recommend certifications that teach that skill
        for gap in skill_gaps[:5]:  # Top 5 gaps
            skill_name = gap['skill_name']
            
            # Simple keyword-based certification recommendations
            cert_keywords = {
                'Python': ['Python', 'Programming'],
                'Machine Learning': ['Machine Learning', 'Data Science', 'AI'],
                'Cloud Computing': ['AWS', 'Azure', 'GCP', 'Cloud'],
                'React': ['React', 'JavaScript', 'Frontend'],
                'SQL': ['SQL', 'Database'],
                'Java': ['Java', 'Programming'],
                'CAD Design': ['AutoCAD', 'SolidWorks', 'CAD'],
            }
            
            keywords = cert_keywords.get(skill_name, [skill_name])
            
            for keyword in keywords:
                cert_recommendations.append({
                    'skill': skill_name,
                    'type': 'certification',
                    'title': f'{keyword} Certification',
                    'provider': 'Coursera / Udemy / Official Provider',
                    'priority': gap['priority']
                })
        
        # Remove duplicates
        unique_certs = []
        seen_titles = set()
        for cert in cert_recommendations:
            if cert['title'] not in seen_titles:
                unique_certs.append(cert)
                seen_titles.add(cert['title'])
        
        return {
            'certifications': unique_certs[:5],
            'courses': course_recommendations,
            'projects': [
                {
                    'skill': gap['skill_name'],
                    'suggestion': f"Build a project demonstrating {gap['skill_name']}",
                    'priority': gap['priority']
                }
                for gap in skill_gaps[:3]
            ]
        }
    
    def find_similar_roles(
        self,
        student_id: uuid.UUID,
        current_role_id: uuid.UUID,
        min_compatibility: float = 60.0
    ) -> List[Dict]:
        """
        Find alternative roles with better compatibility
        
        Args:
            student_id: Student UUID
            current_role_id: Current target role
            min_compatibility: Minimum compatibility threshold
            
        Returns:
            List of alternative role suggestions
        """
        from services.role_matching_service import RoleMatchingService
        
        matching_service = RoleMatchingService(self.db)
        
        # Get all matching roles
        all_matches = matching_service.find_matching_roles(
            student_id,
            min_compatibility=min_compatibility
        )
        
        # Filter out current role
        alternatives = [
            {
                'role_id': match.role_id,
                'role_title': match.role_title,
                'company': match.company,
                'ctc_range': match.ctc_range,
                'compatibility': match.compatibility_percentage,
                'matched_skills': match.matched_skills,
                'total_skills': match.total_required_skills
            }
            for match in all_matches
            if match.role_id != str(current_role_id)
        ]
        
        return alternatives[:5]  # Top 5 alternatives
