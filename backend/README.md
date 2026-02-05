# Engineering Skills Radar - Backend

FastAPI backend for the Engineering Skills Radar system.

## Features

### Phase 2: Data Ingestion Pipeline ✅
- **CSV Import System**
  - 5 CSV templates (students, courses, projects, certifications, internships)
  - Comprehensive validation with field-specific rules
  - Error reporting with row-level details
  - Provider credibility weighting for certifications
  
- **File Storage**
  - MinIO/S3 support for document uploads
  - Presigned URLs for secure access
  - Automatic folder organization by category and date
  - Support for PDF, DOCX, CSV, XLSX files
  
- **API Endpoints**
  - `/api/ingestion/csv/validate` - Validate CSV files
  - `/api/ingestion/csv/import` - Import validated data
  - `/api/ingestion/files/upload` - Upload documents
  - `/api/ingestion/files/list` - List uploaded files
  - `/api/ingestion/templates/download` - Download CSV templates

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database and storage credentials
```

### 3. Set Up MinIO (Optional, for local development)

```bash
# Using Docker
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```

### 4. Run Database Migrations

```bash
# Ensure PostgreSQL is running
cd ../database
./init_database.sh
```

### 5. Start the Server

```bash
cd ../backend
python main.py
```

Server will start at: http://localhost:8000

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── main.py                    # FastAPI application entry
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── api/
│   └── ingestion.py          # Data ingestion endpoints
├── services/
│   ├── csv_upload_service.py # CSV validation service
│   └── file_storage_service.py # MinIO/S3 storage service
├── utils/
│   └── database.py           # Database connection
├── models/                    # SQLAlchemy models (Phase 7)
└── data_templates/           # CSV import templates
    ├── README.md
    ├── students_template.csv
    ├── student_courses_template.csv
    ├── projects_template.csv
    ├── certifications_template.csv
    └── internships_template.csv
```

## CSV Import Usage

### 1. Download Template

```bash
curl http://localhost:8000/api/ingestion/templates/download?template_type=students \
  -o students.csv
```

### 2. Validate CSV

```bash
curl -X POST http://localhost:8000/api/ingestion/csv/validate \
  -F "file=@students.csv" \
  -F "upload_type=students"
```

### 3. Import Data

```bash
curl -X POST http://localhost:8000/api/ingestion/csv/import \
  -F "file=@students.csv" \
  -F "upload_type=students" \
  -F "skip_duplicates=true"
```

## File Upload Usage

### Upload Document

```bash
curl -X POST http://localhost:8000/api/ingestion/files/upload \
  -F "file=@project_report.pdf" \
  -F "category=projects" \
  -F "student_roll=2021CS001" \
  -F "description=Final year project report"
```

### List Files

```bash
curl http://localhost:8000/api/ingestion/files/list?category=projects
```

## Development

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .
```

## Environment Variables

See `.env.example` for all available configuration options.

### Required Variables
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `SECRET_KEY` (generate with: `openssl rand -hex 32`)
- `STORAGE_TYPE` (`minio` or `s3`)
- `MINIO_ENDPOINT` or AWS credentials

## Next Phases

- **Phase 3**: Skill Extraction Engine (NLP)
- **Phase 4**: Scoring Engine (Role matching)
- **Phase 5**: Student Frontend (React dashboard)
- **Phase 6**: TPO Dashboard
- **Phase 7**: Backend API Development (CRUD operations)

## Support

For issues or questions, refer to:
- API Documentation: `/api/docs`
- CSV Templates README: `data_templates/README.md`
- Database Setup: `../database/README.md`
