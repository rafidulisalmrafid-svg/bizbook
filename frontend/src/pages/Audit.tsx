import React, { useState, useEffect } from 'react';
import { History, ShieldCheck, RefreshCw } from 'lucide-react';
import { request } from '../services/api';
import { AuditLog } from '../types';

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadLogs = async () => {
    setIsLoading(true);
    try {
      const data = await request<AuditLog[]>('/audit');
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Immutable Audit Trail</h1>
          <p className="text-xs text-slate-400 mt-1">
            Tamper-evident log of authentication, resource creation, signatures, and portfolio actions.
          </p>
        </div>
        <button
          onClick={loadLogs}
          disabled={isLoading}
          className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center space-x-1.5 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Trail</span>
        </button>
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="px-6 py-3 font-semibold">Timestamp (UTC)</th>
                <th className="px-6 py-3 font-semibold">Action</th>
                <th className="px-6 py-3 font-semibold">Resource Type</th>
                <th className="px-6 py-3 font-semibold">Resource ID</th>
                <th className="px-6 py-3 font-semibold">Details / Context</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="px-6 py-3.5 font-mono text-slate-400 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-3.5">
                    <span className="font-mono px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20 text-[11px]">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-3.5 capitalize text-slate-300">{log.resource_type}</td>
                  <td className="px-6 py-3.5 font-mono text-[11px] text-slate-500">
                    {log.resource_id ? log.resource_id.slice(0, 8) + '...' : '-'}
                  </td>
                  <td className="px-6 py-3.5 text-slate-400 font-mono text-[11px] max-w-xs truncate">
                    {JSON.stringify(log.details)}
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
