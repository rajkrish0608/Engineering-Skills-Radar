import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Paper,
    Typography,
    Box,
    Grid,
    TextField,
    Button,
    MenuItem,
    Stepper,
    Step,
    StepLabel,
    Card,
    CardContent,
    FormControl,
    InputLabel,
    Select,
    CircularProgress,
    Alert,
    Chip,
    Divider
} from '@mui/material';
import {
    Assignment,
    School,
    Code,
    CheckCircle,
    ArrowBack
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/services/apiClient';

interface Skill {
    id: string;
    skill_name: string;
    category: string;
}

interface ExtractedSkill {
    skill_id: string;
    skill_name: string;
    confidence: number;
    evidence?: string;
}

const AssessmentPage: React.FC = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    // State
    const [activeStep, setActiveStep] = useState(0);
    const [assessmentType, setAssessmentType] = useState('quiz'); // quiz, project, certification
    const [selectedSkill, setSelectedSkill] = useState('');
    const [skills, setSkills] = useState<Skill[]>([]);

    // Form Data
    const [projectDesc, setProjectDesc] = useState('');
    const [certTitle, setCertTitle] = useState('');
    const [certProvider, setCertProvider] = useState('');
    const [quizScore, setQuizScore] = useState(0);

    // Processing State
    const [loading, setLoading] = useState(false);
    const [extracting, setExtracting] = useState(false);
    const [extractedSkills, setExtractedSkills] = useState<ExtractedSkill[]>([]);
    const [submissionResult, setSubmissionResult] = useState<any>(null);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchSkills();
    }, []);

    const fetchSkills = async () => {
        try {
            const response = await apiClient.get<any>('/api/skills/');
            setSkills(response.skills || []);
        } catch (err) {
            console.error('Failed to fetch skills', err);
        }
    };

    const handleNext = () => setActiveStep((prev) => prev + 1);
    const handleBack = () => setActiveStep((prev) => prev - 1);

    const handleProjectExtraction = async () => {
        if (!projectDesc) return;

        try {
            setExtracting(true);
            const response = await apiClient.post<any>('/api/skills/extract/project', {
                project_description: projectDesc,
                student_id: user?.id
            });
            setExtractedSkills(response.skills || []);
            handleNext();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Extraction failed');
        } finally {
            setExtracting(false);
        }
    };

    const handleCertExtraction = async () => {
        if (!certTitle) return;

        try {
            setExtracting(true);
            const response = await apiClient.post<any>('/api/skills/extract/certification', {
                certification_title: certTitle,
                provider: certProvider,
                student_id: user?.id
            });
            setExtractedSkills(response.skills || []);
            handleNext();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Extraction failed');
        } finally {
            setExtracting(false);
        }
    };

    const submitAssessment = async () => {
        if (!user?.id || !selectedSkill) return;

        try {
            setLoading(true);

            // For Quiz, we submit the score directly
            // For Project/Cert, we confirm the extracted skills

            let payload;

            if (assessmentType === 'quiz') {
                payload = {
                    student_id: user.id,
                    skill_id: selectedSkill,
                    assessment_type: 'quiz',
                    score: quizScore,
                    metadata: { type: 'self_assessment' }
                };
            } else {
                // For extraction types, we create assessments for all found skills
                // But the API currently takes one skill at a time.
                // For simplicity in this demo, we'll just submit the PRIMARY selected skill
                // In a real app, we would loop through extractedSkills

                // Find if selected skill was in extracted list (optional validation)

                payload = {
                    student_id: user.id,
                    skill_id: selectedSkill,
                    assessment_type: assessmentType,
                    score: 85, // Default high score for verified evidence
                    metadata: {
                        source_text: assessmentType === 'project' ? projectDesc : certTitle,
                        extracted_count: extractedSkills.length
                    }
                };
            }

            const response = await apiClient.post<any>('/api/skills/assessments', payload);
            setSubmissionResult(response.assessment);
            handleNext();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Submission failed');
        } finally {
            setLoading(false);
        }
    };

    // --- Render Steps ---

    const renderTypeSelection = () => (
        <Grid container spacing={3}>
            {[
                { id: 'quiz', title: 'Skill Quiz', icon: <Assignment fontSize="large" />, desc: 'Take a quick quiz to verify your knowledge' },
                { id: 'project', title: 'Project Evidence', icon: <Code fontSize="large" />, desc: 'Analyze a project description to find skills' },
                { id: 'certification', title: 'Certification', icon: <School fontSize="large" />, desc: 'Upload a certification to validate skills' }
            ].map((type) => (
                <Grid item xs={12} md={4} key={type.id}>
                    <Card
                        sx={{
                            cursor: 'pointer',
                            border: assessmentType === type.id ? '2px solid #1976d2' : '1px solid #eee',
                            bgcolor: assessmentType === type.id ? 'primary.50' : 'background.paper',
                            height: '100%'
                        }}
                        onClick={() => setAssessmentType(type.id)}
                    >
                        <CardContent sx={{ textAlign: 'center', py: 4 }}>
                            <Box sx={{ color: assessmentType === type.id ? 'primary.main' : 'text.secondary', mb: 2 }}>
                                {type.icon}
                            </Box>
                            <Typography variant="h6" fontWeight="bold" gutterBottom>{type.title}</Typography>
                            <Typography variant="body2" color="text.secondary">{type.desc}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );

    const renderInputForm = () => {
        switch (assessmentType) {
            case 'quiz':
                return (
                    <Box sx={{ maxWidth: 600, mx: 'auto' }}>
                        <FormControl fullWidth sx={{ mb: 3 }}>
                            <InputLabel>Select Skill to Assess</InputLabel>
                            <Select
                                value={selectedSkill}
                                label="Select Skill to Assess"
                                onChange={(e) => setSelectedSkill(e.target.value)}
                            >
                                {skills.map((s) => (
                                    <MenuItem key={s.id} value={s.id}>{s.skill_name} ({s.category})</MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                        {selectedSkill && (
                            <Paper variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
                                <Typography gutterBottom>Mock Quiz Interface</Typography>
                                <Typography variant="caption" display="block" color="text.secondary" sx={{ mb: 3 }}>
                                    (In a real implementation, 10 MCQs would appear here)
                                </Typography>

                                <Typography gutterBottom>Simulate Score:</Typography>
                                <TextField
                                    type="number"
                                    value={quizScore}
                                    onChange={(e) => setQuizScore(Number(e.target.value))}
                                    inputProps={{ min: 0, max: 100 }}
                                    sx={{ width: 100, mb: 2 }}
                                />
                                <Box>
                                    <Button variant="contained" onClick={submitAssessment} disabled={loading}>
                                        Submit Quiz Score
                                    </Button>
                                </Box>
                            </Paper>
                        )}
                    </Box>
                );

            case 'project':
                return (
                    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
                        <Typography gutterBottom>
                            Paste your project abstract or description. Our AI will identify the skills used.
                        </Typography>
                        <TextField
                            fullWidth
                            multiline
                            rows={6}
                            placeholder="e.g., Built a weather app using React and Node.js..."
                            value={projectDesc}
                            onChange={(e) => setProjectDesc(e.target.value)}
                            sx={{ mb: 3 }}
                        />
                        <Button
                            variant="contained"
                            onClick={handleProjectExtraction}
                            disabled={!projectDesc || extracting}
                            startIcon={extracting && <CircularProgress size={20} />}
                        >
                            Analyze Project
                        </Button>
                    </Box>
                );

            case 'certification':
                return (
                    <Box sx={{ maxWidth: 600, mx: 'auto' }}>
                        <TextField
                            fullWidth
                            label="Certification Title"
                            value={certTitle}
                            onChange={(e) => setCertTitle(e.target.value)}
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            fullWidth
                            label="Provider (e.g., Coursera, Udemy)"
                            value={certProvider}
                            onChange={(e) => setCertProvider(e.target.value)}
                            sx={{ mb: 3 }}
                        />
                        <Button
                            variant="contained"
                            onClick={handleCertExtraction}
                            disabled={!certTitle || extracting}
                            startIcon={extracting && <CircularProgress size={20} />}
                        >
                            Verify Certification
                        </Button>
                    </Box>
                );
            default:
                return null;
        }
    };

    const renderVerification = () => (
        <Box sx={{ maxWidth: 800, mx: 'auto' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
                Analysis Results
            </Typography>
            <Alert severity="success" sx={{ mb: 3 }}>
                We found {extractedSkills.length} skills in your submission!
            </Alert>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 4 }}>
                {extractedSkills.map((skill, index) => (
                    <Chip
                        key={index}
                        label={`${skill.skill_name} (${Math.round(skill.confidence * 100)}%)`}
                        color="primary"
                        variant="outlined"
                    />
                ))}
            </Box>

            <Typography gutterBottom>Select the primary skill to credit this evidence towards:</Typography>
            <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Select Primary Skill</InputLabel>
                <Select
                    value={selectedSkill}
                    label="Select Primary Skill"
                    onChange={(e) => setSelectedSkill(e.target.value)}
                >
                    {extractedSkills.map((es) => {
                        // Find matching ID from all skills list if possible, or use extracted ID
                        const match = skills.find(s => s.skill_name.toLowerCase() === es.skill_name.toLowerCase());
                        const skillId = match ? match.id : es.skill_id;
                        return (
                            <MenuItem key={skillId} value={skillId}>
                                {es.skill_name}
                            </MenuItem>
                        );
                    })}
                    <Divider />
                    <MenuItem disabled value=""><em>Other Skills</em></MenuItem>
                    {skills.map((s) => (
                        <MenuItem key={s.id} value={s.id}>{s.skill_name}</MenuItem>
                    ))}
                </Select>
            </FormControl>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button onClick={handleBack}>Back</Button>
                <Button variant="contained" onClick={submitAssessment} disabled={loading || !selectedSkill}>
                    Confirm & Submit
                </Button>
            </Box>
        </Box>
    );

    const renderSuccess = () => (
        <Box sx={{ textAlign: 'center', py: 5 }}>
            <CheckCircle color="success" sx={{ fontSize: 80, mb: 2 }} />
            <Typography variant="h4" fontWeight="bold" gutterBottom>
                Assessment Submitted!
            </Typography>
            <Box sx={{ mb: 4 }}>
                <Typography color="text.secondary">
                    Your skill score has been updated.
                </Typography>
                {submissionResult && (
                    <Typography variant="h5" color="primary" sx={{ mt: 2, fontWeight: 'bold' }}>
                        Score Recorded: {submissionResult.score}%
                    </Typography>
                )}
            </Box>
            <Button variant="contained" onClick={() => navigate('/dashboard')}>
                Return to Dashboard
            </Button>
        </Box>
    );

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
            <Button startIcon={<ArrowBack />} onClick={() => navigate('/dashboard')} sx={{ mb: 3 }}>
                Dashboard
            </Button>

            <Paper elevation={2} sx={{ p: 4 }}>
                <Typography variant="h4" fontWeight="bold" gutterBottom align="center">
                    Skill Assessment Center
                </Typography>
                <Typography align="center" color="text.secondary" sx={{ mb: 6 }}>
                    Validate your skills through quizzes, projects, and certifications.
                </Typography>

                <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 6 }}>
                    <Step><StepLabel>Select Method</StepLabel></Step>
                    <Step><StepLabel>Provide Details</StepLabel></Step>
                    <Step><StepLabel>Verify Results</StepLabel></Step>
                    <Step><StepLabel>Complete</StepLabel></Step>
                </Stepper>

                {error && <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError('')}>{error}</Alert>}

                <Box sx={{ mt: 4 }}>
                    {activeStep === 0 && (
                        <>
                            {renderTypeSelection()}
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
                                <Button variant="contained" onClick={handleNext}>Next</Button>
                            </Box>
                        </>
                    )}

                    {activeStep === 1 && (
                        <>
                            <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                                {assessmentType === 'quiz' ? 'Take Quiz' :
                                    assessmentType === 'project' ? 'Project Details' : 'Certification Details'}
                            </Typography>
                            {renderInputForm()}
                            {assessmentType !== 'quiz' && (
                                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mt: 2 }}>
                                    <Button onClick={handleBack}>Back</Button>
                                </Box>
                            )}
                        </>
                    )}

                    {activeStep === 2 && renderVerification()}

                    {activeStep === 3 && renderSuccess()}
                </Box>
            </Paper>
        </Container>
    );
};

export default AssessmentPage;
