"""
CSV Upload and Validation Service
Handles bulk data import with validation and error reporting
"""
import pandas as pd
import io
from typing import List, Dict, Any, Tuple
from datetime import datetime
import re

class CSVValidationError(Exception):
    """Custom exception for CSV validation errors"""
    pass

class CSVUploadService:
    """
    Service for uploading and validating CSV files
    """
    
    # Define required columns for each upload type
    REQUIRED_COLUMNS = {
        'students': ['Roll Number', 'Full Name', 'Email', 'Branch', 'Batch Year', 'Current Semester', 'CGPA'],
        'courses': ['Roll Number', 'Course Code', 'Course Name', 'Semester', 'Grade', 'Marks'],
        'projects': ['Roll Number', 'Project Title', 'Project Abstract', 'Project Type', 'Semester', 'Tech Stack'],
        'certifications': ['Roll Number', 'Certification Title', 'Provider', 'Completion Date', 'Certificate URL'],
        'internships': ['Roll Number', 'Company Name', 'Role Title', 'Duration (Months)', 'Description', 'Skills Used', 'Start Date', 'End Date']
    }
    
    # Valid values for specific fields
    VALID_BRANCHES = ['CS', 'IT', 'Mechanical', 'Civil', 'Electrical', 'ECE']
    VALID_GRADES = ['A+', 'A', 'B+', 'B', 'C', 'D', 'F']
    VALID_PROJECT_TYPES = ['Academic', 'Personal', 'Internship']
    
    def __init__(self, max_rows: int = 1000):
        self.max_rows = max_rows
        self.validation_errors = []
    
    def read_csv(self, file_content: bytes, upload_type: str) -> pd.DataFrame:
        """
        Read and parse CSV file
        
        Args:
            file_content: Raw CSV file bytes
            upload_type: Type of upload (students, courses, etc.)
        
        Returns:
            DataFrame with parsed CSV data
        
        Raises:
            CSVValidationError: If CSV format is invalid
        """
        try:
            # Read CSV into DataFrame
            df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
            
            # Check row limit
            if len(df) > self.max_rows:
                raise CSVValidationError(f"CSV exceeds maximum allowed rows ({self.max_rows})")
            
            # Validate required columns
            required_cols = self.REQUIRED_COLUMNS.get(upload_type, [])
            missing_cols = set(required_cols) - set(df.columns)
            
            if missing_cols:
                raise CSVValidationError(f"Missing required columns: {', '.join(missing_cols)}")
            
            return df
        
        except pd.errors.ParserError as e:
            raise CSVValidationError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            raise CSVValidationError(f"Error reading CSV: {str(e)}")
    
    def validate_students(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate student records
        
        Returns:
            Tuple of (valid_records, error_records)
        """
        valid_records = []
        error_records = []
        
        for idx, row in df.iterrows():
            errors = []
            
            # Validate Roll Number (alphanumeric, max 20 chars)
            if not re.match(r'^[A-Za-z0-9]{1,20}$', str(row['Roll Number'])):
                errors.append("Invalid roll number format")
            
            # Validate Email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(row['Email'])):
                errors.append("Invalid email format")
            
            # Validate Branch
            if row['Branch'] not in self.VALID_BRANCHES:
                errors.append(f"Invalid branch. Must be one of: {', '.join(self.VALID_BRANCHES)}")
            
            # Validate Current Semester (1-8)
            try:
                semester = int(row['Current Semester'])
                if semester < 1 or semester > 8:
                    errors.append("Semester must be between 1 and 8")
            except (ValueError, TypeError):
                errors.append("Invalid semester value")
            
            # Validate CGPA (0-10)
            try:
                cgpa = float(row['CGPA'])
                if cgpa < 0 or cgpa > 10:
                    errors.append("CGPA must be between 0.00 and 10.00")
            except (ValueError, TypeError):
                errors.append("Invalid CGPA value")
            
            if errors:
                error_records.append({
                    'row': idx + 2,  # +2 for header row and 0-indexing
                    'data': row.to_dict(),
                    'errors': errors
                })
            else:
                valid_records.append(row.to_dict())
        
        return valid_records, error_records
    
    def validate_courses(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate course records
        """
        valid_records = []
        error_records = []
        
        for idx, row in df.iterrows():
            errors = []
            
            # Validate Semester (1-8)
            try:
                semester = int(row['Semester'])
                if semester < 1 or semester > 8:
                    errors.append("Semester must be between 1 and 8")
            except (ValueError, TypeError):
                errors.append("Invalid semester value")
            
            # Validate Grade
            if row['Grade'] not in self.VALID_GRADES:
                errors.append(f"Invalid grade. Must be one of: {', '.join(self.VALID_GRADES)}")
            
            # Validate Marks (0-100)
            try:
                marks = int(row['Marks'])
                if marks < 0 or marks > 100:
                    errors.append("Marks must be between 0 and 100")
            except (ValueError, TypeError):
                errors.append("Invalid marks value")
            
            if errors:
                error_records.append({
                    'row': idx + 2,
                    'data': row.to_dict(),
                    'errors': errors
                })
            else:
                valid_records.append(row.to_dict())
        
        return valid_records, error_records
    
    def validate_projects(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate project records
        """
        valid_records = []
        error_records = []
        
        for idx, row in df.iterrows():
            errors = []
            
            # Validate Project Type
            if row['Project Type'] not in self.VALID_PROJECT_TYPES:
                errors.append(f"Invalid project type. Must be one of: {', '.join(self.VALID_PROJECT_TYPES)}")
            
            # Validate abstract length (minimum 50 characters for meaningful extraction)
            if len(str(row['Project Abstract'])) < 50:
                errors.append("Project abstract too short (minimum 50 characters)")
            
            # Validate Semester (1-8)
            try:
                semester = int(row['Semester'])
                if semester < 1 or semester > 8:
                    errors.append("Semester must be between 1 and 8")
            except (ValueError, TypeError):
                errors.append("Invalid semester value")
            
            if errors:
                error_records.append({
                    'row': idx + 2,
                    'data': row.to_dict(),
                    'errors': errors
                })
            else:
                valid_records.append(row.to_dict())
        
        return valid_records, error_records
    
    def validate_certifications(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate certification records
        """
        valid_records = []
        error_records = []
        
        for idx, row in df.iterrows():
            errors = []
            
            # Validate Completion Date
            try:
                datetime.strptime(str(row['Completion Date']), '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD")
            
            if errors:
                error_records.append({
                    'row': idx + 2,
                    'data': row.to_dict(),
                    'errors': errors
                })
            else:
                # Assign provider credibility
                provider = row['Provider'].lower()
                if any(p in provider for p in ['coursera', 'edx', 'nptel']):
                    row['credibility'] = 0.9
                elif any(p in provider for p in ['udacity', 'linkedin']):
                    row['credibility'] = 0.85
                elif any(p in provider for p in ['udemy', 'pluralsight']):
                    row['credibility'] = 0.7
                else:
                    row['credibility'] = 0.6
                
                valid_records.append(row.to_dict())
        
        return valid_records, error_records
    
    def validate_internships(self, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate internship records
        """
        valid_records = []
        error_records = []
        
        for idx, row in df.iterrows():
            errors = []
            
            # Validate dates
            try:
                start_date = datetime.strptime(str(row['Start Date']), '%Y-%m-%d')
                end_date = datetime.strptime(str(row['End Date']), '%Y-%m-%d')
                
                if end_date <= start_date:
                    errors.append("End date must be after start date")
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD")
            
            # Validate duration
            try:
                duration = int(row['Duration (Months)'])
                if duration < 1 or duration > 24:
                    errors.append("Duration must be between 1 and 24 months")
            except (ValueError, TypeError):
                errors.append("Invalid duration value")
            
            if errors:
                error_records.append({
                    'row': idx + 2,
                    'data': row.to_dict(),
                    'errors': errors
                })
            else:
                valid_records.append(row.to_dict())
        
        return valid_records, error_records
    
    def validate_upload(self, file_content: bytes, upload_type: str) -> Dict[str, Any]:
        """
        Main validation method
        
        Returns:
            Dictionary with validation results
        """
        # Read CSV
        df = self.read_csv(file_content, upload_type)
        
        # Route to appropriate validator
        validators = {
            'students': self.validate_students,
            'courses': self.validate_courses,
            'projects': self.validate_projects,
            'certifications': self.validate_certifications,
            'internships': self.validate_internships
        }
        
        validator = validators.get(upload_type)
        if not validator:
            raise CSVValidationError(f"Unknown upload type: {upload_type}")
        
        valid_records, error_records = validator(df)
        
        return {
            'upload_type': upload_type,
            'total_rows': len(df),
            'valid_count': len(valid_records),
            'error_count': len(error_records),
            'valid_records': valid_records,
            'error_records': error_records,
            'success_rate': round((len(valid_records) / len(df)) * 100, 2) if len(df) > 0 else 0
        }
