import React from 'react';
import { Sparkles, Eye, Upload, CheckCircle2, FileText, ArrowRight } from 'lucide-react';

export type ActionType = 'Use' | 'View' | 'Generate' | 'Upload' | 'Review' | 'Approve';

interface ActionCardProps {
  title: string;
  description: string;
  type: ActionType;
  metadata?: string;
  badge?: string;
  onClick: () => void;
  disabled?: boolean;
}

export const ActionCard: React.FC<ActionCardProps> = ({
  title,
  description,
  type,
  metadata,
  badge,
  onClick,
  disabled = false,
}) => {
  const getIcon = () => {
    switch (type) {
      case 'Generate':
        return <Sparkles className="w-4 h-4 text-purple-400" />;
      case 'View':
        return <Eye className="w-4 h-4 text-sky-400" />;
      case 'Upload':
        return <Upload className="w-4 h-4 text-emerald-400" />;
      case 'Review':
        return <FileText className="w-4 h-4 text-amber-400" />;
      case 'Approve':
        return <CheckCircle2 className="w-4 h-4 text-teal-400" />;
      case 'Use':
      default:
        return <ArrowRight className="w-4 h-4 text-blue-400" />;
    }
  };

  const getButtonClass = () => {
    switch (type) {
      case 'Generate':
        return 'bg-purple-600 hover:bg-purple-500 text-white';
      case 'Approve':
        return 'bg-emerald-600 hover:bg-emerald-500 text-white';
      case 'Review':
        return 'bg-amber-600 hover:bg-amber-500 text-white';
      case 'Upload':
        return 'bg-slate-700 hover:bg-slate-600 text-slate-100';
      case 'View':
        return 'bg-sky-600 hover:bg-sky-500 text-white';
      default:
        return 'bg-blue-600 hover:bg-blue-500 text-white';
    }
  };

  return (
    <div className="glass-card rounded-xl p-4 transition-all duration-200 hover:border-slate-600 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="p-1.5 rounded-lg bg-slate-800/80 border border-slate-700/50">
              {getIcon()}
            </span>
            <h4 className="text-sm font-semibold text-slate-200">{title}</h4>
          </div>
          {badge && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
              {badge}
            </span>
          )}
        </div>
        <p className="text-xs text-slate-400 mb-3">{description}</p>
        {metadata && <p className="text-[11px] text-slate-500 font-mono mb-3">{metadata}</p>}
      </div>

      <button
        onClick={onClick}
        disabled={disabled}
        className={`w-full py-2 px-3 rounded-lg text-xs font-medium flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${getButtonClass()}`}
      >
        <span>{type}</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
