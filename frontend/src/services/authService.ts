/**
 * Authentication Service
 * Handles login, register, logout, and token management
 */
import apiClient from './apiClient';

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface RegisterData {
    username: string;
    email: string;
    password: string;
    full_name?: string;
    role: 'student' | 'tpo' | 'faculty' | 'admin';
    department?: string;
}

export interface User {
    id: string;
    username: string;
    email: string;
    role: string;
    full_name?: string;
    department?: string;
    is_active: boolean;
    created_at?: string;
    last_login?: string;
}

export interface AuthResponse {
    status: string;
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: User;
}

class AuthService {
    /**
     * Login user
     */
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const response = await apiClient.post<AuthResponse>('/api/auth/login', credentials);

        // Store tokens
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        localStorage.setItem('user', JSON.stringify(response.user));

        return response;
    }

    /**
     * Register new user
     */
    async register(data: RegisterData): Promise<any> {
        return await apiClient.post('/api/auth/register', data);
    }

    /**
     * Logout user
     */
    logout(): void {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    /**
     * Get current user info from API
     */
    async getCurrentUser(): Promise<User> {
        const response = await apiClient.get<{ status: string; user: User }>('/api/auth/me');
        localStorage.setItem('user', JSON.stringify(response.user));
        return response.user;
    }

    /**
     * Get stored user from localStorage
     */
    getStoredUser(): User | null {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated(): boolean {
        return !!localStorage.getItem('access_token');
    }

    /**
     * Change password
     */
    async changePassword(oldPassword: string, newPassword: string): Promise<any> {
        return await apiClient.post('/api/auth/change-password', {
            old_password: oldPassword,
            new_password: newPassword,
        });
    }
}

export const authService = new AuthService();
export default authService;
