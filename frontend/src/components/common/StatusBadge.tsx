import React from 'react';

interface StatusBadgeProps {
  status: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, variant }) => {
  const getStyle = () => {
    const s = status.toUpperCase();
    if (variant === 'success' || s === 'COMPLETED' || s === 'ACTIVE' || s === 'APPROVED' || s === 'PROCESSED' || s === 'READY') {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    }
    if (variant === 'warning' || s === 'IN_PROGRESS' || s === 'REVIEW' || s === 'PARTIAL' || s === 'PENDING') {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    }
    if (variant === 'danger' || s === 'CANCELLED' || s === 'CHURNED' || s === 'FAILED' || s === 'EXPIRED' || s === 'MISSING') {
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    }
    if (variant === 'info' || s === 'PLANNED' || s === 'LEAD' || s === 'DRAFT' || s === 'UPLOADED') {
      return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
    }
    return 'bg-slate-500/10 text-slate-300 border-slate-500/20';
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStyle()}`}>
      <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-current opacity-70"></span>
      {status.replace(/_/g, ' ')}
    </span>
  );
};
