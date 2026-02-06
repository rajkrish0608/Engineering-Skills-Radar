"""
Pytest configuration and fixtures for backend tests
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import datetime
import uuid

from models.database_models import Base, Student, Skill, IndustryRole, StudentSkill
from main import app
from utils.database import get_db


# Test database configuration
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal()
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_student(test_db):
    """Create a sample student for testing"""
    student = Student(
        roll_number="CS001",
        full_name="Test Student",
        email="test@example.com",
        branch="CS",
        graduation_year=2024,
        cgpa=8.5
    )
    test_db.add(student)
    test_db.commit()
    test_db.refresh(student)
    return student


@pytest.fixture
def sample_skill(test_db):
    """Create a sample skill for testing"""
    skill = Skill(
        skill_name="Python",
        skill_category="Core Technical",
        benchmark_score=70.0,
        applicable_branches=["CS", "IT"]
    )
    test_db.add(skill)
    test_db.commit()
    test_db.refresh(skill)
    return skill


@pytest.fixture
def sample_role(test_db):
    """Create a sample industry role for testing"""
    role = IndustryRole(
        role_title="Software Engineer",
        role_category="Software",
        description="Entry level software engineering role",
        required_skills=[
            {
                "skill_name": "Python",
                "min_score": 70,
                "mandatory": True,
                "weight": 0.4
            },
            {
                "skill_name": "SQL",
                "min_score": 60,
                "mandatory": False,
                "weight": 0.3
            }
        ],
        eligible_branches=["CS", "IT"],
        avg_ctc=800000.0,
        demand_score=75,
        typical_companies=["Google", "Microsoft"]
    )
    test_db.add(role)
    test_db.commit()
    test_db.refresh(role)
    return role


@pytest.fixture
def sample_student_skill(test_db, sample_student, sample_skill):
    """Create a student skill record"""
    student_skill = StudentSkill(
        student_id=sample_student.id,
        skill_id=sample_skill.id,
        proficiency_score=75.0,
        weighted_score=75.0,
        confidence_score=0.85,
        last_updated=datetime.now()
    )
    test_db.add(student_skill)
    test_db.commit()
    test_db.refresh(student_skill)
    return student_skill
