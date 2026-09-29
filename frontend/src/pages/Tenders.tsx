import React from 'react';
import { FileCheck2, Sparkles, CheckCircle2, AlertTriangle, FileSpreadsheet, Package } from 'lucide-react';
import { ActionCard } from '../components/common/ActionCard';
import { StatusBadge } from '../components/common/StatusBadge';

export const TendersPage: React.FC = () => {
  const requirements = [
    { section: '3.1 Legal', text: 'Valid Trade License & Incorporation Certificate', type: 'LEGAL', status: 'READY', evidence: 'Incorporation_Certificate_2024.pdf' },
    { section: '4.2 Experience', text: 'At least 1 completed government portal contract > $100k', type: 'EXPERIENCE', status: 'READY', evidence: 'Project: Automated Government Gateway ($180k)' },
    { section: '5.1 Team', text: 'Lead AI Engineer with Cloud Certification', type: 'TEAM', status: 'READY', evidence: 'Dr. Sarah Chen (GCP ML Engineer)' },
    { section: '6.4 Financial', text: 'Audited Turnover statement > $500,000 for FY2025', type: 'FINANCIAL', status: 'REVIEW', evidence: 'Audited_Financial_Statement_2025.xlsx' },
    { section: '7.2 Quality', text: 'CMMI Level 3 or ISO 27001 Certification', type: 'DOCUMENT', status: 'MISSING', evidence: 'Flagged: ISO 27001 Missing in Vault' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Tender AI & Proposal Automation</h1>
          <p className="text-xs text-slate-400 mt-1">
            Zero-hallucination requirement matching, compliance matrix validation, and structured submission export.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => alert('Exporting structured Tender ZIP submission package...')}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center space-x-2 border border-slate-700 transition-colors"
          >
            <Package className="w-4 h-4" />
            <span>Export Tender ZIP</span>
          </button>
          <button
            onClick={() => alert('Starting AI Proposal Generation...')}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-lg shadow-purple-600/30"
          >
            <Sparkles className="w-4 h-4" />
            <span>Generate Full Proposal</span>
          </button>
        </div>
      </div>

      {/* Tender Readiness Score Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-mono text-purple-400 font-semibold uppercase">RFP-2026-HC-092</span>
          <h2 className="text-lg font-bold text-white mt-0.5">National Healthcare AI Diagnostics Tender</h2>
          <p className="text-xs text-slate-400 mt-1">Deadline: October 15, 2026 • Client: Ministry of Health</p>
        </div>
        <div className="flex items-center space-x-6">
          <div className="text-right">
            <span className="text-xs text-slate-400 block">Readiness Score</span>
            <span className="text-2xl font-extrabold text-emerald-400 font-mono">80%</span>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400 block">Blocking Issues</span>
            <span className="text-2xl font-extrabold text-rose-400 font-mono">1</span>
          </div>
        </div>
      </div>

      {/* Actionable Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ActionCard
          title="Missing ISO 27001 Certification"
          description="AI detected mandatory compliance item missing in company vault. Non-fabrication guarantee."
          type="Upload"
          badge="Blocking Issue"
          metadata="Status: MISSING"
          onClick={() => alert('Upload ISO 27001 to Vault...')}
        />
        <ActionCard
          title="Approve Team Allocation"
          description="Dr. Sarah Chen matched for Lead AI position based on verified GCP certifications."
          type="Approve"
          badge="Verified CV"
          metadata="Match Score: 98%"
          onClick={() => alert('Team allocation approved!')}
        />
        <ActionCard
          title="Technical Methodology Draft"
          description="Generate section-by-section proposal methodology grounded in company past performance."
          type="Generate"
          badge="Grounded"
          metadata="Zero Hallucination"
          onClick={() => alert('Generating Methodology...')}
        />
      </div>

      {/* Compliance Matrix Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Compliance Matrix & Requirement Matching</h3>
          <span className="text-xs text-slate-400">Section and page references preserved</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="px-6 py-3 font-semibold">Tender Section</th>
                <th className="px-6 py-3 font-semibold">Requirement Specification</th>
                <th className="px-6 py-3 font-semibold">Requirement Type</th>
                <th className="px-6 py-3 font-semibold">Evidence Grounding</th>
                <th className="px-6 py-3 font-semibold">Compliance Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {requirements.map((r, i) => (
                <tr key={i} className="hover:bg-slate-900/40 transition-colors">
                  <td className="px-6 py-3.5 font-mono text-purple-400 font-medium whitespace-nowrap">{r.section}</td>
                  <td className="px-6 py-3.5 font-medium text-slate-200">{r.text}</td>
                  <td className="px-6 py-3.5 font-mono text-[11px] text-slate-400">{r.type}</td>
                  <td className="px-6 py-3.5 text-xs text-slate-400">{r.evidence}</td>
                  <td className="px-6 py-3.5">
                    <StatusBadge status={r.status} />
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
