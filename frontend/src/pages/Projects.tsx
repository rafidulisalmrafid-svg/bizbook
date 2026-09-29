import React, { useState, useEffect } from 'react';
import { Layers, Plus, Sparkles, FileText, CheckCircle2, DollarSign } from 'lucide-react';
import { request } from '../services/api';
import { Project, PortfolioDraft } from '../types';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/common/StatusBadge';

export const ProjectsPage: React.FC = () => {
  const { role } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [portfolioDraft, setPortfolioDraft] = useState<PortfolioDraft | null>(null);
  const [title, setTitle] = useState('');
  const [contractValue, setContractValue] = useState(50000);
  const [summary, setSummary] = useState('');

  const canEdit = role === 'OWNER' || role === 'ADMIN' || role === 'MANAGER';

  const loadProjects = async () => {
    try {
      const data = await request<Project[]>('/projects');
      setProjects(data);
    } catch (err) {
      console.error('Failed to load projects', err);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await request('/projects', {
        method: 'POST',
        body: JSON.stringify({
          title,
          contract_value: Number(contractValue),
          currency: 'USD',
          status: 'COMPLETED',
          completion_summary: summary,
        }),
      });
      setIsModalOpen(false);
      setTitle('');
      setContractValue(50000);
      setSummary('');
      loadProjects();
    } catch (err: any) {
      alert(err.message || 'Creation failed');
    }
  };

  const handleGeneratePortfolio = async (id: string) => {
    try {
      const draft = await request<PortfolioDraft>(`/projects/${id}/portfolio-draft`, {
        method: 'POST',
      });
      setPortfolioDraft(draft);
      loadProjects();
    } catch (err: any) {
      alert(err.message || 'Draft creation failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Project Portfolio & Evidence</h1>
          <p className="text-xs text-slate-400 mt-1">
            Track contracts, deliverables, linked team members, and generate tender-ready case studies.
          </p>
        </div>
        {canEdit && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-lg shadow-brand-600/30"
          >
            <Plus className="w-4 h-4" />
            <span>Add Project</span>
          </button>
        )}
      </div>

      {/* Portfolio Draft Modal Notification */}
      {portfolioDraft && (
        <div className="p-5 rounded-2xl glass-panel border border-purple-500/40 bg-purple-950/20 space-y-3 animate-in fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-purple-400" />
              <h3 className="text-sm font-bold text-white">{portfolioDraft.title}</h3>
            </div>
            <button
              onClick={() => setPortfolioDraft(null)}
              className="text-xs text-slate-400 hover:text-white"
            >
              Dismiss
            </button>
          </div>
          <p className="text-xs text-purple-200">
            <strong>Solution & Delivery:</strong> {portfolioDraft.solution}
          </p>
          <p className="text-xs text-emerald-300">
            <strong>Impact:</strong> {portfolioDraft.results_and_impact}
          </p>
          <div className="flex items-center space-x-2 pt-1 text-[11px] text-slate-400">
            <span>Evidence Documents Verified: {portfolioDraft.evidence_count}</span>
            <span>•</span>
            <span className="text-amber-400">Marked: Ready for Human Review</span>
          </div>
        </div>
      )}

      {/* Project Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map((p) => (
          <div key={p.id} className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{p.title}</h3>
                  <div className="mt-1 flex items-center space-x-2 text-xs font-mono text-emerald-400">
                    <DollarSign className="w-3.5 h-3.5" />
                    <span>{p.currency} {p.contract_value.toLocaleString()}</span>
                  </div>
                </div>
                <StatusBadge status={p.status} />
              </div>

              {p.completion_summary && (
                <p className="text-xs text-slate-400 mt-3 line-clamp-2">
                  {p.completion_summary}
                </p>
              )}

              <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500">
                <span>{p.documents?.length || 0} Evidence Files</span>
                <span>{p.team_members?.length || 0} Team Contributors</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
              {p.portfolio_draft_created ? (
                <span className="text-[11px] text-purple-400 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Portfolio Draft Created</span>
                </span>
              ) : (
                <span className="text-[11px] text-slate-500">No Case Study Draft</span>
              )}

              {canEdit && (
                <button
                  onClick={() => handleGeneratePortfolio(p.id)}
                  className="px-3 py-1.5 rounded-lg bg-purple-600/20 text-purple-300 border border-purple-500/30 hover:bg-purple-600/30 text-xs font-medium flex items-center space-x-1.5 transition-colors"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Generate Case Study</span>
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-md rounded-2xl p-6 border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">Add Project</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Project Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Contract Value (USD)</label>
                <input
                  type="number"
                  required
                  value={contractValue}
                  onChange={(e) => setContractValue(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Completion Summary</label>
                <textarea
                  rows={3}
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  placeholder="Key deliverables, achievements and metrics..."
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-brand-600 text-white text-xs font-semibold hover:bg-brand-500"
                >
                  Save Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
