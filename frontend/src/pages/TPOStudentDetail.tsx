import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container,
    Grid,
    Paper,
    Typography,
    Box,
    Card,
    CardContent,
    LinearProgress,
    Chip,
    Button,
    Alert,
    CircularProgress,
    Breadcrumbs,
    Link as MuiLink
} from '@mui/material';
import {
    AccountCircleOutlined,
    TrendingUpOutlined,
    WorkOutlineOutlined,
    ArrowBack,
    NavigateNext,
    CodeOutlined,
    VerifiedOutlined,
    EmailOutlined,
    School
} from '@mui/icons-material';
import apiClient from '@/services/apiClient';

interface Student {
    id: string;
    roll_number: string;
    full_name: string;
    email: string;
    branch: string;
    batch_year: number;
    current_semester: number;
    cgpa: number;
    account_status: string;
}

interface Skill {
    skill_id: string;
    skill_name: string;
    category: string;
    weighted_score: number;
    confidence: number;
}

interface RoleMatch {
    role_id: string;
    role_title: string;
    role_category: string;
    match_score: number;
    missing_skills: any[];
    avg_ctc?: number;
}

interface Project {
    id: string;
    title: string;
    type: string;
    tech_stack: string[];
    document_url?: string;
}

interface Certification {
    id: string;
    title: string;
    provider: string;
    credibility: number;
    completion_date?: string;
}

