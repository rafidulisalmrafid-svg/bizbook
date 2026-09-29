import React, { useState, useEffect } from 'react';
import { Briefcase, Plus, Globe, MapPin, Archive } from 'lucide-react';
import { request } from '../services/api';
import { Client } from '../types';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/common/StatusBadge';

export const ClientsPage: React.FC = () => {
  const { role } = useAuth();
  const [clients, setClients] = useState<Client[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [industry, setIndustry] = useState('');
  const [website, setWebsite] = useState('');
  const [address, setAddress] = useState('');

  const canEdit = role === 'OWNER' || role === 'ADMIN' || role === 'MANAGER';

  const loadClients = async () => {
    try {
      const data = await request<Client[]>('/clients');
      setClients(data);
    } catch (err) {
      console.error('Failed to load clients', err);
    }
  };

  useEffect(() => {
    loadClients();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await request('/clients', {
        method: 'POST',
        body: JSON.stringify({ name, industry, website, address, status: 'ACTIVE' }),
      });
      setIsModalOpen(false);
      setName('');
      setIndustry('');
      setWebsite('');
      setAddress('');
      loadClients();
    } catch (err: any) {
      alert(err.message || 'Creation failed');
    }
  };

  const handleArchive = async (id: string) => {
    if (!confirm('Archive this client?')) return;
    try {
      await request(`/clients/${id}`, { method: 'DELETE' });
      loadClients();
    } catch (err: any) {
      alert(err.message || 'Archive failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Client Directory</h1>
          <p className="text-xs text-slate-400 mt-1">Enterprise accounts, contacts, and relationship records.</p>
        </div>
        {canEdit && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-lg shadow-brand-600/30"
          >
            <Plus className="w-4 h-4" />
            <span>Add Client</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {clients.map((c) => (
          <div key={c.id} className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{c.name}</h3>
                  <p className="text-xs text-slate-400">{c.industry || 'Enterprise'}</p>
                </div>
                <StatusBadge status={c.status} />
              </div>

              {c.website && (
                <div className="mt-3 flex items-center space-x-1.5 text-xs text-brand-400">
                  <Globe className="w-3.5 h-3.5 text-slate-500" />
                  <a href={c.website} target="_blank" rel="noreferrer" className="hover:underline truncate">
                    {c.website}
                  </a>
                </div>
              )}

              {c.address && (
                <div className="mt-2 flex items-center space-x-1.5 text-xs text-slate-400">
                  <MapPin className="w-3.5 h-3.5 text-slate-500" />
                  <span className="truncate">{c.address}</span>
                </div>
              )}
            </div>

            {canEdit && (
              <div className="mt-4 pt-3 border-t border-slate-800/60 flex justify-end">
                <button
                  onClick={() => handleArchive(c.id)}
                  title="Archive Client"
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <Archive className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-md rounded-2xl p-6 border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">Add Client</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Company / Organization Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Industry</label>
                <input
                  type="text"
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  placeholder="Government, Banking, Telecommunications"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Website</label>
                <input
                  type="url"
                  value={website}
                  onChange={(e) => setWebsite(e.target.value)}
                  placeholder="https://client.com"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Address</label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
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
                  Save Client
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
