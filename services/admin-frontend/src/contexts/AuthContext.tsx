import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, UserRole, PERMISSIONS } from '@/types';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
  isSuperAdmin: () => boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper to convert API user to frontend User type
function mapApiUserToUser(apiUser: any): User {
  return {
    id: apiUser.id,
    email: apiUser.email,
    name: apiUser.name,
    role: apiUser.role as UserRole,
    permissions: apiUser.permissions || [],
    isActive: apiUser.is_active !== undefined ? apiUser.is_active : apiUser.isActive,
    createdAt: apiUser.created_at ? new Date(apiUser.created_at) : new Date(),
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('taxease_access_token');
      const storedUser = localStorage.getItem('taxease_user');
      
      if (token && storedUser) {
        try {
          // Try to get current user from API
          const apiUser = await apiService.getCurrentUser();
          const mappedUser = mapApiUserToUser(apiUser);
          setUser(mappedUser);
          localStorage.setItem('taxease_user', JSON.stringify(mappedUser));
        } catch (error) {
          // Token invalid, clear storage
          console.error('Auth check failed:', error);
          localStorage.removeItem('taxease_access_token');
          localStorage.removeItem('taxease_refresh_token');
          localStorage.removeItem('taxease_user');
        }
      }
      setIsLoading(false);
    };
    
    checkAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      console.log('Attempting login for:', email);
      const response = await apiService.login(email, password);
      console.log('Login response received:', response);
      
      if (!response || !response.user) {
        throw new Error('Invalid response from server');
      }
      
      const mappedUser = mapApiUserToUser(response.user);
      setUser(mappedUser);
      localStorage.setItem('taxease_user', JSON.stringify(mappedUser));
      console.log('Login successful, user set');
      return true;
    } catch (error: any) {
      console.error('Login failed:', error);
      const errorMessage = error?.data?.detail || error?.message || 'Invalid email or password';
      console.error('Error details:', {
        status: error?.status,
        message: errorMessage,
        error: error
      });
      toast({
        title: 'Login failed',
        description: errorMessage,
        variant: 'destructive',
      });
      return false;
    }
  };

  const logout = () => {
    apiService.logout();
    setUser(null);
    localStorage.removeItem('taxease_user');
  };

  const refreshUser = async () => {
    try {
      const apiUser = await apiService.getCurrentUser();
      const mappedUser = mapApiUserToUser(apiUser);
      setUser(mappedUser);
      localStorage.setItem('taxease_user', JSON.stringify(mappedUser));
    } catch (error) {
      console.error('Failed to refresh user:', error);
      logout();
    }
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    if (user.role === 'superadmin') return true;
    return user.permissions.includes(permission);
  };

  const isSuperAdmin = (): boolean => {
    return user?.role === 'superadmin';
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      isLoading, 
      login, 
      logout, 
      hasPermission, 
      isSuperAdmin,
      refreshUser 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
