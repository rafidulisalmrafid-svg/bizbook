import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { CompanyProfilePage } from './pages/CompanyProfile';
import { TeamPage } from './pages/Team';
import { ClientsPage } from './pages/Clients';
import { ProjectsPage } from './pages/Projects';
import { ServicesPage } from './pages/Services';
import { VaultPage } from './pages/Vault';
import { TendersPage } from './pages/Tenders';
import { AuditPage } from './pages/Audit';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-xs">
        Authenticating enterprise session...
      </div>
    );
  }
  return isAuthenticated ? <>{children}</> : <Navigate to="/auth/login" replace />;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/register" element={<Register />} />

          {/* Protected Application Routes */}
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/app/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="company" element={<CompanyProfilePage />} />
            <Route path="team" element={<TeamPage />} />
            <Route path="clients" element={<ClientsPage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="services" element={<ServicesPage />} />
            <Route path="vault" element={<VaultPage />} />
            <Route path="tenders" element={<TendersPage />} />
            <Route path="tenders/:id" element={<TendersPage />} />
            <Route path="audit" element={<AuditPage />} />
          </Route>

          {/* Root redirect */}
          <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
