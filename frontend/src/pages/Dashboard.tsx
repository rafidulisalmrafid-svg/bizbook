import React from 'react';
import { Sparkles, Layers, FileCheck2, AlertCircle, FileText, CheckCircle2, TrendingUp, Users } from 'lucide-react';
import { ActionCard } from '../components/common/ActionCard';
import { StatusBadge } from '../components/common/StatusBadge';

export const Dashboard: React.FC = () => {
  const stats = [
    { title: 'Active Projects', value: '12', change: '+2 this month', icon: Layers, color: 'text-blue-400' },
    { title: 'Live Tenders', value: '4', change: '2 deadlines soon', icon: FileCheck2, color: 'text-purple-400' },
    { title: 'Vault Documents', value: '48', change: '100% Virus-scanned', icon: FileText, color: 'text-emerald-400' },
    { title: 'Team Credentials', value: '29', change: 'Grounded in CVs', icon: Users, color: 'text-indigo-400' },
  ];

  const recentTenders = [
    { id: '1', title: 'National Healthcare AI Diagnostics Platform', deadline: 'Oct 15, 2026', readiness: '88%', status: 'READY' },
    { id: '2', title: 'Municipal Smart Grid Monitoring System', deadline: 'Nov 02, 2026', readiness: '64%', status: 'REVIEW' },
    { id: '3', title: 'Ministry Cloud Infrastructure Modernization', deadline: 'Nov 18, 2026', readiness: '95%', status: 'READY' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl glass-panel p-6 border border-slate-800">
        <div className="absolute right-0 top-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Multi-Tenant Enterprise AI Operational</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">BizBook Command Center</h1>
            <p className="text-xs text-slate-400 max-w-xl mt-1">
              Zero-hallucination institutional memory, vault governance, and automated tender proposal engine.
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => window.location.href = '/app/tenders'}
              className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-lg shadow-purple-600/30"
            >
              <Sparkles className="w-4 h-4" />
              <span>New AI Tender Analysis</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s, idx) => (
          <div key={idx} className="glass-panel p-5 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">{s.title}</span>
              <s.icon className={`w-4 h-4 ${s.color}`} />
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-2xl font-bold text-white tracking-tight">{s.value}</span>
              <span className="text-[11px] text-slate-400 font-medium">{s.change}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Actionable AI Controls Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Actionable AI Controls</h3>
            <p className="text-xs text-slate-400">Directly execute actions grounded in company memory</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ActionCard
            title="Generate Portfolio Case Study"
            description="Extract verified completion data from 'Automated Government Gateway' project."
            type="Generate"
            badge="Project Evidence"
            metadata="Verified: $180,000 Contract"
            onClick={() => alert('Generating Case Study...')}
          />
          <ActionCard
            title="Review Compliance Matrix"
            description="National Healthcare AI Diagnostics tender has 2 missing certificates."
            type="Review"
            badge="Action Required"
            metadata="2 items require human review"
            onClick={() => alert('Opening Compliance Matrix...')}
          />
          <ActionCard
            title="Upload Audited Financials"
            description="Vault needs 2025 audited financial statement for upcoming municipal bids."
            type="Upload"
            badge="Expiring Soon"
            metadata="Target: Financial Vault"
            onClick={() => alert('Opening Vault Upload...')}
          />
        </div>
      </div>

      {/* Active Tenders Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Active Tenders & Submissions</h3>
            <p className="text-xs text-slate-400">Tender compliance matrices and readiness scoring</p>
          </div>
          <button
            onClick={() => window.location.href = '/app/tenders'}
            className="text-xs text-brand-400 hover:text-brand-300 font-medium"
          >
            View all tenders →
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="px-6 py-3 font-semibold">Tender Title</th>
                <th className="px-6 py-3 font-semibold">Submission Deadline</th>
                <th className="px-6 py-3 font-semibold">Readiness Score</th>
                <th className="px-6 py-3 font-semibold">Status</th>
                <th className="px-6 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {recentTenders.map((t) => (
                <tr key={t.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">{t.title}</td>
                  <td className="px-6 py-4 text-slate-400 font-mono">{t.deadline}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded-full"
                          style={{ width: t.readiness }}
                        ></div>
                      </div>
                      <span className="font-mono text-slate-300">{t.readiness}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={t.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => window.location.href = `/app/tenders/${t.id}`}
                      className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition-colors"
                    >
                      Open Matrix
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
