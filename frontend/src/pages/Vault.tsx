import React from 'react';
import { FolderLock, Upload, ShieldCheck, FileText, CheckCircle2, Clock } from 'lucide-react';
import { ActionCard } from '../components/common/ActionCard';
import { StatusBadge } from '../components/common/StatusBadge';

export const VaultPage: React.FC = () => {
  const documents = [
    { name: 'Incorporation_Certificate_2024.pdf', category: 'LEGAL', size: '2.4 MB', status: 'PROCESSED', expiry: 'Never' },
    { name: 'ISO_9001_Quality_Management.pdf', category: 'COMPLIANCE', size: '1.8 MB', status: 'PROCESSED', expiry: '2027-04-12' },
    { name: 'Audited_Financial_Statement_2025.xlsx', category: 'FINANCIAL', size: '4.1 MB', status: 'PROCESSED', expiry: '2026-12-31' },
    { name: 'Government_Security_Clearance.pdf', category: 'TECHNICAL', size: '920 KB', status: 'PROCESSED', expiry: '2028-01-15' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Document Vault & Institutional Memory</h1>
          <p className="text-xs text-slate-400 mt-1">
            Private, ClamAV virus-scanned repository with automated OCR, metadata classification and signed URL delivery.
          </p>
        </div>
        <button
          onClick={() => alert('Phase 2 Document Upload pipeline activated!')}
          className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-lg shadow-brand-600/30"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Document</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ActionCard
          title="Tax Clearance Certificate"
          description="Uploaded version v2 approved by Finance. Expiry tracking active."
          type="View"
          badge="Verified"
          metadata="Signed URL token: valid 15m"
          onClick={() => alert('Generating Signed Download URL...')}
        />
        <ActionCard
          title="Company Profile Template"
          description="Dynamic template with {{company.name}} and {{ceo.designation}} tokens."
          type="Use"
          badge="Template"
          metadata="Version 3.1"
          onClick={() => alert('Opening Template Editor...')}
        />
        <ActionCard
          title="Audited Balance Sheet"
          description="Financial compliance requirement for international tender participation."
          type="Review"
          badge="Review Needed"
          metadata="Human review required"
          onClick={() => alert('Reviewing financial document...')}
        />
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Verified Company Files</h3>
          <span className="text-xs text-emerald-400 flex items-center space-x-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Encrypted & Scanned</span>
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="px-6 py-3 font-semibold">Document Name</th>
                <th className="px-6 py-3 font-semibold">Category</th>
                <th className="px-6 py-3 font-semibold">File Size</th>
                <th className="px-6 py-3 font-semibold">Expiry Date</th>
                <th className="px-6 py-3 font-semibold">Processing State</th>
                <th className="px-6 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {documents.map((d, i) => (
                <tr key={i} className="hover:bg-slate-900/40 transition-colors">
                  <td className="px-6 py-3.5 font-medium text-white flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-brand-400 shrink-0" />
                    <span>{d.name}</span>
                  </td>
                  <td className="px-6 py-3.5 font-mono text-[11px] text-slate-400">{d.category}</td>
                  <td className="px-6 py-3.5 text-slate-400">{d.size}</td>
                  <td className="px-6 py-3.5 font-mono text-slate-400">{d.expiry}</td>
                  <td className="px-6 py-3.5">
                    <StatusBadge status={d.status} />
                  </td>
                  <td className="px-6 py-3.5 text-right">
                    <button
                      onClick={() => alert(`Generating signed URL for ${d.name}`)}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs"
                    >
                      Download (Signed)
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
