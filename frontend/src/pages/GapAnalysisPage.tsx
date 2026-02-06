import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container,
    Grid,
    Paper,
    Typography,
    Box,
    LinearProgress,
    Chip,
    Button,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Divider,
    Alert,
    CircularProgress,
    Breadcrumbs,
    Link as MuiLink
} from '@mui/material';
import {
    ArrowBack,
    CheckCircle,
    Warning,
    MenuBook,
    School,
    TrendingUp,
    NavigateNext
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/services/apiClient';

// Interfaces based on backend response
interface SkillGap {
    skill_id: string;
    skill_name: string;
    current_score: number;
    required_score: number;
    gap: number;
    priority: 'Critical' | 'High' | 'Medium' | 'Low';
    is_mandatory: boolean;
}

interface GapAnalysisData {
    role_id: string;
    role_title: string;
    company: string;
    gaps: SkillGap[];
    strengths: SkillGap[];
    total_gaps: number;
    total_strengths: number;
}

interface BaseRecommendation {
    skill: string;
    priority: string;
}

interface CertificationRecommendation extends BaseRecommendation {
    type: 'certification';
    title: string;
    provider: string;
}

interface ProjectRecommendation extends BaseRecommendation {
    suggestion: string;
}

interface Recommendations {
    certifications: CertificationRecommendation[];
    courses: any[];
    projects: ProjectRecommendation[];
}

interface AlternativeRole {
    role_id: string;
    role_title: string;
    company: string;
    ctc_range: string;
    compatibility: number;
    matched_skills: number;
    total_skills: number;
}

const GapAnalysisPage: React.FC = () => {
    const { roleId } = useParams<{ roleId: string }>();
    const navigate = useNavigate();
    const { user } = useAuth();

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [gapData, setGapData] = useState<GapAnalysisData | null>(null);
    const [recommendations, setRecommendations] = useState<Recommendations | null>(null);
    const [alternatives, setAlternatives] = useState<AlternativeRole[]>([]);

    useEffect(() => {
        if (roleId && user?.id) {
            fetchGapAnalysis();
        }
    }, [roleId, user]);

    const fetchGapAnalysis = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get<any>(`/api/students/${user?.id}/gap-analysis/${roleId}`);

            setGapData(response.gap_analysis);
            setRecommendations(response.recommendations);
            setAlternatives(response.alternative_roles);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load gap analysis');
        } finally {
            setLoading(false);
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'Critical': return 'error';
            case 'High': return 'warning';
            case 'Medium': return 'info';
            default: return 'success'; // Low priority
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <Alert severity="error" action={
                    <Button color="inherit" size="small" onClick={() => navigate('/dashboard')}>
                        Back to Dashboard
                    </Button>
                }>
                    {error}
                </Alert>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
            {/* Navigation */}
            <Box sx={{ mb: 3 }}>
                <Button
                    startIcon={<ArrowBack />}
                    onClick={() => navigate('/dashboard')}
                    sx={{ mb: 2 }}
                >
                    Back to Dashboard
                </Button>
                <Breadcrumbs separator={<NavigateNext fontSize="small" />}>
                    <MuiLink underline="hover" color="inherit" onClick={() => navigate('/dashboard')} sx={{ cursor: 'pointer' }}>
                        Dashboard
                    </MuiLink>
                    <Typography color="text.primary">Gap Analysis</Typography>
                </Breadcrumbs>
            </Box>

            {/* Header Section */}
            <Paper elevation={0} sx={{ p: 4, mb: 4, bgcolor: 'primary.main', color: 'primary.contrastText', borderRadius: 2 }}>
                <Typography variant="overline" sx={{ opacity: 0.8 }}>
                    ROLE ANALYSIS
                </Typography>
                <Typography variant="h3" fontWeight="bold" gutterBottom>
                    {gapData?.role_title}
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
                    {gapData?.company}
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 2 }}>
                    <Chip
                        label={`${gapData?.total_strengths} Strength Areas`}
                        color="success"
                        sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                        icon={<CheckCircle style={{ color: 'white' }} />}
                    />
                    <Chip
                        label={`${gapData?.total_gaps} Skills to Improve`}
                        color="warning"
                        sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                        icon={<TrendingUp style={{ color: 'white' }} />}
                    />
                </Box>
            </Paper>

            <Grid container spacing={4}>
                {/* Main Content: Gaps & Strengths */}
                <Grid item xs={12} md={8}>
                    {/* Critical Gaps Section */}
                    {gapData?.gaps && gapData.gaps.length > 0 ? (
                        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                                <Warning color="warning" sx={{ mr: 1.5, fontSize: 28 }} />
                                <Typography variant="h5" fontWeight="bold">
                                    Attention Needed
                                </Typography>
                            </Box>

                            {gapData.gaps.map((gap) => (
                                <Box key={gap.skill_id} sx={{ mb: 4 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, alignItems: 'center' }}>
                                        <Box>
                                            <Typography variant="h6" fontWeight="medium">
                                                {gap.skill_name}
                                            </Typography>
                                            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                                {gap.is_mandatory && (
                                                    <Chip label="Mandatory" size="small" color="error" variant="outlined" />
                                                )}
                                                <Chip
                                                    label={`${gap.priority} Priority`}
                                                    size="small"
                                                    color={getPriorityColor(gap.priority) as any}
                                                    variant="outlined"
                                                />
                                            </Box>
                                        </Box>
                                        <Box sx={{ textAlign: 'right' }}>
                                            <Typography variant="body2" color="text.secondary">Target: {gap.required_score}%</Typography>
                                            <Typography variant="h6" color={getPriorityColor(gap.priority) + ".main"}>
                                                {gap.current_score}%
                                            </Typography>
                                        </Box>
                                    </Box>
                                    <LinearProgress
                                        variant="determinate"
                                        value={(gap.current_score / gap.required_score) * 100}
                                        color={getPriorityColor(gap.priority) as any}
                                        sx={{ height: 10, borderRadius: 5, bgcolor: 'grey.100' }}
                                    />
                                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                        Gap of {gap.gap} points. Improve this to boost your match score.
                                    </Typography>
                                </Box>
                            ))}
                        </Paper>
                    ) : (
                        <Paper elevation={2} sx={{ p: 3, mb: 4, bgcolor: 'success.light', color: 'success.contrastText' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <CheckCircle sx={{ mr: 2, fontSize: 32 }} />
                                <Box>
                                    <Typography variant="h6" fontWeight="bold">Excellent Profile!</Typography>
                                    <Typography>You meet all the skill requirements for this role.</Typography>
                                </Box>
                            </Box>
                        </Paper>
                    )}

                    {/* Strengths Section */}
                    {gapData?.strengths && gapData.strengths.length > 0 && (
                        <Paper elevation={2} sx={{ p: 3 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                                <CheckCircle color="success" sx={{ mr: 1.5, fontSize: 28 }} />
                                <Typography variant="h5" fontWeight="bold">
                                    Your Strengths
                                </Typography>
                            </Box>
                            <Grid container spacing={2}>
                                {gapData.strengths.map((str) => (
                                    <Grid item xs={12} sm={6} key={str.skill_id}>
                                        <Paper variant="outlined" sx={{ p: 2, borderColor: 'success.main', bgcolor: 'success.50' }}>
                                            <Typography variant="subtitle1" fontWeight="bold">
                                                {str.skill_name}
                                            </Typography>
                                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                                                <CircularProgress
                                                    variant="determinate"
                                                    value={100}
                                                    size={24}
                                                    sx={{ color: 'success.main', mr: 1.5 }}
                                                />
                                                <Typography color="success.main" fontWeight="bold">
                                                    {str.current_score}%
                                                </Typography>
                                            </Box>
                                        </Paper>
                                    </Grid>
                                ))}
                            </Grid>
                        </Paper>
                    )}
                </Grid>

                {/* Sidebar: Recommendations & Alternatives */}
                <Grid item xs={12} md={4}>
                    <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
                        <Typography variant="h6" fontWeight="bold" gutterBottom>
                            Action Plan
                        </Typography>
                        <Divider sx={{ mb: 2 }} />

                        {recommendations?.certifications.length === 0 && recommendations?.projects.length === 0 && (
                            <Typography color="text.secondary">
                                No specific recommendations available.
                            </Typography>
                        )}

                        {recommendations?.certifications && recommendations.certifications.length > 0 && (
                            <Box sx={{ mb: 3 }}>
                                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                    RECOMMENDED CERTIFICATIONS
                                </Typography>
                                <List disablePadding>
                                    {recommendations.certifications.map((cert, index) => (
                                        <ListItem key={index} disableGutters>
                                            <ListItemIcon sx={{ minWidth: 36 }}>
                                                <School color="primary" fontSize="small" />
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={cert.title}
                                                secondary={cert.provider}
                                                primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                                                secondaryTypographyProps={{ variant: 'caption' }}
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </Box>
                        )}

                        {recommendations?.projects && recommendations.projects.length > 0 && (
                            <Box>
                                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                    PROJECT IDEAS
                                </Typography>
                                <List disablePadding>
                                    {recommendations.projects.map((proj, index) => (
                                        <ListItem key={index} disableGutters>
                                            <ListItemIcon sx={{ minWidth: 36 }}>
                                                <MenuBook color="secondary" fontSize="small" />
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={proj.suggestion}
                                                secondary={`Improve ${proj.skill}`}
                                                primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                                                secondaryTypographyProps={{ variant: 'caption' }}
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            </Box>
                        )}
                    </Paper>

                    {/* Alternative Roles */}
                    <Paper elevation={2} sx={{ p: 3 }}>
                        <Typography variant="h6" fontWeight="bold" gutterBottom>
                            Alternative Roles
                        </Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            Roles with better match scores based on your current skills.
                        </Typography>

                        {alternatives.map((alt) => (
                            <Box
                                key={alt.role_id}
                                sx={{
                                    p: 2,
                                    mb: 2,
                                    border: '1px solid',
                                    borderColor: 'divider',
                                    borderRadius: 1,
                                    cursor: 'pointer',
                                    '&:hover': { bgcolor: 'grey.50', borderColor: 'primary.main' }
                                }}
                                onClick={() => navigate(`/gaps/${alt.role_id}`)}
                            >
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                    <Typography variant="subtitle2" fontWeight="bold">
                                        {alt.role_title}
                                    </Typography>
                                    <Chip
                                        label={`${alt.compatibility}%`}
                                        size="small"
                                        color="success"
                                        sx={{ height: 20, fontSize: '0.7rem' }}
                                    />
                                </Box>
                                <Typography variant="caption" display="block" color="text.secondary">
                                    {alt.company}
                                </Typography>
                            </Box>
                        ))}
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default GapAnalysisPage;
