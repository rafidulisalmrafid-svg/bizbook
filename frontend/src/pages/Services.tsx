import React, { useState, useEffect } from 'react';
import { Layers, Plus, DollarSign, Clock, CheckCircle2 } from 'lucide-react';
import { request } from '../services/api';
import { ServiceItem } from '../types';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/common/StatusBadge';

export const ServicesPage: React.FC = () => {
  const { role } = useAuth();
  const [services, setServices] = useState<ServiceItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Technology & AI');
  const [price, setPrice] = useState(25000);
  const [duration, setDuration] = useState('4 Weeks');
  const [deliverablesStr, setDeliverablesStr] = useState('');

  const canEdit = role === 'OWNER' || role === 'ADMIN' || role === 'MANAGER';

  const loadServices = async () => {
    try {
      const data = await request<ServiceItem[]>('/services');
      setServices(data);
    } catch (err) {
      console.error('Failed to load services', err);
    }
  };

  useEffect(() => {
    loadServices();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const deliverables = deliverablesStr.split(',').map((s) => s.trim()).filter(Boolean);
    try {
      await request('/services', {
        method: 'POST',
        body: JSON.stringify({
          title,
          category,
          standard_price: Number(price),
          typical_duration: duration,
          deliverables,
        }),
      });
      setIsModalOpen(false);
      setTitle('');
      setDeliverablesStr('');
      loadServices();
    } catch (err: any) {
      alert(err.message || 'Creation failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Services & Capabilities Catalog</h1>
          <p className="text-xs text-slate-400 mt-1">Pre-configured corporate offerings, timelines and pricing.</p>
        </div>
        {canEdit && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-lg shadow-brand-600/30"
          >
            <Plus className="w-4 h-4" />
            <span>Add Service Offering</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map((s) => (
          <div key={s.id} className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{s.title}</h3>
                  <span className="text-[11px] text-brand-400 font-medium">{s.category}</span>
                </div>
                <StatusBadge status={s.is_active ? 'ACTIVE' : 'ARCHIVED'} />
              </div>

              <div className="mt-4 flex items-center justify-between text-xs text-slate-300">
                <span className="flex items-center space-x-1 font-mono text-emerald-400">
                  <DollarSign className="w-3.5 h-3.5" />
                  <span>${s.standard_price.toLocaleString()}</span>
                </span>
                {s.typical_duration && (
                  <span className="flex items-center space-x-1 text-slate-400">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{s.typical_duration}</span>
                  </span>
                )}
              </div>

              {s.deliverables?.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-800/80">
                  <p className="text-[11px] font-semibold text-slate-400 mb-1.5">Deliverables:</p>
                  <ul className="space-y-1">
                    {s.deliverables.map((d, idx) => (
                      <li key={idx} className="flex items-center space-x-1.5 text-xs text-slate-300">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span className="truncate">{d}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-md rounded-2xl p-6 border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">Add Service Offering</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Service Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Category</label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Standard Price (USD)</label>
                <input
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Typical Duration</label>
                <input
                  type="text"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  placeholder="e.g. 4 Weeks"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Deliverables (comma separated)</label>
                <input
                  type="text"
                  value={deliverablesStr}
                  onChange={(e) => setDeliverablesStr(e.target.value)}
                  placeholder="Executive Summary, Cloud Architecture, SLA"
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
                  Save Service
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
