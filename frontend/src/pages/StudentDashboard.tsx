/**
 * Student Dashboard Page
 * Main dashboard showing skills, role matches, and profile
 */
import React, { useEffect, useState } from 'react';
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
} from '@mui/material';
import {
    AccountCircleOutlined,
    TrendingUpOutlined,
    WorkOutlineOutlined,
    SchoolOutlined,
    CodeOutlined,
    VerifiedOutlined,
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/services/apiClient';

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

const StudentDashboard: React.FC = () => {
    const { user } = useAuth();
    const [skills, setSkills] = useState<Skill[]>([]);
    const [roleMatches, setRoleMatches] = useState<RoleMatch[]>([]);
    const [projects, setProjects] = useState<Project[]>([]);
    const [certifications, setCertifications] = useState<Certification[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);

            // In a real app, get student ID from user profile
            // For now, we'll handle the case where we might not have data yet
            const studentId = user?.id;

            if (studentId) {
                const [skillsData, rolesData, projectsData, certsData] = await Promise.all([
                    apiClient.get<any>(`/api/students/${studentId}/skills`),
                    apiClient.get<any>(`/api/students/${studentId}/role-matches?top_n=5`),
                    apiClient.get<any>(`/api/students/${studentId}/projects`),
                    apiClient.get<any>(`/api/students/${studentId}/certifications`),
                ]);

                setSkills(skillsData.skills || []);
                setRoleMatches(rolesData.matches || []);
                setProjects(projectsData.projects || []);
                setCertifications(certsData.certifications || []);
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load dashboard data');
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
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <LinearProgress />
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Welcome Section */}
            <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                    <Typography variant="h4" gutterBottom fontWeight="bold">
                        Welcome back, {user?.full_name || user?.username}!
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Track your skills, explore career opportunities, and plan your growth.
                    </Typography>
                </Box>
                <Button
                    variant="contained"
                    size="large"
                    startIcon={<SchoolOutlined />}
                    onClick={() => window.location.href = '/assessment'}
                    sx={{ height: 48 }}
                >
                    Take Assessment
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Stats Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={4}>
                    <Card elevation={2}>
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
                    <Card elevation={2}>
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
                    <Card elevation={2}>
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
            </Grid>

            <Grid container spacing={3}>
                {/* Skills Section */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={2} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Your Skills
                        </Typography>

                        {skills.length === 0 ? (
                            <Alert severity="info">
                                No skills tracked yet. Complete assessments to build your profile.
                            </Alert>
                        ) : (
                            <Box sx={{ mt: 2 }}>
                                {skills.slice(0, 8).map((skill) => (
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
                    <Paper elevation={2} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Top Role Matches
                        </Typography>

                        {roleMatches.length === 0 ? (
                            <Alert severity="info">
                                Complete skill assessments to see role recommendations.
                            </Alert>
                        ) : (
                            <Box sx={{ mt: 2 }}>
                                {roleMatches.map((role) => (
                                    <Card
                                        key={role.role_id}
                                        variant="outlined"
                                        sx={{ mb: 2, p: 2, '&:hover': { boxShadow: 2 } }}
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
                                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                                            {role.role_category}
                                        </Typography>
                                        {role.avg_ctc && (
                                            <Typography variant="body2" color="primary" fontWeight="medium">
                                                Avg. CTC: ₹{role.avg_ctc / 100000} LPA
                                            </Typography>
                                        )}
                                        <Button
                                            size="small"
                                            variant="outlined"
                                            sx={{ mt: 1 }}
                                            onClick={() => window.location.href = `/gaps/${role.role_id}`}
                                        >
                                            View Gap Analysis
                                        </Button>
                                    </Card>
                                ))}
                            </Box>
                        )}
                    </Paper>
                </Grid>
            </Grid>

            {/* Portfolio Section */}
            <Typography variant="h5" gutterBottom fontWeight="bold" sx={{ mt: 4, mb: 3 }}>
                My Portfolio
            </Typography>

            <Grid container spacing={3}>
                {/* Projects */}
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

                {/* Certifications */}
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

export default StudentDashboard;
