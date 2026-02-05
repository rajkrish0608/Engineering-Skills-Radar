# Engineering Skills Radar Database Setup

## Prerequisites
- PostgreSQL 15 or higher
- Command-line access (Terminal/PowerShell)

## Quick Start

### 1. Install PostgreSQL

**macOS** (using Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql-15 postgresql-contrib
sudo systemctl start postgresql
```

**Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE engineering_skills_radar;

# Create user (optional)
CREATE USER esr_admin WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE engineering_skills_radar TO esr_admin;

# Exit
\q
```

### 3. Initialize Schema

```bash
cd engineering-skills-radar/database

# Run schema creation
psql -d engineering_skills_radar -f schema.sql

# Seed skills taxonomy (28 skills)
psql -d engineering_skills_radar -f seed_skills.sql

# Seed industry roles (15 roles)
psql -d engineering_skills_radar -f seed_roles.sql
```

### 4. Verify Installation

```bash
# Connect to database
psql -d engineering_skills_radar

# Check tables
\dt

# Check skills count (should be 28)
SELECT COUNT(*) FROM skills;

# Check roles count (should be 15)
SELECT COUNT(*) FROM industry_roles;

# View sample skills
SELECT skill_name, skill_category, branches FROM skills LIMIT 5;

# View sample roles
SELECT role_title, role_category, avg_ctc FROM industry_roles LIMIT 5;
```

## Database Structure

### Core Tables (16)
1. **students** - Student records with branch, CGPA
2. **courses** - Course catalog
3. **skills** - 28 skill taxonomy
4. **student_skills** - Student skill scores with evidence
5. **industry_roles** - 15 role definitions
6. **student_role_matches** - Cached role match scores
7. **skill_assessments** - Quiz/project/cert submissions
8. **student_courses** - Student course enrollments
9. **projects** - Student project portfolio
10. **certifications** - External certifications
11. **internships** - Internship records
12. **users** - TPO/Faculty/Admin accounts
13. **audit_logs** - Complete audit trail
14. **skill_mapping_overrides** - Manual corrections

### Key Features
- **JSONB fields** for flexible skill/role data
- **Foreign key constraints** with cascading deletes
- **CHECK constraints** for data validation (CGPA 0-10, scores 0-100)
- **Indexes** on student_id, skill_id, branch for performance
- **Audit triggers** for updated_at timestamps

## Configuration

### Environment Variables
Create `.env` file in backend directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=engineering_skills_radar
DB_USER=esr_admin
DB_PASSWORD=your_secure_password

# Connection Pool
DB_POOL_MIN=2
DB_POOL_MAX=10
```

## Backup & Restore

### Backup
```bash
pg_dump engineering_skills_radar > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
psql engineering_skills_radar < backup_20260205.sql
```

## Troubleshooting

### Connection Issues
```bash
# Check if PostgreSQL is running
pg_isready

# Check service status
brew services list  # macOS
sudo systemctl status postgresql  # Linux
```

### Permission Errors
```bash
# Grant permissions on all tables
psql -d engineering_skills_radar -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO esr_admin;"
```

### Reset Database
```bash
# Drop and recreate
psql postgres -c "DROP DATABASE engineering_skills_radar;"
psql postgres -c "CREATE DATABASE engineering_skills_radar;"

# Re-run setup
psql -d engineering_skills_radar -f schema.sql
psql -d engineering_skills_radar -f seed_skills.sql
psql -d engineering_skills_radar -f seed_roles.sql
```

## Next Steps
After database setup:
1. Configure backend connection in FastAPI
2. Run database migrations (if any)
3. Test CRUD operations
4. Proceed to Phase 2: Data Ingestion Pipeline
