import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UploadCloud,
  FileSpreadsheet,
  ListOrdered,
  AlertCircle,
  Scale,
  LineChart,
  Cpu,
  Download,
  History,
  Settings as SettingsIcon,
  ShieldCheck,
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Upload Statement', path: '/upload', icon: UploadCloud },
  { name: 'Statement History', path: '/statements', icon: FileSpreadsheet },
  { name: 'Transaction Explorer', path: '/transactions', icon: ListOrdered },
  { name: 'Review & Exceptions', path: '/reviews', icon: AlertCircle },
  { name: 'Reconciliation Centre', path: '/reconciliation', icon: Scale },
  { name: 'Financial Analytics', path: '/analytics', icon: LineChart },
  { name: 'Classification Insights', path: '/classification', icon: Cpu },
  { name: 'Export Centre', path: '/exports', icon: Download },
  { name: 'Audit Trail', path: '/audit', icon: History },
  { name: 'Settings', path: '/settings', icon: SettingsIcon },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="hidden md:flex w-64 flex-col border-r border-slate-200/90 bg-white dark:border-navy-800 dark:bg-navy-900 justify-between select-none transition-colors">
      <div className="flex flex-col py-4">
        {/* Brand Header */}
        <div className="px-5 pb-4 mb-2 border-b border-slate-100 dark:border-navy-800">
          <div className="flex items-center space-x-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy-950 border border-gold-400/40 text-gold-400 font-bold text-sm shadow-sm">
              O
            </div>
            <div>
              <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-[#F4F1E9]">OSCAR</span>
              <p className="text-[10px] font-medium text-slate-500 dark:text-[#9BA8BA]">
                Financial Document Intelligence
              </p>
            </div>
          </div>
        </div>

        <div className="px-5 mb-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-navy-400">
            Navigation
          </span>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1 px-3">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center space-x-3 rounded-lg px-3 py-2 text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-gold-400/10 text-gold-600 dark:bg-gold-400/15 dark:text-gold-400 font-bold border-l-2 border-gold-400 shadow-sm'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-[#9BA8BA] dark:hover:bg-navy-800 dark:hover:text-[#F4F1E9]'
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Sidebar Footer with Tagline & System Status */}
      <div className="border-t border-slate-200/80 p-4 dark:border-navy-800">
        <div className="rounded-lg bg-slate-50 p-3 dark:bg-navy-800/80 border border-slate-200/60 dark:border-navy-700/60 space-y-1">
          <p className="text-[11px] font-medium italic text-slate-700 dark:text-[#F4F1E9]">
            "Every transaction deserves an explanation."
          </p>
          <div className="flex items-center justify-between pt-1 text-[10px] text-slate-400 dark:text-[#9BA8BA]">
            <span className="flex items-center space-x-1">
              <ShieldCheck className="h-3 w-3 text-emerald-500" />
              <span>Offline Verified</span>
            </span>
            <span className="font-mono">v1.0.0</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