const TPOStudentDetail: React.FC = () => {
    const { studentId } = useParams<{ studentId: string }>();
    const navigate = useNavigate();

    const [student, setStudent] = useState<Student | null>(null);
    const [skills, setSkills] = useState<Skill[]>([]);
    const [roleMatches, setRoleMatches] = useState<RoleMatch[]>([]);
    const [projects, setProjects] = useState<Project[]>([]);
    const [certifications, setCertifications] = useState<Certification[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (studentId) {
            fetchStudentDetails();
        }
    }, [studentId]);

    const fetchStudentDetails = async () => {
        try {
            setLoading(true);
            const [studentRes, skillsRes, rolesRes, projectsRes, certsRes] = await Promise.all([
                apiClient.get<any>(`/api/students/${studentId}`),
                apiClient.get<any>(`/api/students/${studentId}/skills`),
                apiClient.get<any>(`/api/students/${studentId}/role-matches?top_n=5`),
                apiClient.get<any>(`/api/students/${studentId}/projects`),
                apiClient.get<any>(`/api/students/${studentId}/certifications`),
            ]);

            setStudent(studentRes.student);
            setSkills(skillsRes.skills || []);
            setRoleMatches(rolesRes.matches || []);
            setProjects(projectsRes.projects || []);
            setCertifications(certsRes.certifications || []);
        } catch (err: any) {
            console.error('Failed to load student details', err);
            setError('Failed to load student details');
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number): string => {
        if (score >= 80) return 'success.main';
        if (score >= 60) return 'warning.main';
        return 'error.main';
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    if (error || !student) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <Alert severity="error" action={
                    <Button color="inherit" size="small" onClick={() => navigate('/tpo/students')}>
                        Back to List
                    </Button>
                }>
                    {error || 'Student not found'}
                </Alert>
            </Container>
        );
    }

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
                    <Typography color="text.primary">Profile</Typography>
                </Breadcrumbs>
            </Box>

            {/* Profile Header */}
            <Paper elevation={3} sx={{ p: 4, mb: 4, borderRadius: 2 }}>
                <Grid container spacing={3} alignItems="center">
                    <Grid item xs={12} md={8}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <AccountCircleOutlined sx={{ fontSize: 60, color: 'primary.main', mr: 2 }} />
                            <Box>
                                <Typography variant="h4" fontWeight="bold">
                                    {student.full_name}
                                </Typography>
                                <Typography variant="h6" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                                    {student.roll_number}
                                </Typography>
                            </Box>
                        </Box>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 2, ml: 1 }}>
                            <Chip icon={<School />} label={`${student.branch} • Sem ${student.current_semester}`} />
                            <Chip icon={<EmailOutlined />} label={student.email} />
                            <Chip label={`CGPA: ${student.cgpa}`} color={student.cgpa >= 7.5 ? "success" : "default"} variant="outlined" />
                            <Chip label={student.account_status} color={student.account_status === 'Active' ? 'success' : 'default'} size="small" />
                        </Box>
                    </Grid>
                    <Grid item xs={12} md={4} sx={{ textAlign: { xs: 'left', md: 'right' } }}>
                        <Button variant="contained" color="primary" sx={{ mr: 1 }}>
                            Update Status
                        </Button>
                        <Button variant="outlined" color="secondary">
                            Export Report
                        </Button>
                    </Grid>
                </Grid>
            </Paper>

            <Grid container spacing={3}>
                {/* Stats */}
                <Grid item xs={12} md={4}>
                    <Card elevation={2} sx={{ height: '100%' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <TrendingUpOutlined sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                                <Box>
                                    <Typography variant="h3" fontWeight="bold">
                                        {skills.length}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Skills Tracked
                                    </Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Card elevation={2} sx={{ height: '100%' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <WorkOutlineOutlined sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                                <Box>
                                    <Typography variant="h3" fontWeight="bold">
                                        {roleMatches.length}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Role Matches
                                    </Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Card elevation={2} sx={{ height: '100%' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <AccountCircleOutlined sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                                <Box>
                                    <Typography variant="h3" fontWeight="bold">
                                        {Math.round(skills.reduce((acc, s) => acc + s.weighted_score, 0) / (skills.length || 1))}%
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Avg Skill Score
                                    </Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Skills Section */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Skill Proficiency
                        </Typography>
                        {skills.length === 0 ? (
                            <Alert severity="info">No skills tracked yet.</Alert>
                        ) : (
                            <Box sx={{ mt: 2 }}>
                                {skills.map((skill) => (
                                    <Box key={skill.skill_id} sx={{ mb: 2 }}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                            <Typography variant="body2" fontWeight="medium">
                                                {skill.skill_name}
                                            </Typography>
                                            <Typography
                                                variant="body2"
                                                fontWeight="bold"
                                                sx={{ color: getScoreColor(skill.weighted_score) }}
                                            >
                                                {skill.weighted_score}%
                                            </Typography>
                                        </Box>
                                        <LinearProgress
                                            variant="determinate"
                                            value={skill.weighted_score}
                                            sx={{
                                                height: 8,
                                                borderRadius: 4,
                                                backgroundColor: 'grey.200',
                                                '& .MuiLinearProgress-bar': {
                                                    backgroundColor: getScoreColor(skill.weighted_score),
                                                },
                                            }}
                                        />
                                    </Box>
                                ))}
                            </Box>
                        )}
                    </Paper>
                </Grid>

                {/* Top Role Matches */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Recommended Roles
                        </Typography>
                        {roleMatches.length === 0 ? (
                            <Alert severity="info">No role matches found.</Alert>
                        ) : (
                            <Box sx={{ mt: 2 }}>
                                {roleMatches.map((role) => (
                                    <Card
                                        key={role.role_id}
                                        variant="outlined"
                                        sx={{ mb: 2, p: 2 }}
                                    >
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                            <Typography variant="body1" fontWeight="bold">
                                                {role.role_title}
                                            </Typography>
                                            <Chip
                                                label={`${role.match_score}% Match`}
                                                color={role.match_score >= 70 ? 'success' : 'warning'}
                                                size="small"
                                            />
                                        </Box>
                                        <Typography variant="caption" color="text.secondary" display="block">
                                            {role.role_category}
                                        </Typography>
                                    </Card>
                                ))}
                            </Box>
                        )}
                    </Paper>
                </Grid>

                {/* Portfolio Section */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={2} sx={{ p: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <CodeOutlined color="primary" sx={{ mr: 1.5 }} />
                            <Typography variant="h6" fontWeight="bold">
                                Academic Projects
                            </Typography>
                        </Box>
                        {projects.length === 0 ? (
                            <Alert severity="info">No projects added yet.</Alert>
                        ) : (
                            projects.map((proj) => (
                                <Box key={proj.id} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #eee' }}>
                                    <Typography variant="subtitle1" fontWeight="bold">{proj.title}</Typography>
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        Type: {proj.type}
                                    </Typography>
                                    <Box sx={{ mt: 1 }}>
                                        {Array.isArray(proj.tech_stack) ? proj.tech_stack.map((tech) => (
                                            <Chip key={tech} label={tech} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                                        )) : null}
                                    </Box>
                                </Box>
                            ))
                        )}
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper elevation={2} sx={{ p: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <VerifiedOutlined color="secondary" sx={{ mr: 1.5 }} />
                            <Typography variant="h6" fontWeight="bold">
                                Certifications
                            </Typography>
                        </Box>
                        {certifications.length === 0 ? (
                            <Alert severity="info">No certifications added yet.</Alert>
                        ) : (
                            certifications.map((cert) => (
                                <Box key={cert.id} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #eee' }}>
                                    <Typography variant="subtitle1" fontWeight="bold">{cert.title}</Typography>
                                    <Typography variant="body2" color="text.secondary">{cert.provider}</Typography>
                                    {cert.completion_date && (
                                        <Typography variant="caption" display="block">
                                            Completed: {new Date(cert.completion_date).toLocaleDateString()}
                                        </Typography>
                                    )}
                                </Box>
                            ))
                        )}
                    </Paper>
                </Grid>

            </Grid>
        </Container>
    );
};

export default TPOStudentDetail;
