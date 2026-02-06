import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Paper,
    Typography,
    Box,
    Chip,
    Button,
    Alert,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Stepper,
    Step,
    StepLabel,
    Breadcrumbs,
    Link as MuiLink,
    List,
    ListItem,
    ListItemIcon,
    ListItemText
} from '@mui/material';
import {
    CloudUpload,
    ArrowBack,
    NavigateNext,
    CheckCircle,
    Error as ErrorIcon
} from '@mui/icons-material';
import apiClient from '@/services/apiClient';

interface StudentData {
    roll_number: string;
    full_name: string;
    email: string;
    branch: string;
    batch_year: number;
    current_semester: number;
    cgpa: number;
}

const BulkImportPage: React.FC = () => {
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [activeStep, setActiveStep] = useState(0);
    const [parsedData, setParsedData] = useState<StudentData[]>([]);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<{ created: number; total: number; errors: any[] } | null>(null);
    const [error, setError] = useState('');

    const steps = ['Select File', 'Preview Data', 'Upload & Process'];

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            parseCSV(selectedFile);
        }
    };

    const parseCSV = (file: File) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const text = e.target?.result as string;
                const lines = text.split('\n');

                // Assuming first row is header
                const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]+/g, ''));

                const data: StudentData[] = [];

                for (let i = 1; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (!line) continue;

                    const values = line.split(',').map(v => v.trim().replace(/['"]+/g, ''));

                    // Basic mapping - in a real app, you'd want more robust validation/mapping
                    if (values.length === headers.length) {
                        const student: any = {};

                        headers.forEach((header, index) => {
                            let value: any = values[index];

                            // Type conversion based on field
                            if (header === 'batch_year' || header === 'current_semester') {
                                value = parseInt(value, 10);
                            } else if (header === 'cgpa') {
                                value = parseFloat(value);
                            }

                            student[header] = value;
                        });

                        data.push(student as StudentData);
                    }
                }

                setParsedData(data);
                if (data.length > 0) {
                    setActiveStep(1);
                    setError('');
                } else {
                    setError('No valid data found in CSV.');
                }
            } catch (err) {
                console.error('CSV Parse Error', err);
                setError('Failed to parse CSV file. Please check format.');
            }
        };
        reader.readAsText(file);
    };

    const handleUpload = async () => {
        setUploading(true);
        setActiveStep(2);

        try {
            const response = await apiClient.post<any>('/api/bulk/import-students', parsedData);
            setResult({
                created: response.created_count,
                total: response.total_rows,
                errors: response.errors || []
            });
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Import failed. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    const handleReset = () => {
        setParsedData([]);
        setResult(null);
        setActiveStep(0);
        setError('');
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Navigation */}
            <Box sx={{ mb: 3 }}>
                <Button
                    startIcon={<ArrowBack />}
                    onClick={() => navigate('/tpo/students')}
                    sx={{ mb: 2 }}
                >
                    Back to Student List
                </Button>
                <Breadcrumbs separator={<NavigateNext fontSize="small" />}>
                    <MuiLink underline="hover" color="inherit" onClick={() => navigate('/tpo')} sx={{ cursor: 'pointer' }}>
                        TPO Dashboard
                    </MuiLink>
                    <MuiLink underline="hover" color="inherit" onClick={() => navigate('/tpo/students')} sx={{ cursor: 'pointer' }}>
                        Students
                    </MuiLink>
                    <Typography color="text.primary">Bulk Import</Typography>
                </Breadcrumbs>
            </Box>

            <Paper sx={{ p: 4 }}>
                <Typography variant="h5" gutterBottom fontWeight="bold">
                    Bulk Student Import
                </Typography>
                <Stepper activeStep={activeStep} sx={{ py: 3, mb: 4 }}>
                    {steps.map((label) => (
                        <Step key={label}>
                            <StepLabel>{label}</StepLabel>
                        </Step>
                    ))}
                </Stepper>

                {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                        {error}
                    </Alert>
                )}

                {/* Step 1: File Selection */}
                {activeStep === 0 && (
                    <Box sx={{ textAlign: 'center', py: 4, border: '2px dashed #ccc', borderRadius: 2 }}>
                        <CloudUpload sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" gutterBottom>
                            Drag and drop or select a CSV file
                        </Typography>
                        <input
                            accept=".csv"
                            style={{ display: 'none' }}
                            id="raised-button-file"
                            type="file"
                            onChange={handleFileChange}
                            ref={fileInputRef}
                        />
                        <label htmlFor="raised-button-file">
                            <Button variant="contained" component="span" size="large">
                                Browse File
                            </Button>
                        </label>
                        <Box sx={{ mt: 4, textAlign: 'left', maxWidth: 600, mx: 'auto' }}>
                            <Typography variant="subtitle2" gutterBottom>Required Columns:</Typography>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {['roll_number', 'full_name', 'email', 'branch', 'batch_year', 'current_semester', 'cgpa'].map(col => (
                                    <Chip key={col} label={col} size="small" variant="outlined" />
                                ))}
                            </Box>
                            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                                <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                                    roll_number,full_name,email,branch,batch_year,current_semester,cgpa<br />
                                    CS21001,John Doe,john@example.com,CS,2021,6,8.5
                                </Typography>
                            </Box>
                        </Box>
                    </Box>
                )}

                {/* Step 2: Preview */}
                {activeStep === 1 && (
                    <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                            <Typography variant="h6">
                                Preview ({parsedData.length} records)
                            </Typography>
                            <Box>
                                <Button onClick={handleReset} sx={{ mr: 1 }}>Cancel</Button>
                                <Button variant="contained" onClick={handleUpload} startIcon={<CloudUpload />}>
                                    Upload & Import
                                </Button>
                            </Box>
                        </Box>

                        <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
                            <Table stickyHeader size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Roll No</TableCell>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Email</TableCell>
                                        <TableCell>Branch</TableCell>
                                        <TableCell>Year</TableCell>
                                        <TableCell>Sem</TableCell>
                                        <TableCell>CGPA</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {parsedData.slice(0, 10).map((row, index) => (
                                        <TableRow key={index}>
                                            <TableCell>{row.roll_number}</TableCell>
                                            <TableCell>{row.full_name}</TableCell>
                                            <TableCell>{row.email}</TableCell>
                                            <TableCell>{row.branch}</TableCell>
                                            <TableCell>{row.batch_year}</TableCell>
                                            <TableCell>{row.current_semester}</TableCell>
                                            <TableCell>{row.cgpa}</TableCell>
                                        </TableRow>
                                    ))}
                                    {parsedData.length > 10 && (
                                        <TableRow>
                                            <TableCell colSpan={7} align="center">
                                                ... and {parsedData.length - 10} more rows
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Box>
                )}

                {/* Step 3: Result */}
                {activeStep === 2 && (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                        {uploading ? (
                            <Box>
                                <CircularProgress size={60} sx={{ mb: 2 }} />
                                <Typography variant="h6">Processing Import...</Typography>
                                <Typography color="text.secondary">This may take a few moments.</Typography>
                            </Box>
                        ) : result ? (
                            <Box>
                                <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
                                <Typography variant="h4" gutterBottom>
                                    Import Complete
                                </Typography>
                                <Typography variant="h6" color="text.secondary" gutterBottom>
                                    Successfully imported {result.created} of {result.total} students
                                </Typography>

                                {result.errors.length > 0 && (
                                    <Box sx={{ mt: 4, textAlign: 'left', maxWidth: 800, mx: 'auto' }}>
                                        <Alert severity="warning" sx={{ mb: 2 }}>
                                            {result.errors.length} records were skipped due to errors:
                                        </Alert>
                                        <Paper variant="outlined" sx={{ maxHeight: 200, overflow: 'auto', p: 0 }}>
                                            <List dense>
                                                {result.errors.map((err, idx) => (
                                                    <ListItem key={idx}>
                                                        <ListItemIcon>
                                                            <ErrorIcon color="error" fontSize="small" />
                                                        </ListItemIcon>
                                                        <ListItemText
                                                            primary={`Row ${err.row} (Roll: ${err.roll_number})`}
                                                            secondary={err.error}
                                                            secondaryTypographyProps={{ color: 'error' }}
                                                        />
                                                    </ListItem>
                                                ))}
                                            </List>
                                        </Paper>
                                    </Box>
                                )}

                                <Box sx={{ mt: 4 }}>
                                    <Button variant="outlined" onClick={handleReset} sx={{ mr: 2 }}>
                                        Import More
                                    </Button>
                                    <Button variant="contained" onClick={() => navigate('/tpo/students')}>
                                        View Student List
                                    </Button>
                                </Box>
                            </Box>
                        ) : null}
                    </Box>
                )}
            </Paper>
        </Container>
    );
};

export default BulkImportPage;
