/**
 * Main App Component
 * Sets up routing, theme, and auth provider
 */
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import StudentDashboard from './pages/StudentDashboard';
import GapAnalysisPage from './pages/GapAnalysisPage';
import AssessmentPage from './pages/AssessmentPage';
import TPODashboard from './pages/TPODashboard';
import TPOStudentList from './pages/TPOStudentList';

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />

            {/* Student routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute requiredRole={['student']}>
                  <StudentDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/gaps/:roleId"
              element={
                <ProtectedRoute requiredRole={['student']}>
                  <GapAnalysisPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/assessment"
              element={
                <ProtectedRoute requiredRole={['student']}>
                  <AssessmentPage />
                </ProtectedRoute>
              }
            />

            {/* TPO routes */}
            <Route
              path="/tpo"
              element={
                <ProtectedRoute requiredRole={['tpo', 'admin']}>
                  <TPODashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/tpo/students"
              element={
                <ProtectedRoute requiredRole={['tpo', 'admin']}>
                  <TPOStudentList />
                </ProtectedRoute>
              }
            />

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
