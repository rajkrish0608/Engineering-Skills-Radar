import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Paper,
    Typography,
    Box,
    Button,
    Grid,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    ListItemSecondaryAction,
    Divider,
    Alert
} from '@mui/material';
import {
    ArrowBack,
    Download,
    Assessment,
    TrendingUp,
    People
} from '@mui/icons-material';
import apiClient from '@/services/apiClient';

const TPOReports: React.FC = () => {
    const navigate = useNavigate();
    const [downloading, setDownloading] = useState(false);
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await apiClient.get<any>('/api/analytics/overview');
                setStats(res.metrics);
            } catch (e) {
                console.error(e);
            }
        };
        fetchStats();
    }, []);

    const handleExportStudents = async () => {
        try {
            setDownloading(true);
            const response = await apiClient.get('/api/analytics/export/students', {
                responseType: 'blob'
            });

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response as any]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `student_report_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (err) {
            console.error('Download failed', err);
            alert('Failed to download report');
        } finally {
            setDownloading(false);
        }
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Button startIcon={<ArrowBack />} onClick={() => navigate('/tpo')}>
                    Dashboard
                </Button>
                <Typography color="text.secondary">/</Typography>
                <Typography color="text.primary">Analytics & Reports</Typography>
            </Box>

            <Typography variant="h4" fontWeight="bold" gutterBottom>
                Analytics & Reports
            </Typography>

            <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 3, mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Available Reports
                        </Typography>
                        <List>
                            <ListItem>
                                <ListItemIcon>
                                    <People color="primary" />
                                </ListItemIcon>
                                <ListItemText
                                    primary="Student Performance Report"
                                    secondary="Comprehensive list of students with CGPA, Top Skills, and Best Role Matches."
                                />
                                <ListItemSecondaryAction>
                                    <Button
                                        variant="outlined"
                                        startIcon={<Download />}
                                        onClick={handleExportStudents}
                                        disabled={downloading}
                                    >
                                        {downloading ? 'Downloading...' : 'Export CSV'}
                                    </Button>
                                </ListItemSecondaryAction>
                            </ListItem>
                            <Divider component="li" />
                            <ListItem>
                                <ListItemIcon>
                                    <TrendingUp color="secondary" />
                                </ListItemIcon>
                                <ListItemText
                                    primary="Placement Analytics (Coming Soon)"
                                    secondary="Detailed breakdown of placement stats by branch and company."
                                />
                                <ListItemSecondaryAction>
                                    <Button variant="outlined" disabled>
                                        Export PDF
                                    </Button>
                                </ListItemSecondaryAction>
                            </ListItem>
                        </List>
                    </Paper>

                    <Alert severity="info" icon={<Assessment />}>
                        More advanced reports will be available once more data is collected from student assessments.
                    </Alert>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Quick Stats
                        </Typography>
                        <List dense>
                            <ListItem>
                                <ListItemText primary="Total Students" secondary={stats?.total_students || 0} />
                            </ListItem>
                            <Divider />
                            <ListItem>
                                <ListItemText primary="Placement Ready" secondary={`${stats?.placement_ready_percentage || 0}%`} />
                            </ListItem>
                            <Divider />
                            <ListItem>
                                <ListItemText primary="Avg Skill Score" secondary={stats?.avg_skill_score || 0} />
                            </ListItem>
                        </List>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default TPOReports;
