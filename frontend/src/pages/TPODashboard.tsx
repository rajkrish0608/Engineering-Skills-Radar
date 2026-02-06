import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Grid,
    Paper,
    Typography,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Drawer,
    AppBar,
    Toolbar,
    IconButton,
    Divider,
    Avatar,
    CircularProgress,
    Alert,
    Button
} from '@mui/material';
import {
    Dashboard,
    People,
    Work,
    Assessment,
    Menu as MenuIcon,
    Logout,
    TrendingUp,
    School,
    BusinessCenter,
    Person
} from '@mui/icons-material';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';
import { useAuth } from '@/contexts/AuthContext';
import apiClient from '@/services/apiClient';

// Interfaces for Analytics Data
interface DashboardMetrics {
    total_students: number;
    total_roles: number;
    placement_ready_percentage: number;
    avg_skill_score: number;
    active_recruitments: number;
}

interface BranchStat {
    branch: string;
    total_students: number;
    avg_skill_score: number;
    placement_ready_percentage: number;
}

const drawerWidth = 240;

const TPODashboard: React.FC = () => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();

    // State
    const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
    const [branchStats, setBranchStats] = useState<BranchStat[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [mobileOpen, setMobileOpen] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [overviewRes, branchRes] = await Promise.all([
                    apiClient.get<any>('/api/analytics/overview'),
                    apiClient.get<any>('/api/analytics/branch-stats')
                ]);

                setMetrics(overviewRes.metrics);
                setBranchStats(branchRes.branches);
            } catch (err: any) {
                console.error('Failed to fetch analytics', err);
                setError('Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Navigation Items
    const menuItems = [
        { text: 'Dashboard', icon: <Dashboard />, path: '/tpo' },
        { text: 'Students', icon: <People />, path: '/tpo/students' },
        { text: 'Roles & Jobs', icon: <Work />, path: '/tpo/roles' },
        { text: 'Analytics & Reports', icon: <Assessment />, path: '/tpo/reports' },
    ];

    const drawer = (
        <div>
            <Toolbar sx={{ justifyContent: 'center', py: 2 }}>
                <Typography variant="h6" color="primary" fontWeight="bold">
                    Skills Radar
                </Typography>
                <Typography variant="caption" display="block" color="text.secondary">
                    TPO Portal
                </Typography>
            </Toolbar>
            <Divider />
            <List>
                {menuItems.map((item) => (
                    <ListItem button key={item.text} onClick={() => navigate(item.path)} selected={window.location.pathname === item.path}>
                        <ListItemIcon color={window.location.pathname === item.path ? 'primary' : 'inherit'}>
                            {item.icon}
                        </ListItemIcon>
                        <ListItemText primary={item.text} />
                    </ListItem>
                ))}
            </List>
            <Divider />
            <Box sx={{ p: 2, textAlign: 'center' }}>
                <Button
                    variant="outlined"
                    color="error"
                    startIcon={<Logout />}
                    onClick={handleLogout}
                    fullWidth
                >
                    Logout
                </Button>
            </Box>
        </div>
    );

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ display: 'flex' }}>
            <AppBar
                position="fixed"
                sx={{
                    width: { sm: `calc(100% - ${drawerWidth}px)` },
                    ml: { sm: `${drawerWidth}px` },
                    bgcolor: 'background.paper',
                    color: 'text.primary',
                    boxShadow: 1
                }}
            >
                <Toolbar>
                    <IconButton
                        color="inherit"
                        aria-label="open drawer"
                        edge="start"
                        onClick={handleDrawerToggle}
                        sx={{ mr: 2, display: { sm: 'none' } }}
                    >
                        <MenuIcon />
                    </IconButton>
                    <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                        Placement Officer Dashboard
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body2" sx={{ mr: 2 }}>
                            {user?.username}
                        </Typography>
                        <Avatar sx={{ bgcolor: 'secondary.main' }}>
                            <Person />
                        </Avatar>
                    </Box>
                </Toolbar>
            </AppBar>

            <Box
                component="nav"
                sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
                aria-label="mailbox folders"
            >
                <Drawer
                    variant="temporary"
                    open={mobileOpen}
                    onClose={handleDrawerToggle}
                    ModalProps={{ keepMounted: true }}
                    sx={{
                        display: { xs: 'block', sm: 'none' },
                        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                    }}
                >
                    {drawer}
                </Drawer>
                <Drawer
                    variant="permanent"
                    sx={{
                        display: { xs: 'none', sm: 'block' },
                        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                    }}
                    open
                >
                    {drawer}
                </Drawer>
            </Box>

            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 3,
                    width: { sm: `calc(100% - ${drawerWidth}px)` },
                    bgcolor: '#f5f7fa',
                    minHeight: '100vh'
                }}
            >
                <Toolbar /> {/* Spacer for AppBar */}

                {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

                {/* Summary Metrics */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <People color="primary" sx={{ fontSize: 40, mr: 1, opacity: 0.8 }} />
                                <Typography color="text.secondary" variant="subtitle2">
                                    Total Students
                                </Typography>
                            </Box>
                            <Typography variant="h3" fontWeight="bold" sx={{ mt: 'auto' }}>
                                {metrics?.total_students}
                            </Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <BusinessCenter color="secondary" sx={{ fontSize: 40, mr: 1, opacity: 0.8 }} />
                                <Typography color="text.secondary" variant="subtitle2">
                                    Industry Roles
                                </Typography>
                            </Box>
                            <Typography variant="h3" fontWeight="bold" sx={{ mt: 'auto' }}>
                                {metrics?.total_roles}
                            </Typography>
                            <Typography variant="caption" color="success.main">
                                {metrics?.active_recruitments} active
                            </Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <TrendingUp color="success" sx={{ fontSize: 40, mr: 1, opacity: 0.8 }} />
                                <Typography color="text.secondary" variant="subtitle2">
                                    Placement Ready
                                </Typography>
                            </Box>
                            <Typography variant="h3" fontWeight="bold" sx={{ mt: 'auto' }}>
                                {metrics?.placement_ready_percentage}%
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                Students with &gt;70% match
                            </Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <School sx={{ fontSize: 40, color: '#ff9800', mr: 1, opacity: 0.8 }} />
                                <Typography color="text.secondary" variant="subtitle2">
                                    Avg Skill Score
                                </Typography>
                            </Box>
                            <Typography variant="h3" fontWeight="bold" sx={{ mt: 'auto' }}>
                                {metrics?.avg_skill_score}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                Across all branches
                            </Typography>
                        </Paper>
                    </Grid>
                </Grid>

                {/* Charts Section */}
                <Grid container spacing={3}>
                    {/* Branch Performance Chart */}
                    <Grid item xs={12} md={8}>
                        <Paper sx={{ p: 3, height: 400 }}>
                            <Typography variant="h6" gutterBottom fontWeight="bold">
                                Branch-wise Readiness & Score
                            </Typography>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={branchStats}
                                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="branch" />
                                    <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                                    <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                                    <Tooltip />
                                    <Legend />
                                    <Bar yAxisId="left" dataKey="avg_skill_score" name="Avg Skill Score" fill="#8884d8" radius={[4, 4, 0, 0]} />
                                    <Bar yAxisId="right" dataKey="placement_ready_percentage" name="Ready %" fill="#82ca9d" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </Paper>
                    </Grid>

                    {/* Student Distribution Pie Chart */}
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 3, height: 400 }}>
                            <Typography variant="h6" gutterBottom fontWeight="bold">
                                Student Distribution
                            </Typography>
                            <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={branchStats}
                                            innerRadius={60}
                                            outerRadius={100}
                                            paddingAngle={5}
                                            dataKey="total_students"
                                            nameKey="branch"
                                        >
                                            {branchStats.map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                        <Legend verticalAlign="bottom" height={36} />
                                    </PieChart>
                                </ResponsiveContainer>
                            </Box>
                        </Paper>
                    </Grid>
                </Grid>

                {/* Recent Activities / Alerts (Placeholder) */}
                <Paper sx={{ mt: 3, p: 3 }}>
                    <Typography variant="h6" gutterBottom fontWeight="bold">
                        Pending Actions
                    </Typography>
                    <List>
                        <ListItem>
                            <ListItemIcon><Work color="primary" /></ListItemIcon>
                            <ListItemText primary="Review 5 new role descriptions" secondary="Added by Design Corp" />
                            <Button variant="outlined" size="small">Review</Button>
                        </ListItem>
                        <Divider component="li" />
                        <ListItem>
                            <ListItemIcon><School color="warning" /></ListItemIcon>
                            <ListItemText primary="Validate 12 student certifications" secondary="Requires manual approval" />
                            <Button variant="outlined" size="small">Validate</Button>
                        </ListItem>
                    </List>
                </Paper>

            </Box>
        </Box>
    );
};

export default TPODashboard;
