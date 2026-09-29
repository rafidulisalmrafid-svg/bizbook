import React, { useState, useEffect } from 'react';
import { Building2, Palette, Phone, FileSignature, Stamp, Plus, Save, CheckCircle2 } from 'lucide-react';
import { request } from '../services/api';
import { Company, CompanyProfile as ICompanyProfile, CompanyBrand as ICompanyBrand, CompanySignature, CompanySeal } from '../types';
import { useAuth } from '../context/AuthContext';

export const CompanyProfilePage: React.FC = () => {
  const { role } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'brand' | 'signature'>('profile');
  const [profile, setProfile] = useState<ICompanyProfile | null>(null);
  const [brand, setBrand] = useState<ICompanyBrand | null>(null);
  const [signatures, setSignatures] = useState<CompanySignature[]>([]);
  const [seals, setSeals] = useState<CompanySeal[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const canEdit = role === 'OWNER' || role === 'ADMIN' || role === 'MANAGER';
  const canSign = role === 'OWNER' || role === 'ADMIN';

  useEffect(() => {
    async function loadData() {
      try {
        const [profData, brandData, sigsData, sealsData] = await Promise.all([
          request<ICompanyProfile>('/company/profile'),
          request<ICompanyBrand>('/company/brand'),
          request<CompanySignature[]>('/company/signatures'),
          request<CompanySeal[]>('/company/seals'),
        ]);
        setProfile(profData);
        setBrand(brandData);
        setSignatures(sigsData);
        setSeals(sealsData);
      } catch (err) {
        console.error('Failed to load company assets', err);
      }
    }
    loadData();
  }, []);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setIsSaving(true);
    setSuccessMsg(null);
    try {
      const updated = await request<ICompanyProfile>('/company/profile', {
        method: 'PUT',
        body: JSON.stringify(profile),
      });
      setProfile(updated);
      setSuccessMsg('Company profile updated successfully.');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      alert(err.message || 'Update failed');
    } finally {
      setIsSaving(false);
    }
  };

  const handleBrandSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!brand) return;
    setIsSaving(true);
    setSuccessMsg(null);
    try {
      const updated = await request<ICompanyBrand>('/company/brand', {
        method: 'PUT',
        body: JSON.stringify(brand),
      });
      setBrand(updated);
      setSuccessMsg('Brand assets saved successfully.');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      alert(err.message || 'Update failed');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Company Identity & Governance</h1>
        <p className="text-xs text-slate-400 mt-1">
          Manage corporate credentials, brand assets, letterheads, digital signatures and official seals.
        </p>
      </div>

      {successMsg && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-800">
        <button
          onClick={() => setActiveTab('profile')}
          className={`pb-3 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'profile'
              ? 'border-brand-500 text-brand-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Building2 className="w-4 h-4" />
          <span>Legal & Overview</span>
        </button>
        <button
          onClick={() => setActiveTab('brand')}
          className={`pb-3 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'brand'
              ? 'border-brand-500 text-brand-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Palette className="w-4 h-4" />
          <span>Brand & Visuals</span>
        </button>
        <button
          onClick={() => setActiveTab('signature')}
          className={`pb-3 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'signature'
              ? 'border-brand-500 text-brand-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileSignature className="w-4 h-4" />
          <span>Signatures & Seals</span>
        </button>
      </div>

      {/* Tab: Profile */}
      {activeTab === 'profile' && profile && (
        <form onSubmit={handleProfileSave} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Registration / Trade License No.</label>
              <input
                type="text"
                disabled={!canEdit}
                value={profile.registration_number || ''}
                onChange={(e) => setProfile({ ...profile, registration_number: e.target.value })}
                placeholder="TRD-2024-88910"
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-brand-500 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Tax Identification Number (TIN/VAT)</label>
              <input
                type="text"
                disabled={!canEdit}
                value={profile.tax_id || ''}
                onChange={(e) => setProfile({ ...profile, tax_id: e.target.value })}
                placeholder="TIN-9812-764"
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-brand-500 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Established Year</label>
              <input
                type="number"
                disabled={!canEdit}
                value={profile.established_year || ''}
                onChange={(e) => setProfile({ ...profile, established_year: parseInt(e.target.value) || undefined })}
                placeholder="2018"
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-brand-500 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Primary Industry</label>
              <input
                type="text"
                disabled={!canEdit}
                value={profile.primary_industry || ''}
                onChange={(e) => setProfile({ ...profile, primary_industry: e.target.value })}
                placeholder="Information Technology & AI Services"
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-brand-500 disabled:opacity-50"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Company Overview</label>
            <textarea
              rows={3}
              disabled={!canEdit}
              value={profile.overview || ''}
              onChange={(e) => setProfile({ ...profile, overview: e.target.value })}
              placeholder="Enterprise software company specializing in AI document processing..."
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-brand-500 disabled:opacity-50"
            />
          </div>

          {canEdit && (
            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={isSaving}
                className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                <span>{isSaving ? 'Saving...' : 'Save Profile Changes'}</span>
              </button>
            </div>
          )}
        </form>
      )}

      {/* Tab: Brand */}
      {activeTab === 'brand' && brand && (
        <form onSubmit={handleBrandSave} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Primary Color</label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  disabled={!canEdit}
                  value={brand.primary_color || '#2563eb'}
                  onChange={(e) => setBrand({ ...brand, primary_color: e.target.value })}
                  className="w-9 h-9 rounded-lg bg-transparent cursor-pointer border border-slate-700"
                />
                <input
                  type="text"
                  disabled={!canEdit}
                  value={brand.primary_color || ''}
                  onChange={(e) => setBrand({ ...brand, primary_color: e.target.value })}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 font-mono"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Corporate Font Family</label>
              <input
                type="text"
                disabled={!canEdit}
                value={brand.font_family || 'Inter'}
                onChange={(e) => setBrand({ ...brand, font_family: e.target.value })}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200"
              />
            </div>
          </div>

          {canEdit && (
            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={isSaving}
                className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                <span>{isSaving ? 'Saving...' : 'Update Brand Tokens'}</span>
              </button>
            </div>
          )}
        </form>
      )}

      {/* Tab: Signatures & Seals */}
      {activeTab === 'signature' && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white">Authorized Digital Signatures</h3>
                <p className="text-xs text-slate-400">Strict approval workflow: Generate → Review → Approve → Apply → Lock</p>
              </div>
              {canSign && (
                <button
                  onClick={() => alert('New signature authorization request flow')}
                  className="px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium flex items-center space-x-1.5"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Authorized Signatory</span>
                </button>
              )}
            </div>

            {signatures.length === 0 ? (
              <div className="py-6 text-center text-xs text-slate-500">
                No active signatures registered. Signatures require dedicated permission.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {signatures.map((s) => (
                  <div key={s.id} className="p-4 rounded-xl glass-card border border-slate-700/60 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-white">{s.name}</p>
                      <p className="text-[11px] text-slate-400">{s.designation}</p>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Authorized
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
