"""
Unit tests for RoleService
"""
import pytest
from services.role_service import RoleService
from models.database_models import IndustryRole, StudentSkill, Skill
import uuid


@pytest.mark.unit
class TestRoleService:
    def test_create_role(self, test_db):
        """Test creating a new role"""
        role_data = {
            'role_title': 'Backend Developer',
            'role_category': 'Software',
            'description': 'Backend development role',
            'required_skills': [
                {'skill_name': 'Python', 'min_score': 70, 'mandatory': True, 'weight': 0.4}
            ],
            'eligible_branches': ['CS', 'IT'],
            'avg_ctc': 900000.0,
            'demand_score': 80
        }
        
        role = RoleService.create_role(test_db, role_data)
        
        assert role.role_title == 'Backend Developer'
        assert role.role_category == 'Software'
        assert len(role.required_skills) == 1
        assert role.avg_ctc == 900000.0
    
    def test_get_role_by_id(self, test_db, sample_role):
        """Test retrieving a role by ID"""
        role = RoleService.get_role_by_id(test_db, sample_role.id)
        
        assert role is not None
        assert role.role_title == sample_role.role_title
        assert role.id == sample_role.id
    
    def test_get_all_roles(self, test_db, sample_role):
        """Test getting all roles"""
        roles = RoleService.get_all_roles(test_db)
        
        assert len(roles) >= 1
        assert any(r.role_title == 'Software Engineer' for r in roles)
    
    def test_get_all_roles_with_category_filter(self, test_db, sample_role):
        """Test filtering roles by category"""
        roles = RoleService.get_all_roles(test_db, category='Software')
        
        assert len(roles) >= 1
        assert all(r.role_category == 'Software' for r in roles)
    
    def test_update_role(self, test_db, sample_role):
        """Test updating a role"""
        update_data = {
            'role_title': 'Senior Software Engineer',
            'avg_ctc': 1200000.0
        }
        
        updated_role = RoleService.update_role(test_db, sample_role.id, update_data)
        
        assert updated_role.role_title == 'Senior Software Engineer'
        assert updated_role.avg_ctc == 1200000.0
    
    def test_delete_role(self, test_db, sample_role):
        """Test deleting a role"""
        role_id = sample_role.id
        result = RoleService.delete_role(test_db, role_id)
        
        assert result is True
        
        # Verify role was deleted
        deleted_role = RoleService.get_role_by_id(test_db, role_id)
        assert deleted_role is None
    
    def test_calculate_role_match_perfect_match(self, test_db, sample_student, sample_role):
        """Test role matching with perfect skill match"""
        # Add Python skill to student
        python_skill = Skill(
            skill_name="Python",
            skill_category="Core Technical",
            benchmark_score=70.0
        )
        test_db.add(python_skill)
        test_db.commit()
        
        student_skill = StudentSkill(
            student_id=sample_student.id,
            skill_id=python_skill.id,
            proficiency_score=90.0,
            weighted_score=90.0
        )
        test_db.add(student_skill)
        
        # Add SQL skill
        sql_skill = Skill(
            skill_name="SQL",
            skill_category="Core Technical",
            benchmark_score=60.0
        )
        test_db.add(sql_skill)
        test_db.commit()
        
        student_sql = StudentSkill(
            student_id=sample_student.id,
            skill_id=sql_skill.id,
            proficiency_score=80.0,
            weighted_score=80.0
        )
        test_db.add(student_sql)
        test_db.commit()
        
        # Calculate match
        match_result = RoleService.calculate_role_match(test_db, sample_student.id, sample_role.id)
        
        assert 'match_score' in match_result
        assert match_result['match_score'] > 70  # Should have high match
        assert len(match_result['missing_skills']) == 0  # No missing skills
    
    def test_calculate_role_match_with_gaps(self, test_db, sample_student, sample_role):
        """Test role matching with skill gaps"""
        # Add only Python skill with lower score
        python_skill = Skill(
            skill_name="Python",
            skill_category="Core Technical",
            benchmark_score=70.0
        )
        test_db.add(python_skill)
        test_db.commit()
        
        student_skill = StudentSkill(
            student_id=sample_student.id,
            skill_id=python_skill.id,
            proficiency_score=50.0,  # Below requirement
            weighted_score=50.0
        )
        test_db.add(student_skill)
        test_db.commit()
        
        # Calculate match
        match_result = RoleService.calculate_role_match(test_db, sample_student.id, sample_role.id)
        
        assert 'match_score' in match_result
        assert match_result['match_score'] < 50  # Should have low match
        assert len(match_result['missing_skills']) > 0  # Should have gaps
        
        # Check gap details
        python_gap = next((g for g in match_result['missing_skills'] if g['skill_name'] == 'Python'), None)
        assert python_gap is not None
        assert python_gap['gap'] == 20  # 70 - 50
        assert python_gap['mandatory'] is True
    
    def test_get_role_gaps(self, test_db, sample_student, sample_role):
        """Test gap analysis"""
        # Add incomplete skills
        python_skill = Skill(
            skill_name="Python",
            skill_category="Core Technical",
            benchmark_score=70.0
        )
        test_db.add(python_skill)
        test_db.commit()
        
        student_skill = StudentSkill(
            student_id=sample_student.id,
            skill_id=python_skill.id,
            proficiency_score=60.0,
            weighted_score=60.0
        )
        test_db.add(student_skill)
        test_db.commit()
        
        gap_analysis = RoleService.get_role_gaps(test_db, sample_student.id, sample_role.id)
        
        assert 'current_readiness' in gap_analysis
        assert 'mandatory_gaps' in gap_analysis
        assert 'optional_gaps' in gap_analysis
        assert 'recommendations' in gap_analysis
        assert gap_analysis['ready_for_role'] is False  # Below 70% threshold
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        gaps = [
            {'skill_name': 'Python', 'gap': 40, 'mandatory': True},
            {'skill_name': 'SQL', 'gap': 20, 'mandatory': False},
            {'skill_name': 'Git', 'gap': 10, 'mandatory': False}
        ]
        
        recommendations = RoleService.generate_recommendations(gaps)
        
        assert len(recommendations) == 3
        assert 'Priority' in recommendations[0]  # Large gap
        assert 'Recommended' in recommendations[1]  # Medium gap
        assert 'Minor' in recommendations[2]  # Small gap
