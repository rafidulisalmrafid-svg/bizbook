import React, { useState, useEffect } from 'react';
import { Users, Plus, Award, Briefcase, Mail, Phone, Archive, Trash2 } from 'lucide-react';
import { request } from '../services/api';
import { TeamMember } from '../types';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/common/StatusBadge';

export const TeamPage: React.FC = () => {
  const { role } = useAuth();
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [designation, setDesignation] = useState('');
  const [department, setDepartment] = useState('');
  const [email, setEmail] = useState('');
  const [skillsStr, setSkillsStr] = useState('');

  const canEdit = role === 'OWNER' || role === 'ADMIN' || role === 'MANAGER';

  const loadMembers = async () => {
    try {
      const data = await request<TeamMember[]>('/team');
      setMembers(data);
    } catch (err) {
      console.error('Failed to load team', err);
    }
  };

  useEffect(() => {
    loadMembers();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const skills = skillsStr.split(',').map((s) => s.trim()).filter(Boolean);
    try {
      await request('/team', {
        method: 'POST',
        body: JSON.stringify({
          full_name: name,
          designation,
          department,
          email,
          skills,
        }),
      });
      setIsModalOpen(false);
      setName('');
      setDesignation('');
      setDepartment('');
      setEmail('');
      setSkillsStr('');
      loadMembers();
    } catch (err: any) {
      alert(err.message || 'Creation failed');
    }
  };

  const handleArchive = async (id: string) => {
    if (!confirm('Are you sure you want to archive this team member?')) return;
    try {
      await request(`/team/${id}`, { method: 'DELETE' });
      loadMembers();
    } catch (err: any) {
      alert(err.message || 'Archive failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Team & Human Capital</h1>
          <p className="text-xs text-slate-400 mt-1">
            Grounded qualifications, certifications, and project role allocations.
          </p>
        </div>
        {canEdit && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-lg shadow-brand-600/30"
          >
            <Plus className="w-4 h-4" />
            <span>Add Team Member</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {members.map((m) => (
          <div key={m.id} className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{m.full_name}</h3>
                  <p className="text-xs text-brand-400 font-medium">{m.designation}</p>
                  {m.department && <p className="text-[11px] text-slate-500">{m.department}</p>}
                </div>
                <StatusBadge status={m.is_active ? 'ACTIVE' : 'ARCHIVED'} />
              </div>

              {m.email && (
                <div className="mt-3 flex items-center space-x-1.5 text-xs text-slate-400">
                  <Mail className="w-3.5 h-3.5 text-slate-500" />
                  <span className="truncate">{m.email}</span>
                </div>
              )}

              {/* Skills */}
              <div className="mt-3 flex flex-wrap gap-1">
                {m.skills?.map((sk, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                    {sk}
                  </span>
                ))}
              </div>

              {/* Badges for experiences / certifications */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center space-x-3 text-[11px] text-slate-400">
                <span className="flex items-center space-x-1">
                  <Briefcase className="w-3.5 h-3.5 text-slate-500" />
                  <span>{m.experiences?.length || 0} Experiences</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Award className="w-3.5 h-3.5 text-slate-500" />
                  <span>{m.certifications?.length || 0} Certifications</span>
                </span>
              </div>
            </div>

            {canEdit && (
              <div className="mt-4 pt-3 border-t border-slate-800/60 flex justify-end">
                <button
                  onClick={() => handleArchive(m.id)}
                  title="Archive Member"
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <Archive className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Modal for adding team member */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-md rounded-2xl p-6 border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4">Add Team Member</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Designation</label>
                <input
                  type="text"
                  required
                  value={designation}
                  onChange={(e) => setDesignation(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Department</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Skills (comma separated)</label>
                <input
                  type="text"
                  value={skillsStr}
                  onChange={(e) => setSkillsStr(e.target.value)}
                  placeholder="Python, AI, Cloud, PMP"
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
                  Save Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
