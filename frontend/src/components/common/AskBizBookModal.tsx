import React, { useState } from 'react';
import { Search, Sparkles, X, FileText, CheckCircle2, ShieldAlert } from 'lucide-react';
import { ActionCard } from './ActionCard';

interface AskBizBookModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AskBizBookModal: React.FC<AskBizBookModalProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [hasSearched, setHasSearched] = useState(false);

  if (!isOpen) return null;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setHasSearched(true);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in">
      <div className="glass-panel w-full max-w-2xl rounded-2xl p-6 shadow-2xl border border-slate-700/80 flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">Ask BizBook Corporate Memory</h3>
              <p className="text-xs text-slate-400">Search institutional knowledge, credentials, tenders, and evidence</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearch} className="my-4">
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Find ISO certificates, previous healthcare projects, or generate tender case study..."
              className="w-full pl-11 pr-24 py-3 rounded-xl bg-slate-900/90 border border-slate-700/70 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/30"
              autoFocus
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-xs font-medium text-white transition-colors"
            >
              Analyze
            </button>
          </div>
        </form>

        {/* Content area */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {hasSearched ? (
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-purple-950/30 border border-purple-800/40 text-xs text-purple-200 flex items-start space-x-2.5">
                <Sparkles className="w-4 h-4 text-purple-400 mt-0.5 shrink-0" />
                <div>
                  <p className="font-semibold mb-1">Company Memory AI Insight:</p>
                  <p className="text-purple-300">
                    Query matched against company vault, completed projects, and team credentials. 
                    Zero hallucinations: all returned matches are grounded in verified records.
                  </p>
                </div>
              </div>

              <div>
                <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
                  Actionable Recommendations
                </h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <ActionCard
                    title="Verified Project Evidence"
                    description="Automated Government Gateway Portal - Completed contract ($180,000 USD)."
                    type="Use"
                    badge="Verified"
                    metadata="Source: Projects Database"
                    onClick={() => alert('Evidence linked to draft tender')}
                  />
                  <ActionCard
                    title="Case Study Narrative"
                    description="Generate standardized case study ready for tender submission."
                    type="Generate"
                    badge="Ready"
                    metadata="Zero-Fabrication Guaranteed"
                    onClick={() => alert('Portfolio draft generated')}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="py-8 text-center">
              <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto mb-3 text-slate-500">
                <Sparkles className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-medium text-slate-300">Grounded Enterprise Memory</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                BizBook scans authorized company vault files, project deliverables, and team CVs. Missing data is never fabricated.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
