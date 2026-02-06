"""
Integration tests for Roles API endpoints
"""
import pytest
from fastapi import status


@pytest.mark.integration
class TestRolesAPI:
    def test_get_roles(self, client, sample_role):
        """Test GET /api/roles/"""
        response = client.get("/api/roles/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert 'roles' in data
        assert len(data['roles']) >= 1
    
    def test_get_roles_with_category_filter(self, client, sample_role):
        """Test GET /api/roles/ with category filter"""
        response = client.get("/api/roles/?category=Software")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(r['category'] == 'Software' for r in data['roles'])
    
    def test_get_role_by_id(self, client, sample_role):
        """Test GET /api/roles/{role_id}"""
        response = client.get(f"/api/roles/{sample_role.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert data['role']['role_title'] == sample_role.role_title
    
    def test_get_role_not_found(self, client):
        """Test GET /api/roles/{role_id} with invalid ID"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/roles/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_role(self, client):
        """Test POST /api/roles/"""
        role_data = {
            'role_title': 'Data Scientist',
            'role_category': 'Data',
            'description': 'Data science role',
            'required_skills': [
                {
                    'skill_name': 'Python',
                    'min_score': 75,
                    'mandatory': True,
                    'weight': 0.5
                }
            ],
            'eligible_branches': ['CS', 'IT'],
            'avg_ctc': 1000000,
            'demand_score': 85
        }
        
        response = client.post("/api/roles/", json=role_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert data['role']['role_title'] == 'Data Scientist'
    
    def test_create_role_validation_error(self, client):
        """Test POST /api/roles/ with missing required fields"""
        invalid_data = {
            'role_category': 'Software'
            # Missing role_title
        }
        
        response = client.post("/api/roles/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_role(self, client, sample_role):
        """Test PUT /api/roles/{role_id}"""
        update_data = {
            'role_title': 'Senior Software Engineer',
            'avg_ctc': 1500000
        }
        
        response = client.put(f"/api/roles/{sample_role.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert data['role']['role_title'] == 'Senior Software Engineer'
        assert data['role']['avg_ctc'] == 1500000
    
    def test_delete_role(self, client, sample_role):
        """Test DELETE /api/roles/{role_id}"""
        role_id = str(sample_role.id)
        response = client.delete(f"/api/roles/{role_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        
        # Verify role was deleted
        get_response = client.get(f"/api/roles/{role_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_matched_students(self, client, sample_role, sample_student, test_db):
        """Test GET /api/roles/{role_id}/matched-students"""
        from models.database_models import StudentRoleMatch
        from datetime import datetime
        
        # Create a match
        match = StudentRoleMatch(
            student_id=sample_student.id,
            role_id=sample_role.id,
            compatibility_score=85.0,
            matched_skills_count=2,
            calculated_at=datetime.now()
        )
        test_db.add(match)
        test_db.commit()
        
        response = client.get(f"/api/roles/{sample_role.id}/matched-students")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert len(data['matched_students']) >= 1
        assert data['matched_students'][0]['compatibility'] == 85.0
    
    def test_recalculate_matches(self, client, sample_role, sample_student, test_db):
        """Test POST /api/roles/{role_id}/recalculate-matches"""
        from models.database_models import Skill, StudentSkill
        
        # Add skills to student
        skill = Skill(
            skill_name="Python",
            skill_category="Core Technical",
            benchmark_score=70.0
        )
        test_db.add(skill)
        test_db.commit()
        
        student_skill = StudentSkill(
            student_id=sample_student.id,
            skill_id=skill.id,
            proficiency_score=80.0,
            weighted_score=80.0
        )
        test_db.add(student_skill)
        test_db.commit()
        
        response = client.post(f"/api/roles/{sample_role.id}/recalculate-matches")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert 'message' in data
