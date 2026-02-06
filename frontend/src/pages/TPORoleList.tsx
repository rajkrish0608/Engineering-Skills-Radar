import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Paper,
    Typography,
    Box,
    Button,
    Grid,
    Card,
    CardContent,
    TextField,
    InputAdornment,
    Chip,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    OutlinedInput,
    SelectChangeEvent,
    CircularProgress,
    Alert,
    Checkbox,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Divider
} from '@mui/material';
import {
    Add,
    Search,
    Edit,
    Delete,
    ArrowBack,
    Business,
    AttachMoney,
    DeleteOutline
} from '@mui/icons-material';
import apiClient from '@/services/apiClient';

interface Role {
    id: string;
    role_title: string;
    category: string;
    description: string;
    eligible_branches: string[];
    avg_ctc?: number;
    demand_score: number;
    typical_companies: string[];
    required_skills: RequiredSkill[];
}

interface RequiredSkill {
    skill_name: string;
    min_score: number;
    mandatory: boolean;
    weight: number;
}

interface Skill {
    id: string;
    skill_name: string;
    category: string;
}

const BRANCHES = ['CS', 'IT', 'ECE', 'EE', 'ME', 'CE'];
const CATEGORIES = ['Software', 'Core Engineering', 'Sales', 'Management', 'Data', 'Design'];

