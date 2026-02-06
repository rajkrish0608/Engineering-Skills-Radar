import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Box,
    Container,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    TextField,
    Button,
    Grid,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    IconButton,
    InputAdornment,
    Toolbar,
    AppBar,
    CircularProgress,
    Alert
} from '@mui/material';
import {
    Search,
    FilterList,
    Visibility,
    ArrowBack,
    PersonAdd
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

const TPOStudentList: React.FC = () => {
    const navigate = useNavigate();

    // State
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [totalCount, setTotalCount] = useState(0);

    // Filters
    const [searchQuery, setSearchQuery] = useState('');
    const [branch, setBranch] = useState('');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    const branches = ['CS', 'IT', 'Mechanical', 'Civil', 'Electrical', 'ECE'];

    useEffect(() => {
        fetchStudents();
    }, [page, rowsPerPage, branch]); // Trigger on filter changes (excluding search for now)

    const fetchStudents = async () => {
        setLoading(true);
        setError('');
        try {
            let url = `/api/students/?skip=${page * rowsPerPage}&limit=${rowsPerPage}`;

            if (branch && branch !== 'All') {
                url += `&branch=${branch}`;
            }

            // Only use search URL if search query is present
            if (searchQuery) {
                // If searching, we use the search endpoint (which might not support pagination/filtering the same way)
                // Integrating search + filter is complex if endpoints are separate.
                // For now, if Query exists, use Search endpoint.
                url = `/api/students/search?q=${searchQuery}`;
            }

            const response = await apiClient.get<any>(url);

            setStudents(response.students || []);
            setTotalCount(response.count || (response.students ? response.students.length : 0));
        } catch (err: any) {
            console.error('Failed to fetch students', err);
            setError('Failed to load student list');
        } finally {
            setLoading(false);
        }
    };

    const handleSearchSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setPage(0);
        fetchStudents();
    };

    const handleChangePage = (_event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    return (
        <Box sx={{ bgcolor: '#f5f7fa', minHeight: '100vh' }}>
            <AppBar position="static" color="default" elevation={1}>
                <Toolbar>
                    <IconButton edge="start" sx={{ mr: 2 }} onClick={() => navigate('/tpo')}>
                        <ArrowBack />
                    </IconButton>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        Student Management
                    </Typography>
                    <Button
                        variant="contained"
                        startIcon={<PersonAdd />}
                        onClick={() => navigate('/tpo/import')} // Placeholder for import
                    >
                        Bulk Import
                    </Button>
                </Toolbar>
            </AppBar>

            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Paper sx={{ p: 3, mb: 3 }}>
                    <form onSubmit={handleSearchSubmit}>
                        <Grid container spacing={2} alignItems="center">
                            <Grid item xs={12} md={5}>
                                <TextField
                                    fullWidth
                                    placeholder="Search by name, roll no, or email..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <Search color="action" />
                                            </InputAdornment>
                                        ),
                                    }}
                                />
                            </Grid>
                            <Grid item xs={12} md={3}>
                                <FormControl fullWidth>
                                    <InputLabel>Branch</InputLabel>
                                    <Select
                                        value={branch}
                                        label="Branch"
                                        onChange={(e) => setBranch(e.target.value)}
                                        startAdornment={
                                            <InputAdornment position="start">
                                                <FilterList />
                                            </InputAdornment>
                                        }
                                    >
                                        <MenuItem value=""><em>All Branches</em></MenuItem>
                                        {branches.map((b) => (
                                            <MenuItem key={b} value={b}>{b}</MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} md={2}>
                                <Button
                                    fullWidth
                                    variant="outlined"
                                    size="large"
                                    onClick={fetchStudents}
                                    sx={{ height: 56 }}
                                >
                                    Filter
                                </Button>
                            </Grid>
                        </Grid>
                    </form>
                </Paper>

                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                <Paper sx={{ width: '100%', overflow: 'hidden' }}>
                    <TableContainer sx={{ maxHeight: '70vh' }}>
                        <Table stickyHeader aria-label="student list table">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Roll Number</TableCell>
                                    <TableCell>Full Name</TableCell>
                                    <TableCell>Branch</TableCell>
                                    <TableCell>Semester</TableCell>
                                    <TableCell>CGPA</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell align="right">Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center" sx={{ py: 5 }}>
                                            <CircularProgress />
                                        </TableCell>
                                    </TableRow>
                                ) : students.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                                            <Typography color="text.secondary">No students found matching criteria.</Typography>
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    students.map((student) => (
                                        <TableRow hover role="checkbox" tabIndex={-1} key={student.id}>
                                            <TableCell sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}>
                                                {student.roll_number}
                                            </TableCell>
                                            <TableCell>{student.full_name}</TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={student.branch}
                                                    size="small"
                                                    color="primary"
                                                    variant="outlined"
                                                />
                                            </TableCell>
                                            <TableCell>{student.current_semester}</TableCell>
                                            <TableCell>
                                                {student.cgpa > 0 ? (
                                                    <Box component="span" sx={{ fontWeight: 'bold', color: student.cgpa >= 7.5 ? 'success.main' : 'text.primary' }}>
                                                        {student.cgpa.toFixed(2)}
                                                    </Box>
                                                ) : '-'}
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={student.account_status || 'Active'}
                                                    size="small"
                                                    color={student.account_status === 'Active' ? 'success' : 'default'}
                                                    sx={{ height: 24, fontSize: '0.75rem' }}
                                                />
                                            </TableCell>
                                            <TableCell align="right">
                                                <Button
                                                    size="small"
                                                    startIcon={<Visibility />}
                                                    onClick={() => navigate(`/tpo/students/${student.id}`)}
                                                >
                                                    View
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                        rowsPerPageOptions={[10, 25, 100]}
                        component="div"
                        count={searchQuery ? students.length : totalCount} // API count might be inaccurate for search
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                </Paper>
            </Container>
        </Box>
    );
};

export default TPOStudentList;
