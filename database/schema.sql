-- ================================================================
-- ENGINEERING SKILLS RADAR - DATABASE SCHEMA
-- Purpose: Core database structure for skill intelligence system
-- Database: PostgreSQL 15+
-- ================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ================================================================
-- CORE TABLES
-- ================================================================

-- Students Table
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roll_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    branch VARCHAR(50) NOT NULL, -- CS, Mechanical, Civil, Electrical, ECE
    batch_year INTEGER NOT NULL,
    current_semester INTEGER CHECK (current_semester BETWEEN 1 AND 8),
    cgpa DECIMAL(3,2) CHECK (cgpa BETWEEN 0 AND 10),
    account_status VARCHAR(20) DEFAULT 'active', -- active, inactive, graduated
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Courses Table
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    branch VARCHAR(50) NOT NULL,
    semester INTEGER CHECK (semester BETWEEN 1 AND 8),
    credits INTEGER CHECK (credits BETWEEN 1 AND 6),
    course_type VARCHAR(30), -- Theory, Lab, Project, Elective
    syllabus_url TEXT, -- S3 link to syllabus PDF
    created_at TIMESTAMP DEFAULT NOW()
);

-- Skills Table (Taxonomy)
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    skill_category VARCHAR(50) NOT NULL, -- Core Technical, Tools & Software, Applied, Foundational
    description TEXT,
    branches JSONB, -- ["CS", "Mechanical", "All"]
    benchmark_score INTEGER DEFAULT 70 CHECK (benchmark_score BETWEEN 0 AND 100), -- Industry minimum
    created_at TIMESTAMP DEFAULT NOW()
);

-- Student Skills (Actual Scores)
CREATE TABLE student_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    raw_score INTEGER CHECK (raw_score BETWEEN 0 AND 100),
    weighted_score DECIMAL(5,2) CHECK (weighted_score BETWEEN 0 AND 100),
    confidence_level DECIMAL(3,2) CHECK (confidence_level BETWEEN 0 AND 1), -- 0.0 to 1.0
    evidence_sources JSONB, -- [{"type": "quiz", "score": 85}, {"type": "project", "score": 92}]
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, skill_id)
);

-- Industry Roles
CREATE TABLE industry_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_title VARCHAR(100) UNIQUE NOT NULL, -- "SDE-II", "Data Scientist", "Structural Engineer"
    role_category VARCHAR(50), -- Software, Data, Design, Infrastructure
    description TEXT,
    required_skills JSONB NOT NULL, -- [{"skill_id": "uuid", "min_score": 70, "mandatory": true}]
    eligible_branches JSONB, -- ["CS", "IT", "ECE"]
    avg_ctc DECIMAL(10,2), -- 12.5L
    demand_score INTEGER CHECK (demand_score BETWEEN 0 AND 100), -- 85/100
    typical_companies JSONB, -- ["TCS", "Infosys", "Wipro", "Google"]
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Student Role Matches (Cached Scores)
CREATE TABLE student_role_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    role_id UUID REFERENCES industry_roles(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2) CHECK (match_score BETWEEN 0 AND 100),
    missing_skills JSONB, -- [{"skill_id": "uuid", "skill_name": "CAD", "gap": 15}]
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, role_id)
);

-- Skill Assessments
CREATE TABLE skill_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    assessment_type VARCHAR(20) NOT NULL, -- quiz, project, certification, internship, interview
    score INTEGER CHECK (score BETWEEN 0 AND 100),
    metadata JSONB, -- {"cert_provider": "Coursera", "project_title": "ML Model"}
    completed_at TIMESTAMP DEFAULT NOW()
);

-- Student Course Records
CREATE TABLE student_courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    semester_taken INTEGER,
    grade VARCHAR(5), -- A+, A, B+, B, C, F
    marks_obtained INTEGER CHECK (marks_obtained BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, course_id, semester_taken)
);

-- Projects Table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    project_title VARCHAR(200) NOT NULL,
    project_abstract TEXT,
    project_type VARCHAR(30), -- Academic, Personal, Internship
    semester INTEGER,
    tech_stack JSONB, -- ["Python", "TensorFlow", "React"]
    document_url TEXT, -- S3 link
    created_at TIMESTAMP DEFAULT NOW()
);

-- Certifications Table
CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    certification_title VARCHAR(200) NOT NULL,
    provider VARCHAR(100), -- Coursera, Udemy, Google, NPTEL
    provider_credibility DECIMAL(3,2) DEFAULT 0.7 CHECK (provider_credibility BETWEEN 0 AND 1),
    completion_date DATE,
    certificate_url TEXT, -- S3 link
    created_at TIMESTAMP DEFAULT NOW()
);

-- Internships Table
CREATE TABLE internships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    company_name VARCHAR(100),
    role_title VARCHAR(100),
    duration_months INTEGER,
    description TEXT,
    skills_used JSONB, -- ["Python", "AWS", "Django"]
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- ADMIN & AUDIT TABLES
-- ================================================================

-- Users (TPO, Faculty, Admin)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- student, tpo, faculty, admin
    full_name VARCHAR(100),
    department VARCHAR(50), -- For faculty
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL, -- skill_override, role_created, student_uploaded
    entity_type VARCHAR(50), -- student, skill, role
    entity_id UUID,
    changes JSONB, -- {"old": {...}, "new": {...}}
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Skill Mapping Overrides (Manual Corrections)
CREATE TABLE skill_mapping_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    original_score INTEGER,
    overridden_score INTEGER CHECK (overridden_score BETWEEN 0 AND 100),
    overridden_by UUID REFERENCES users(id),
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- INDEXES FOR PERFORMANCE
-- ================================================================

CREATE INDEX idx_students_branch ON students(branch);
CREATE INDEX idx_students_batch ON students(batch_year);
CREATE INDEX idx_student_skills_student ON student_skills(student_id);
CREATE INDEX idx_student_skills_skill ON student_skills(skill_id);
CREATE INDEX idx_student_role_matches_student ON student_role_matches(student_id);
CREATE INDEX idx_student_role_matches_role ON student_role_matches(role_id);
CREATE INDEX idx_skill_assessments_student ON skill_assessments(student_id);
CREATE INDEX idx_courses_branch ON courses(branch);
CREATE INDEX idx_industry_roles_category ON industry_roles(role_category);

-- JSONB indexes for filtering
CREATE INDEX idx_skills_branches ON skills USING GIN (branches);
CREATE INDEX idx_roles_branches ON industry_roles USING GIN (eligible_branches);
CREATE INDEX idx_student_skills_evidence ON student_skills USING GIN (evidence_sources);

-- ================================================================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- ================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_industry_roles_updated_at BEFORE UPDATE ON industry_roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- COMMENTS FOR DOCUMENTATION
-- ================================================================

COMMENT ON TABLE students IS 'Core student information and academic records';
COMMENT ON TABLE skills IS 'Master skill taxonomy across all engineering branches';
COMMENT ON TABLE student_skills IS 'Actual student skill scores with evidence tracking';
COMMENT ON TABLE industry_roles IS 'Industry role definitions with skill requirements';
COMMENT ON TABLE student_role_matches IS 'Cached role match calculations for performance';
COMMENT ON COLUMN student_skills.evidence_sources IS 'Multi-source scoring: quiz 40%, project 35%, cert 25%';
COMMENT ON COLUMN skills.benchmark_score IS 'Industry minimum acceptable score (default 70/100)';
