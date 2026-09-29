import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  Users,
  Briefcase,
  Layers,
  FileCheck2,
  FolderLock,
  History,
  FileText,
  Receipt,
  Sparkles,
  LogOut,
  Bell,
  Search,
} from 'lucide-react';

import { useAuth } from '../../context/AuthContext';
import { AskBizBookModal } from '../common/AskBizBookModal';

export const DashboardLayout: React.FC = () => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const [isAskModalOpen, setIsAskModalOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/app/dashboard', icon: LayoutDashboard },
    { name: 'Company Profile', path: '/app/company', icon: Building2 },
    { name: 'Team & Skills', path: '/app/team', icon: Users },
    { name: 'Clients Directory', path: '/app/clients', icon: Briefcase },
    { name: 'Projects & Evidence', path: '/app/projects', icon: Layers },
    { name: 'Services Catalog', path: '/app/services', icon: Briefcase },
    { name: 'Document Vault', path: '/app/vault', icon: FolderLock },
    { name: 'Tenders & Bids', path: '/app/tenders', icon: FileCheck2 },
    { name: 'Proposals & Quotes', path: '/app/proposals', icon: FileText },
    { name: 'Invoices & Billing', path: '/app/invoices', icon: Receipt },
    { name: 'Audit & Governance', path: '/app/audit', icon: History },
  ];


  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden font-sans">
      {/* Sidebar - Desktop first */}
      <aside className="w-64 border-r border-slate-800/80 bg-slate-900/60 backdrop-blur-xl flex flex-col justify-between shrink-0">
        <div>
          {/* Brand header */}
          <div className="h-16 px-6 flex items-center border-b border-slate-800/80 space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <span className="font-extrabold text-white text-lg">B</span>
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white block">BizBook</span>
              <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider block">Enterprise AI</span>
            </div>
          </div>

          {/* Quick Action: Ask BizBook */}
          <div className="p-4">
            <button
              onClick={() => setIsAskModalOpen(true)}
              className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-gradient-to-r from-purple-900/40 to-indigo-900/40 border border-purple-500/30 hover:border-purple-400 text-purple-200 transition-all shadow-sm group"
            >
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-purple-400 group-hover:scale-110 transition-transform" />
                <span className="text-xs font-semibold">Ask BizBook</span>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-mono">⌘K</span>
            </button>
          </div>

          {/* Nav items (Primary 7-9 areas) */}
          <nav className="px-3 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-brand-600/20 text-brand-400 border border-brand-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <item.icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        {/* User footer */}
        <div className="p-4 border-t border-slate-800/80">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 min-w-0">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-brand-400 shrink-0">
                {user?.full_name?.charAt(0) || 'U'}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-slate-200 truncate">{user?.full_name || 'Enterprise User'}</p>
                <span className="text-[10px] text-brand-400 font-mono block uppercase">{role || 'MEMBER'}</span>
              </div>
            </div>
            <button
              onClick={handleLogout}
              title="Logout"
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top header */}
        <header className="h-16 border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-xl px-8 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-4">
            <div className="relative w-80">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Search vault, tenders, projects..."
                onClick={() => setIsAskModalOpen(true)}
                readOnly
                className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 placeholder-slate-500 cursor-pointer focus:outline-none hover:border-slate-700"
              />
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsAskModalOpen(true)}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-purple-600/20 text-purple-300 border border-purple-500/30 hover:bg-purple-600/30 text-xs font-medium transition-all"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Ask BizBook AI</span>
            </button>
            <div className="h-4 w-px bg-slate-800"></div>
            <button className="p-2 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 transition-colors relative">
              <Bell className="w-4 h-4" />
              <span className="w-2 h-2 rounded-full bg-brand-500 absolute top-1.5 right-1.5 ring-2 ring-slate-950"></span>
            </button>
          </div>
        </header>

        {/* Dynamic page outlet */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>

      {/* Global Ask BizBook Modal */}
      <AskBizBookModal isOpen={isAskModalOpen} onClose={() => setIsAskModalOpen(false)} />
    </div>
  );
};
