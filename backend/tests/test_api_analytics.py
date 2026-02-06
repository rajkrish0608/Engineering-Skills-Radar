"""
Integration tests for Analytics API endpoints
"""
import pytest
from fastapi import status


@pytest.mark.integration
class TestAnalyticsAPI:
    def test_get_overview(self, client, sample_student, sample_role):
        """Test GET /api/analytics/overview"""
        response = client.get("/api/analytics/overview")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert 'metrics' in data
        assert 'total_students' in data['metrics']
        assert 'total_roles' in data['metrics']
        assert 'placement_ready_percentage' in data['metrics']
    
    def test_get_skill_distribution(self, client, sample_student_skill):
        """Test GET /api/analytics/skill-distribution"""
        response = client.get("/api/analytics/skill-distribution")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert 'skills' in data
        
        if len(data['skills']) > 0:
            skill = data['skills'][0]
            assert 'skill_name' in skill
            assert 'avg_score' in skill
            assert 'student_count' in skill
    
    def test_get_skill_distribution_with_branch_filter(self, client, sample_student_skill):
        """Test GET /api/analytics/skill-distribution with branch filter"""
        response = client.get("/api/analytics/skill-distribution?branch=CS")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
    
    def test_get_branch_stats(self, client, sample_student):
        """Test GET /api/analytics/branch-stats"""
        response = client.get("/api/analytics/branch-stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert 'branches' in data
        
        if len(data['branches']) > 0:
            branch = data['branches'][0]
            assert 'branch' in branch
            assert 'total_students' in branch
            assert 'avg_cgpa' in branch
            assert 'placement_ready_percentage' in branch
    
    def test_get_role_demand_stats(self, client, sample_role):
        """Test GET /api/analytics/role-demand"""
        response = client.get("/api/analytics/role-demand")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert 'roles' in data
        
        if len(data['roles']) > 0:
            role = data['roles'][0]
            assert 'role_title' in role
            assert 'qualified_students' in role
            assert 'highly_qualified' in role
    
    def test_get_top_students(self, client, sample_student_skill):
        """Test GET /api/analytics/top-students"""
        response = client.get("/api/analytics/top-students?limit=5")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert 'students' in data
        
        if len(data['students']) > 0:
            student = data['students'][0]
            assert 'student_id' in student
            assert 'full_name' in student
            assert 'avg_skill_score' in student
            assert 'skill_count' in student
    
    def test_export_students_csv(self, client, sample_student):
        """Test GET /api/analytics/export/students"""
        response = client.get("/api/analytics/export/students")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers['content-type'] == 'text/csv; charset=utf-8'
        assert 'attachment' in response.headers['content-disposition']
        
        # Check CSV content
        csv_content = response.text
        assert 'Roll Number' in csv_content  # Header
        assert 'Full Name' in csv_content
