"""
Role Matching Service
Calculates student-role compatibility and gap analysis
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from models.database_models import IndustryRole, StudentRoleMatch, StudentSkill, Student
from services.skill_service import SkillService


class RoleService:
    """Service for role management and matching"""
    
    @staticmethod
    def get_all_roles(
        db: Session,
        category: Optional[str] = None,
        branch: Optional[str] = None
    ) -> List[IndustryRole]:
        """
        Get all roles with optional filters
        
        Args:
            db: Database session
            category: Filter by role category
            branch: Filter by branch eligibility
        
        Returns:
            List of roles
        """
        query = db.query(IndustryRole)
        
        if category:
            query = query.filter(IndustryRole.role_category == category)
        if branch:
            query = query.filter(IndustryRole.eligible_branches.contains([branch]))
        
        return query.all()
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: uuid.UUID) -> Optional[IndustryRole]:
        """Get role by ID"""
        return db.query(IndustryRole).filter(IndustryRole.id == role_id).first()
    
    @staticmethod
    def calculate_role_match(
        db: Session,
        student_id: uuid.UUID,
        role_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Calculate match score between student and role
        
        Algorithm:
        1. Get student skills with scores
        2. Get role required skills with min scores and weights
        3. Calculate weighted match score
        4. Identify missing/weak skills
        
        Returns:
            Dictionary with match_score and missing_skills
        """
        # Get student skills
        student_skills = db.query(StudentSkill).options(
            joinedload(StudentSkill.skill)
        ).filter(StudentSkill.student_id == student_id).all()
        
        student_skill_map = {
            str(ss.skill.skill_name): ss.weighted_score
            for ss in student_skills
        }
        
        # Get role requirements
        role = db.query(IndustryRole).filter(IndustryRole.id == role_id).first()
        if not role:
            return {'error': 'Role not found'}
        
        required_skills = role.required_skills  # JSONB list
        
        # Calculate match score
        total_weight = 0
        weighted_score = 0
        missing_skills = []
        
        for req_skill in required_skills:
            skill_name = req_skill.get('skill_name')
            min_score = req_skill.get('min_score', 70)
            mandatory = req_skill.get('mandatory', False)
            weight = req_skill.get('weight', 0.25)
            
            student_score = student_skill_map.get(skill_name, 0)
            
            if student_score >= min_score:
                # Skill meets requirement
                weighted_score += (student_score / 100) * weight
            else:
                # Skill gap
                gap = min_score - student_score
                missing_skills.append({
                    'skill_name': skill_name,
                    'current_score': student_score,
                    'required_score': min_score,
                    'gap': gap,
                    'mandatory': mandatory
                })
                
                # Partial credit for non-mandatory skills
                if not mandatory and student_score > 0:
                    weighted_score += (student_score / 100) * weight * 0.5
            
            total_weight += weight
        
        # Normalize to 0-100 scale
        match_score = (weighted_score / total_weight * 100) if total_weight > 0 else 0
        
        # Sort missing skills by gap (largest first)
        missing_skills.sort(key=lambda x: x['gap'], reverse=True)
        
        return {
            'match_score': round(match_score, 2),
            'missing_skills': missing_skills,
            'total_required_skills': len(required_skills),
            'matched_skills': len(required_skills) - len(missing_skills)
        }
    
    @staticmethod
    def match_student_to_roles(
        db: Session,
        student_id: uuid.UUID,
        top_n: int = 10,
        save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Match student to all roles and return top N
        
        Args:
            db: Database session
            student_id: Student ID
            top_n: Number of top matches to return
            save_to_db: Whether to cache results in database
        
        Returns:
            List of role matches sorted by score
        """
        # Get student for branch filtering
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return []
        
        # Get roles eligible for student's branch
        roles = db.query(IndustryRole).filter(
            IndustryRole.eligible_branches.contains([student.branch])
        ).all()
        
        role_matches = []
        
        for role in roles:
            match_result = RoleService.calculate_role_match(db, student_id, role.id)
            
            role_matches.append({
                'role_id': str(role.id),
                'role_title': role.role_title,
                'role_category': role.role_category,
                'match_score': match_result['match_score'],
                'missing_skills': match_result['missing_skills'],
                'avg_ctc': float(role.avg_ctc) if role.avg_ctc else None,
                'demand_score': role.demand_score,
                'typical_companies': role.typical_companies
            })
        
        # Sort by match score (descending)
        role_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Save top matches to database if requested
        if save_to_db:
            # Delete existing matches
            db.query(StudentRoleMatch).filter(
                StudentRoleMatch.student_id == student_id
            ).delete()
            
            # Save new matches
            for match in role_matches[:top_n]:
                db_match = StudentRoleMatch(
                    student_id=student_id,
                    role_id=uuid.UUID(match['role_id']),
                    match_score=match['match_score'],
                    missing_skills=match['missing_skills'],
                    calculated_at=datetime.now()
                )
                db.add(db_match)
            
            db.commit()
        
        return role_matches[:top_n]
    
    @staticmethod
    def get_role_gaps(
        db: Session,
        student_id: uuid.UUID,
        role_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get detailed gap analysis for a student-role combination
        
        Returns:
            Dictionary with current readiness, gaps, and recommendations
        """
        match_result = RoleService.calculate_role_match(db, student_id, role_id)
        role = db.query(IndustryRole).filter(IndustryRole.id == role_id).first()
        
        if not role:
            return {'error': 'Role not found'}
        
        # Prioritize gaps (mandatory first, then by gap size)
        gaps = match_result['missing_skills']
        mandatory_gaps = [g for g in gaps if g['mandatory']]
        optional_gaps = [g for g in gaps if not g['mandatory']]
        
        return {
            'role_title': role.role_title,
            'current_readiness': match_result['match_score'],
            'ready_for_role': match_result['match_score'] >= 70,  # 70% threshold
            'mandatory_gaps': mandatory_gaps,
            'optional_gaps': optional_gaps,
            'total_gaps': len(gaps),
            'recommendations': RoleService.generate_recommendations(mandatory_gaps + optional_gaps)
        }
    
    @staticmethod
    def generate_recommendations(gaps: List[Dict[str, Any]]) -> List[str]:
        """
        Generate improvement recommendations based on skill gaps
        
        Args:
            gaps: List of skill gaps
        
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        for gap in gaps[:5]:  # Top 5 gaps
            skill_name = gap['skill_name']
            gap_size = gap['gap']
            
            if gap_size >= 30:
                recommendations.append(
                    f"Priority: Improve {skill_name} (gap: {gap_size} points). "
                    f"Consider taking focused courses or certification."
                )
            elif gap_size >= 15:
                recommendations.append(
                    f"Recommended: Strengthen {skill_name} (gap: {gap_size} points). "
                    f"Practice with mini-projects or tutorials."
                )
            else:
                recommendations.append(
                    f"Minor gap in {skill_name} ({gap_size} points). "
                    f"Review key concepts to meet requirement."
                )
        
        return recommendations
