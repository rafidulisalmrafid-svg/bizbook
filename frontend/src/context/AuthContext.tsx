import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthResponse, Role, User } from '../types';
import { request } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  companyId: string | null;
  role: Role | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string, companyName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('bizbook_token'));
  const [companyId, setCompanyId] = useState<string | null>(() => localStorage.getItem('bizbook_company_id'));
  const [role, setRole] = useState<Role | null>(() => (localStorage.getItem('bizbook_role') as Role) || null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadUser() {
      if (token) {
        try {
          const userData = await request<User>('/auth/me');
          setUser(userData);
        } catch (err) {
          console.error('Failed to load user session', err);
          logout();
        }
      }
      setIsLoading(false);
    }
    loadUser();
  }, [token]);

  const handleAuthSuccess = (data: AuthResponse) => {
    localStorage.setItem('bizbook_token', data.access_token);
    localStorage.setItem('bizbook_company_id', data.company_id);
    localStorage.setItem('bizbook_role', data.role);
    setToken(data.access_token);
    setCompanyId(data.company_id);
    setRole(data.role);
  };

  const login = async (email: string, password: string) => {
    const data = await request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    handleAuthSuccess(data);
    const userData = await request<User>('/auth/me', {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    setUser(userData);
  };

  const register = async (fullName: string, email: string, password: string, companyName: string) => {
    const data = await request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        full_name: fullName,
        email,
        password,
        company_name: companyName,
      }),
    });
    handleAuthSuccess(data);
    const userData = await request<User>('/auth/me', {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('bizbook_token');
    localStorage.removeItem('bizbook_company_id');
    localStorage.removeItem('bizbook_role');
    setToken(null);
    setCompanyId(null);
    setRole(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        companyId,
        role,
        isAuthenticated: !!token,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
