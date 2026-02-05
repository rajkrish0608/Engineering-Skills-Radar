# CSV Import Templates

This folder contains CSV templates for bulk data import into the Engineering Skills Radar system.

## Available Templates

### 1. `students_template.csv`
Import student basic information.

**Required Fields:**
- Roll Number (unique identifier)
- Full Name
- Email (unique)
- Branch (CS, Mechanical, Civil, Electrical, ECE)
- Batch Year (e.g., 2021)
- Current Semester (1-8)
- CGPA (0.00-10.00)

---

### 2. `student_courses_template.csv`
Import semester-wise course records and marks.

**Required Fields:**
- Roll Number (must exist in students)
- Course Code
- Course Name
- Semester (1-8)
- Grade (A+, A, B+, B, C, D, F)
- Marks (0-100)

**Note:** System will extract skills from course names automatically.

---

### 3. `projects_template.csv`
Import student project portfolios.

**Required Fields:**
- Roll Number
- Project Title
- Project Abstract (detailed description for skill extraction)
- Project Type (Academic, Personal, Internship)
- Semester
- Tech Stack (comma-separated)

**Tip:** Include detailed abstracts with technical keywords for better skill extraction.

---

### 4. `certifications_template.csv`
Import external certifications.

**Required Fields:**
- Roll Number
- Certification Title
- Provider (Coursera, Udemy, NPTEL, Google, AWS, etc.)
- Completion Date (YYYY-MM-DD)
- Certificate URL (optional)

**Provider Credibility Weights:**
- Coursera, edX, NPTEL: 0.9
- Udacity, LinkedIn Learning: 0.85
- Udemy, Pluralsight: 0.7
- Internal certificates: 0.6

---

### 5. `internships_template.csv`
Import internship experience (optional).

**Required Fields:**
- Roll Number
- Company Name
- Role Title
- Duration (Months)
- Description
- Skills Used (comma-separated in quotes)
- Start Date (YYYY-MM-DD)
- End Date (YYYY-MM-DD)

---

## Usage Instructions

### 1. Download Template
Download the appropriate template CSV file.

### 2. Fill Data
- Use Excel, Google Sheets, or any CSV editor
- Follow the field requirements strictly
- DO NOT modify column headers
- Use UTF-8 encoding

### 3. Validate
Before uploading:
- Check for duplicate roll numbers
- Verify email formats
- Ensure CGPA is between 0-10
- Confirm branch names match exactly

### 4. Upload
- Navigate to Admin Dashboard → Data Import
- Select upload type
- Choose CSV file
- Review validation report
- Confirm import

---

## Common Validation Rules

### Data Constraints
- **Roll Number**: Alphanumeric, max 20 chars, unique
- **Email**: Valid format, unique
- **CGPA**: 0.00 - 10.00
- **Semester**: 1-8
- **Marks**: 0-100
- **Branch**: Must be one of: CS, IT, Mechanical, Civil, Electrical, ECE

### Error Handling
- **Duplicate entries**: System will skip and report
- **Invalid data**: Row rejected with reason
- **Missing required fields**: Row rejected
- **Foreign key errors**: Roll number must exist for related imports

---

## Best Practices

1. **Start with Students**: Always import students first before other data
2. **Incremental Updates**: Import data in batches (100-500 rows)
3. **Backup**: Keep original CSV files for audit
4. **Verification**: Review validation report before confirming
5. **Test First**: Try with 5-10 sample rows before bulk upload

---

## Sample Data

Each template file contains sample data showing:
- Expected formats
- Real-world examples
- Multiple branches
- Various scenarios

**Remove or replace sample data before importing to production.**

---

## Need Help?

- **Invalid CSV**: Ensure UTF-8 encoding, no special characters in headers
- **Upload Failed**: Check file size (<10MB), format (.csv only)
- **Validation Errors**: See error report for specific row issues
- **Contact**: Reach out to system admin for assistance
