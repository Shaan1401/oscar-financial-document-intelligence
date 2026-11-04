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
    <aside className="hidden md:flex w-64 flex-col border-r border-slate-200/90 bg-white dark:border-slate-800/90 dark:bg-slate-900 justify-between select-none">
      <div className="flex flex-col py-4">
        {/* Brand Header & Complete Full Form Identity */}
        <div className="px-5 pb-3.5 mb-2 border-b border-slate-100 dark:border-slate-800/80">
          <div className="flex items-center space-x-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white font-bold text-sm shadow-sm ring-1 ring-brand-500/30">
              O
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-white">OSCAR</span>
                <span className="rounded bg-brand-50 px-1.5 py-0.2 text-[9px] font-bold text-brand-700 dark:bg-brand-950 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
                  PRO
                </span>
              </div>
              <p className="text-[10px] font-semibold text-slate-500 dark:text-slate-400">
                Financial Document Intelligence
              </p>
            </div>
          </div>

          {/* Full Acronym Expansion Block */}
          <div className="mt-2.5 rounded-lg bg-slate-50 p-2 text-[10px] text-slate-600 dark:bg-slate-800/60 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700/60 leading-snug">
            <div className="font-bold text-brand-600 dark:text-brand-400 tracking-wider text-[9px] uppercase">
              O • S • C • A • R
            </div>
            <div className="text-[9.5px] text-slate-600 dark:text-slate-300 font-medium mt-0.5">
              Operational Statement Classification, Analysis &amp; Reconciliation
            </div>
          </div>
        </div>

        <div className="px-5 mb-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Workstation Modules
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
                      ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/70 dark:text-brand-300 font-bold border-l-2 border-brand-600 dark:border-brand-500 shadow-xs'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-slate-200'
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
      <div className="border-t border-slate-200/80 p-4 dark:border-slate-800/80">
        <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 space-y-1">
          <p className="text-[11px] font-semibold italic text-slate-700 dark:text-slate-200">
            "Every transaction deserves an explanation."
          </p>
          <div className="flex items-center justify-between pt-1 text-[10px] text-slate-400 dark:text-slate-500">
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
