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
    <aside className="hidden md:flex w-64 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 justify-between">
      <div className="flex flex-col py-4">
        <div className="px-5 mb-3">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Platform Navigation
          </span>
        </div>

        <nav className="space-y-1 px-3">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center space-x-3 rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/60 dark:text-brand-300 font-semibold'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200'
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

      <div className="border-t border-slate-200 p-4 dark:border-slate-800">
        <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60">
          <p className="text-[11px] font-medium italic text-slate-600 dark:text-slate-300">
            "Every transaction deserves an explanation."
          </p>
          <p className="mt-1 text-[10px] text-slate-400 dark:text-slate-500">
            OSCAR • Local-First Intelligence
          </p>
        </div>
      </div>
    </aside>
  );
};

