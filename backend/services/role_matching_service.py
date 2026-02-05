"""
Role Matching Service
Matches students to industry roles based on skill scores
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
import uuid

from models.database_models import IndustryRole, Skill, RoleSkill, StudentRoleMatch
from services.scoring_service import ScoringService

@dataclass
class RoleMatch:
    """Represents a student-role compatibility match"""
    role_id: str
    role_title: str
    company: str
    ctc_range: str
    compatibility_percentage: float
    matched_skills: int
    total_required_skills: int
    missing_mandatory_skills: List[str]
    skill_breakdown: List[Dict]

class RoleMatchingService:
    """
    Match students to roles based on skill proficiency
    """
    
    def __init__(self, db: Session):
        """
        Initialize role matching service
        
        Args:
            db: Database session
        """
        self.db = db
        self.scoring_service = ScoringService(db)
    
    def calculate_compatibility(
        self,
        student_id: uuid.UUID,
        role_id: uuid.UUID
    ) -> Optional[RoleMatch]:
        """
        Calculate compatibility between student and role
        
        Args:
            student_id: Student UUID
            role_id: Role UUID
            
        Returns:
            RoleMatch object or None if disqualified
        """
        # Get role details
        role = self.db.query(IndustryRole).filter(
            IndustryRole.id == role_id
        ).first()
        
        if not role:
            return None
        
        # Get student's skill scores
        student_skills = self.scoring_service.aggregate_all_skills(student_id)
        
        # Get role requirements
        role_skills = self.db.query(RoleSkill, Skill).join(
            Skill, RoleSkill.skill_id == Skill.id
        ).filter(
            RoleSkill.role_id == role_id
        ).all()
        
        if not role_skills:
            return None
        
        # Calculate compatibility
        total_score = 0.0
        total_weight = 0.0
        matched_count = 0
        missing_mandatory = []
        skill_breakdown = []
        
        for role_skill, skill in role_skills:
            # Get student's score for this skill (0 if not found)
            student_score = student_skills.get(str(skill.id), {}).get('score', 0.0)
            
            # Benchmark is the required score for this role
            benchmark = skill.benchmark_score
            
            # Check mandatory skills
            if role_skill.is_mandatory:
                # Must meet at least 80% of benchmark
                min_required = benchmark * 0.8
                
                if student_score < min_required:
                    missing_mandatory.append(skill.skill_name)
                    # Disqualified if any mandatory skill is missing
                    continue
            
            # Calculate skill match percentage
            skill_match = min(student_score / benchmark, 1.0) if benchmark > 0 else 0.0
            
            # Weight for this skill in the role
            skill_weight = role_skill.weight_percentage / 100.0
            
            # Add to totals
            total_score += skill_match * skill_weight
            total_weight += skill_weight
            
            # Track if student meets benchmark
            if student_score >= benchmark:
                matched_count += 1
            
            # Breakdown
            skill_breakdown.append({
                'skill_name': skill.skill_name,
                'student_score': round(student_score, 1),
                'required_score': benchmark,
                'gap': max(0, benchmark - student_score),
                'is_mandatory': role_skill.is_mandatory,
                'meets_requirement': student_score >= benchmark
            })
        
        # Disqualify if missing mandatory skills
        if missing_mandatory:
            return None
        
        # Calculate final compatibility percentage
        compatibility = (total_score / total_weight * 100) if total_weight > 0 else 0.0
        
        return RoleMatch(
            role_id=str(role.id),
            role_title=role.role_title,
            company=role.company,
            ctc_range=role.ctc_range,
            compatibility_percentage=round(compatibility, 2),
            matched_skills=matched_count,
            total_required_skills=len(role_skills),
            missing_mandatory_skills=missing_mandatory,
            skill_breakdown=skill_breakdown
        )
    
    def find_matching_roles(
        self,
        student_id: uuid.UUID,
        min_compatibility: float = 60.0,
        limit: int = 10
    ) -> List[RoleMatch]:
        """
        Find all roles that match student's skills
        
        Args:
            student_id: Student UUID
            min_compatibility: Minimum compatibility percentage
            limit: Maximum number of results
            
        Returns:
            List of RoleMatch objects, sorted by compatibility
        """
        # Get all roles
        roles = self.db.query(IndustryRole).all()
        
        matches = []
        for role in roles:
            match = self.calculate_compatibility(student_id, role.id)
            
            if match and match.compatibility_percentage >= min_compatibility:
                matches.append(match)
        
        # Sort by compatibility (highest first)
        matches.sort(key=lambda x: x.compatibility_percentage, reverse=True)
        
        # Limit results
        return matches[:limit]
    
    def save_role_matches(self, student_id: uuid.UUID, matches: List[RoleMatch]) -> int:
        """
        Save role matches to database
        
        Args:
            student_id: Student UUID
            matches: List of RoleMatch objects
            
        Returns:
            Number of matches saved
        """
        # Delete existing matches for this student
        self.db.query(StudentRoleMatch).filter(
            StudentRoleMatch.student_id == student_id
        ).delete()
        
        # Insert new matches
        saved_count = 0
        for match in matches:
            role_match = StudentRoleMatch(
                student_id=student_id,
                role_id=uuid.UUID(match.role_id),
                compatibility_score=match.compatibility_percentage,
                matched_skills_count=match.matched_skills,
                skill_gap_details={
                    'total_skills': match.total_required_skills,
                    'matched': match.matched_skills,
                    'breakdown': match.skill_breakdown
                }
            )
            self.db.add(role_match)
            saved_count += 1
        
        self.db.commit()
        return saved_count
    
    def get_saved_matches(
        self,
        student_id: uuid.UUID,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get previously calculated role matches from database
        
        Args:
            student_id: Student UUID
            limit: Maximum results
            
        Returns:
            List of match dictionaries
        """
        matches = self.db.query(StudentRoleMatch, IndustryRole).join(
            IndustryRole, StudentRoleMatch.role_id == IndustryRole.id
        ).filter(
            StudentRoleMatch.student_id == student_id
        ).order_by(
            StudentRoleMatch.compatibility_score.desc()
        ).limit(limit).all()
        
        results = []
        for match, role in matches:
            results.append({
                'role_id': str(role.id),
                'role_title': role.role_title,
                'company': role.company,
                'ctc_range': role.ctc_range,
                'compatibility': round(match.compatibility_score, 2),
                'matched_skills': match.matched_skills_count,
                'total_skills': match.skill_gap_details.get('total_skills', 0),
                'calculated_at': match.calculated_at.isoformat() if match.calculated_at else None
            })
        
        return results
