import React, { useState } from 'react';
import { Receipt, Plus, DollarSign, Calendar, CheckCircle2, Clock, AlertTriangle, ArrowUpRight } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';

export const InvoicesPage: React.FC = () => {
  const [filter, setFilter] = useState<'ALL' | 'DRAFT' | 'SENT' | 'PAID' | 'OVERDUE'>('ALL');

  const mockInvoices = [
    {
      id: 'inv-1',
      number: 'INV-2026-001',
      client: 'Global Tech Corp',
      issueDate: '2026-09-30',
      dueDate: '2026-10-30',
      total: 6600,
      paid: 6600,
      currency: 'USD',
      status: 'PAID',
    },
    {
      id: 'inv-2',
      number: 'INV-2026-002',
      client: 'National Health Services',
      issueDate: '2026-09-15',
      dueDate: '2026-10-15',
      total: 22000,
      paid: 11000,
      currency: 'USD',
      status: 'PARTIALLY_PAID',
    },
    {
      id: 'inv-3',
      number: 'INV-2026-003',
      client: 'Apex Financial Holdings',
      issueDate: '2026-08-01',
      dueDate: '2026-09-01',
      total: 14500,
      paid: 0,
      currency: 'USD',
      status: 'OVERDUE',
    },
  ];

  const filtered = filter === 'ALL' ? mockInvoices : mockInvoices.filter((i) => i.status === filter);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
            <Receipt className="w-5 h-5 text-emerald-400" />
            <span>Invoices & Receivables</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Track customer billing, tax calculations, partial payments, and overdue accounts.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => alert('New Invoice form')}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Generate Invoice</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 text-xs">
        {(['ALL', 'DRAFT', 'SENT', 'PAID', 'OVERDUE'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-3 py-1.5 rounded-lg capitalize font-medium transition-all ${
              filter === tab
                ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {tab.toLowerCase()}
          </button>
        ))}
      </div>

      {/* Invoices Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800/80 bg-slate-900/40 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-3.5 px-4">Invoice #</th>
                <th className="py-3.5 px-4">Client</th>
                <th className="py-3.5 px-4">Issue Date</th>
                <th className="py-3.5 px-4">Due Date</th>
                <th className="py-3.5 px-4">Total Amount</th>
                <th className="py-3.5 px-4">Paid</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((inv) => (
                <tr key={inv.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3.5 px-4 font-mono font-medium text-white">{inv.number}</td>
                  <td className="py-3.5 px-4 text-slate-300 font-medium">{inv.client}</td>
                  <td className="py-3.5 px-4 text-slate-400 font-mono">{inv.issueDate}</td>
                  <td className="py-3.5 px-4 text-slate-400 font-mono">{inv.dueDate}</td>
                  <td className="py-3.5 px-4 text-white font-mono font-semibold">
                    ${inv.total.toLocaleString()} {inv.currency}
                  </td>
                  <td className="py-3.5 px-4 text-emerald-400 font-mono font-medium">
                    ${inv.paid.toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4">
                    <StatusBadge status={inv.status} />
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => alert(`Record payment for ${inv.number}`)}
                      className="text-xs text-brand-400 hover:text-brand-300 font-medium"
                    >
                      Record Payment
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
