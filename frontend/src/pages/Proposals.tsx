import React, { useState } from 'react';
import { FileText, Plus, DollarSign, Calendar, CheckCircle2, Clock, XCircle, ArrowUpRight, Sparkles } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';

export const ProposalsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'all' | 'draft' | 'sent' | 'accepted'>('all');

  const mockProposals = [
    {
      id: 'prop-1',
      title: 'Enterprise Cloud Architecture Overhaul',
      client: 'Global Tech Corp',
      project: 'Cloud Banking Migration',
      subtotal: 10000,
      tax: 950,
      total: 10450,
      currency: 'USD',
      status: 'SENT',
      validUntil: '2026-10-31',
      itemsCount: 2,
    },
    {
      id: 'prop-2',
      title: 'AI Diagnostic Copilot Deployment',
      client: 'National Health Services',
      project: 'Healthcare AI Platform',
      subtotal: 45000,
      tax: 4275,
      total: 49275,
      currency: 'USD',
      status: 'ACCEPTED',
      validUntil: '2026-11-15',
      itemsCount: 4,
    },
    {
      id: 'prop-3',
      title: 'Zero-Trust IAM & Vault Governance Scope',
      client: 'Apex Financial Holdings',
      project: 'Cybersecurity Hardening',
      subtotal: 18500,
      tax: 1757.5,
      total: 20257.5,
      currency: 'USD',
      status: 'DRAFT',
      validUntil: '2026-10-15',
      itemsCount: 3,
    },
  ];

  const filtered = activeTab === 'all' ? mockProposals : mockProposals.filter((p) => p.status.toLowerCase() === activeTab);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
            <FileText className="w-5 h-5 text-brand-400" />
            <span>Proposals & Quotations</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Grounded commercial proposals, granular line items, and client quotations.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => alert('New Proposal generator will open with grounded templates')}
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>New Commercial Proposal</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 text-xs">
        {(['all', 'draft', 'sent', 'accepted'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1.5 rounded-lg capitalize font-medium transition-all ${
              activeTab === tab
                ? 'bg-brand-600/20 text-brand-400 border border-brand-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Proposals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((prop) => (
          <div
            key={prop.id}
            className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all group"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <StatusBadge status={prop.status} />
                <span className="text-[11px] text-slate-500 font-mono">
                  {prop.itemsCount} line items
                </span>
              </div>
              <h3 className="text-sm font-semibold text-white group-hover:text-brand-300 transition-colors">
                {prop.title}
              </h3>
              <p className="text-xs text-slate-400 mt-1 font-medium">{prop.client}</p>
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-slate-400">Total Value:</span>
                <span className="font-bold text-white font-mono text-sm">
                  ${prop.total.toLocaleString()} {prop.currency}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
              <span className="flex items-center space-x-1">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                <span>Valid: {prop.validUntil}</span>
              </span>
              <button
                onClick={() => alert(`Viewing details for ${prop.title}`)}
                className="text-brand-400 hover:text-brand-300 font-medium flex items-center space-x-0.5"
              >
                <span>View Scope</span>
                <ArrowUpRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
