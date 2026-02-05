#!/bin/bash

# ================================================================
# Engineering Skills Radar - Database Initialization Script
# Purpose: Automated database setup for development environment
# ================================================================

set -e  # Exit on error

echo "🚀 Engineering Skills Radar - Database Setup"
echo "=============================================="

# Configuration
DB_NAME="engineering_skills_radar"
DB_USER="esr_admin"
DB_PASSWORD="${DB_PASSWORD:-esr_secure_2026}"  # Use env var or default

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not installed${NC}"
    echo "Please install PostgreSQL 15+ first:"
    echo "  macOS:  brew install postgresql@15"
    echo "  Linux:  sudo apt install postgresql-15"
    exit 1
fi

echo -e "${GREEN}✓ PostgreSQL found${NC}"

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo -e "${YELLOW}⚠ PostgreSQL is not running. Starting...${NC}"
    
    # Try to start based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql@15
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start postgresql
    fi
    
    sleep 2
    
    if ! pg_isready -q; then
        echo -e "${RED}❌ Could not start PostgreSQL${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ PostgreSQL is running${NC}"

# Drop existing database if it exists (development only!)
echo -e "${YELLOW}📋 Checking for existing database...${NC}"
if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    read -p "Database '$DB_NAME' already exists. Drop and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Dropping existing database..."
        psql postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
        echo -e "${GREEN}✓ Dropped existing database${NC}"
    else
        echo "Aborting. Please manually drop the database or use a different name."
        exit 1
    fi
fi

# Create database
echo "📦 Creating database '$DB_NAME'..."
psql postgres -c "CREATE DATABASE $DB_NAME;"
echo -e "${GREEN}✓ Database created${NC}"

# Create user (if not exists)
echo "👤 Creating database user '$DB_USER'..."
psql postgres -c "DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;"
echo -e "${GREEN}✓ User created/verified${NC}"

# Grant privileges
echo "🔐 Granting privileges..."
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
echo -e "${GREEN}✓ Privileges granted${NC}"

# Run schema
echo "📐 Creating database schema..."
psql -d "$DB_NAME" -f schema.sql > /dev/null
echo -e "${GREEN}✓ Schema created (16 tables)${NC}"

# Seed skills
echo "🧠 Seeding skills taxonomy (28 skills)..."
psql -d "$DB_NAME" -f seed_skills.sql > /dev/null
SKILL_COUNT=$(psql -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM skills;")
echo -e "${GREEN}✓ Inserted $SKILL_COUNT skills${NC}"

# Seed roles
echo "💼 Seeding industry roles (15 roles)..."
psql -d "$DB_NAME" -f seed_roles.sql > /dev/null
ROLE_COUNT=$(psql -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM industry_roles;")
echo -e "${GREEN}✓ Inserted $ROLE_COUNT roles${NC}"

# Grant table permissions to user
echo "🔓 Granting table permissions..."
psql -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
psql -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
echo -e "${GREEN}✓ Table permissions granted${NC}"

# Verification
echo ""
echo "🧪 Running verification tests..."
echo "================================"

# Test 1: Check table count
TABLE_COUNT=$(psql -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
if [ "$TABLE_COUNT" -eq 16 ]; then
    echo -e "${GREEN}✓ All 16 tables created${NC}"
else
    echo -e "${RED}❌ Expected 16 tables, found $TABLE_COUNT${NC}"
fi

# Test 2: Sample skills
echo ""
echo "Sample Skills:"
psql -d "$DB_NAME" -c "SELECT skill_name, skill_category, branches FROM skills LIMIT 3;" -P pager=off

# Test 3: Sample roles
echo ""
echo "Sample Roles:"
psql -d "$DB_NAME" -c "SELECT role_title, role_category, avg_ctc FROM industry_roles LIMIT 3;" -P pager=off

# Create .env file
echo ""
echo "📝 Creating .env configuration file..."
cat > .env << EOF
# Engineering Skills Radar - Database Configuration
# Generated on $(date)

DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Connection Pool Settings
DB_POOL_MIN=2
DB_POOL_MAX=10

# Environment
ENVIRONMENT=development
EOF

echo -e "${GREEN}✓ .env file created${NC}"

# Success message
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Database setup complete!${NC}"
echo "=============================================="
echo ""
echo "Database Name: $DB_NAME"
echo "Database User: $DB_USER"
echo "Skills Loaded: $SKILL_COUNT"
echo "Roles Loaded:  $ROLE_COUNT"
echo ""
echo "📚 Next steps:"
echo "  1. Update backend/.env with database credentials"
echo "  2. Test database connection"
echo "  3. Proceed to Phase 2: Data Ingestion"
echo ""
echo "🔗 Connect to database:"
echo "  psql -d $DB_NAME"
echo ""