const TPORoleList: React.FC = () => {
    const navigate = useNavigate();

    const [roles, setRoles] = useState<Role[]>([]);
    const [allSkills, setAllSkills] = useState<Skill[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    // Dialog State
    const [openDialog, setOpenDialog] = useState(false);
    const [editingRole, setEditingRole] = useState<Role | null>(null);
    const [formData, setFormData] = useState<Partial<Role>>({
        role_title: '',
        category: '',
        description: '',
        eligible_branches: [],
        avg_ctc: 0,
        demand_score: 50,
        typical_companies: [],
        required_skills: []
    });
    const [saving, setSaving] = useState(false);

    // Skill Selection State
    const [selectedSkillId, setSelectedSkillId] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [rolesRes, skillsRes] = await Promise.all([
                apiClient.get<any>('/api/roles/'),
                apiClient.get<any>('/api/skills/')
            ]);
            setRoles(rolesRes.roles);
            setAllSkills(skillsRes.skills);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    const fetchRoles = async () => {
        const response = await apiClient.get<any>('/api/roles/');
        setRoles(response.roles);
    };

    const handleOpenDialog = (role?: Role) => {
        if (role) {
            setEditingRole(role);
            setFormData({
                role_title: role.role_title,
                category: role.category || '',
                description: role.description || '',
                eligible_branches: role.eligible_branches || [],
                avg_ctc: role.avg_ctc || 0,
                demand_score: role.demand_score || 50,
                typical_companies: role.typical_companies || [],
                required_skills: role.required_skills || []
            });
        } else {
            setEditingRole(null);
            setFormData({
                role_title: '',
                category: '',
                description: '',
                eligible_branches: [],
                avg_ctc: 0,
                demand_score: 50,
                typical_companies: [],
                required_skills: []
            });
        }
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setEditingRole(null);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'avg_ctc' || name === 'demand_score' ? Number(value) : value
        }));
    };

    const handleBranchChange = (event: SelectChangeEvent<string[]>) => {
        const {
            target: { value },
        } = event;
        setFormData(prev => ({
            ...prev,
            eligible_branches: typeof value === 'string' ? value.split(',') : value,
        }));
    };

    const handleCategoryChange = (event: SelectChangeEvent) => {
        setFormData(prev => ({
            ...prev,
            category: event.target.value
        }));
    };

    // Skill Management
    const handleAddSkill = () => {
        if (!selectedSkillId) return;
        const skill = allSkills.find(s => s.id === selectedSkillId);
        if (!skill) return;

        // Check if already exists
        if (formData.required_skills?.some(s => s.skill_name === skill.skill_name)) {
            return;
        }

        setFormData(prev => ({
            ...prev,
            required_skills: [
                ...(prev.required_skills || []),
                {
                    skill_name: skill.skill_name,
                    min_score: 70,
                    mandatory: false,
                    weight: 0.25
                }
            ]
        }));
        setSelectedSkillId('');
    };

    const handleRemoveSkill = (skillName: string) => {
        setFormData(prev => ({
            ...prev,
            required_skills: prev.required_skills?.filter(s => s.skill_name !== skillName) || []
        }));
    };

    const handleSkillChange = (index: number, field: keyof RequiredSkill, value: any) => {
        const updatedSkills = [...(formData.required_skills || [])];
        updatedSkills[index] = {
            ...updatedSkills[index],
            [field]: value
        };
        setFormData(prev => ({ ...prev, required_skills: updatedSkills }));
    };

    const handleSave = async () => {
        if (!formData.role_title) return;

        try {
            setSaving(true);
            const payload = {
                ...formData,
                role_category: formData.category,
                // Ensure required_skills is formatted correctly
                required_skills: formData.required_skills?.map(s => ({
                    ...s,
                    min_score: Number(s.min_score),
                    weight: Number(s.weight)
                }))
            };

            if (editingRole) {
                await apiClient.put(`/api/roles/${editingRole.id}`, payload);
            } else {
                await apiClient.post('/api/roles/', payload);
            }

            fetchRoles();
            handleCloseDialog();
        } catch (err: any) {
            console.error('Failed to save role', err);
            // Show error in a snackbar usually
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this role?')) {
            try {
                await apiClient.delete(`/api/roles/${id}`);
                fetchRoles();
            } catch (err) {
                console.error('Failed to delete role', err);
            }
        }
    };

    const filteredRoles = roles.filter(role =>
        role.role_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        role.category?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Navigation */}
            <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Button startIcon={<ArrowBack />} onClick={() => navigate('/tpo')}>
                    Dashboard
                </Button>
                <Typography color="text.secondary">/</Typography>
                <Typography color="text.primary">Role Management</Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Typography variant="h4" fontWeight="bold">
                    Industry Roles
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => handleOpenDialog()}
                >
                    Add New Role
                </Button>
            </Box>

            <Paper sx={{ p: 2, mb: 3 }}>
                <TextField
                    fullWidth
                    placeholder="Search roles by title or category..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <Search color="action" />
                            </InputAdornment>
                        ),
                    }}
                    size="small"
                />
            </Paper>

            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress />
                </Box>
            ) : error ? (
                <Alert severity="error">{error}</Alert>
            ) : (
                <Grid container spacing={3}>
                    {filteredRoles.map((role) => (
                        <Grid item xs={12} md={6} lg={4} key={role.id}>
                            <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                        <Box>
                                            <Typography variant="h6" fontWeight="bold">
                                                {role.role_title}
                                            </Typography>
                                            <Chip
                                                label={role.category}
                                                size="small"
                                                color="primary"
                                                variant="outlined"
                                                sx={{ mt: 0.5 }}
                                            />
                                        </Box>
                                        <Box>
                                            <IconButton size="small" onClick={() => handleOpenDialog(role)}>
                                                <Edit fontSize="small" />
                                            </IconButton>
                                            <IconButton size="small" color="error" onClick={() => handleDelete(role.id)}>
                                                <Delete fontSize="small" />
                                            </IconButton>
                                        </Box>
                                    </Box>

                                    <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                                        <Chip
                                            icon={<AttachMoney />}
                                            label={role.avg_ctc ? `₹${(role.avg_ctc / 100000).toFixed(1)} LPA` : 'CTC N/A'}
                                            size="small"
                                        />
                                        <Chip
                                            icon={<Business />}
                                            label={`${role.typical_companies?.length || 0} Companies`}
                                            size="small"
                                        />
                                    </Box>

                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                        {role.description}
                                    </Typography>

                                    {/* Skills Summary */}
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                                            Required Skills ({role.required_skills?.length || 0})
                                        </Typography>
                                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', maxHeight: 40, overflow: 'hidden' }}>
                                            {role.required_skills?.slice(0, 4).map(s => (
                                                <Chip key={s.skill_name} label={s.skill_name} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
                                            ))}
                                            {(role.required_skills?.length || 0) > 4 &&
                                                <Chip label={`+${(role.required_skills?.length || 0) - 4}`} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
                                            }
                                        </Box>
                                    </Box>

                                    <Box sx={{ mt: 'auto' }}>
                                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                                            Eligible Branches:
                                        </Typography>
                                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                            {role.eligible_branches?.map(b => (
                                                <Chip key={b} label={b} size="small" sx={{ height: 20, fontSize: '0.7rem' }} />
                                            ))}
                                        </Box>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            {/* Add/Edit Role Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="lg" fullWidth>
                <DialogTitle>{editingRole ? 'Edit Role' : 'Add New Role'}</DialogTitle>
                <DialogContent dividers>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Grid container spacing={2}>
                                <Grid item xs={12}>
                                    <TextField
                                        fullWidth
                                        label="Role Title"
                                        name="role_title"
                                        value={formData.role_title}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <FormControl fullWidth>
                                        <InputLabel>Category</InputLabel>
                                        <Select
                                            value={formData.category}
                                            label="Category"
                                            onChange={handleCategoryChange}
                                        >
                                            {CATEGORIES.map(cat => (
                                                <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        fullWidth
                                        label="Description"
                                        name="description"
                                        value={formData.description}
                                        onChange={handleInputChange}
                                        multiline
                                        rows={4}
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="Average CTC (₹)"
                                        name="avg_ctc"
                                        type="number"
                                        value={formData.avg_ctc}
                                        onChange={handleInputChange}
                                    />
                                </Grid>
                                <Grid item xs={6}>
                                    <TextField
                                        fullWidth
                                        label="Demand Score (0-100)"
                                        name="demand_score"
                                        type="number"
                                        value={formData.demand_score}
                                        onChange={handleInputChange}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <FormControl fullWidth>
                                        <InputLabel>Eligible Branches</InputLabel>
                                        <Select
                                            multiple
                                            value={formData.eligible_branches}
                                            onChange={handleBranchChange}
                                            input={<OutlinedInput label="Eligible Branches" />}
                                            renderValue={(selected) => (
                                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                                    {selected.map((value) => (
                                                        <Chip key={value} label={value} size="small" />
                                                    ))}
                                                </Box>
                                            )}
                                        >
                                            {BRANCHES.map((branch) => (
                                                <MenuItem key={branch} value={branch}>
                                                    {branch}
                                                </MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>
                                </Grid>
                            </Grid>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>Required Skills & Scoring</Typography>
                            <Divider sx={{ mb: 2 }} />

                            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                <FormControl fullWidth size="small">
                                    <InputLabel>Add Skill</InputLabel>
                                    <Select
                                        value={selectedSkillId}
                                        label="Add Skill"
                                        onChange={(e) => setSelectedSkillId(e.target.value)}
                                    >
                                        {allSkills.map((skill) => (
                                            <MenuItem key={skill.id} value={skill.id}>
                                                {skill.skill_name} ({skill.category})
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                                <Button variant="contained" onClick={handleAddSkill}>
                                    Add
                                </Button>
                            </Box>

                            <Paper variant="outlined" sx={{ height: 400, overflow: 'auto' }}>
                                <Table size="small" stickyHeader>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Skill</TableCell>
                                            <TableCell width={100}>Min Score</TableCell>
                                            <TableCell width={80}>Mandatory</TableCell>
                                            <TableCell width={50}></TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {formData.required_skills?.length === 0 ? (
                                            <TableRow>
                                                <TableCell colSpan={4} align="center">
                                                    No skills added yet
                                                </TableCell>
                                            </TableRow>
                                        ) : (
                                            formData.required_skills?.map((skill, index) => (
                                                <TableRow key={index}>
                                                    <TableCell>{skill.skill_name}</TableCell>
                                                    <TableCell>
                                                        <TextField
                                                            type="number"
                                                            size="small"
                                                            value={skill.min_score}
                                                            onChange={(e) => handleSkillChange(index, 'min_score', Number(e.target.value))}
                                                            InputProps={{ inputProps: { min: 0, max: 100 } }}
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <Checkbox
                                                            checked={skill.mandatory}
                                                            onChange={(e) => handleSkillChange(index, 'mandatory', e.target.checked)}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                    <TableCell>
                                                        <IconButton size="small" color="error" onClick={() => handleRemoveSkill(skill.skill_name)}>
                                                            <DeleteOutline fontSize="small" />
                                                        </IconButton>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </Paper>
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Cancel</Button>
                    <Button
                        onClick={handleSave}
                        variant="contained"
                        disabled={saving || !formData.role_title}
                    >
                        {saving ? 'Saving...' : 'Save Role'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default TPORoleList;
