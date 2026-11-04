import React, { useEffect, useState } from 'react';
import { Sun, Moon, UploadCloud, CheckCircle2, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import { api } from '../../services/api';

export const Navbar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [ocrStatus, setOcrStatus] = useState<{ available: boolean; message: string } | null>(null);

  useEffect(() => {
    api.getHealth()
      .then((data) => {
        if (data.ocr_status) {
          setOcrStatus({
            available: data.ocr_status.available,
            message: data.ocr_status.available ? 'OCR Engine Ready' : 'Text Extraction Active',
          });
        }
      })
      .catch(() => {
        setOcrStatus(null);
      });
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200/90 bg-white/95 px-6 backdrop-blur dark:border-navy-800 dark:bg-navy-900/95 transition-colors">
      <div className="flex items-center space-x-3 min-w-0">
        <Link to="/" className="flex items-center space-x-3 group min-w-0">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-navy-900 border border-gold-400/40 text-gold-400 font-black tracking-wider shadow-sm group-hover:border-gold-400 transition">
            O
          </div>
          <div className="min-w-0">
            <div className="flex items-baseline space-x-2 flex-wrap">
              <span className="font-extrabold text-lg text-slate-900 dark:text-[#F4F1E9] tracking-tight shrink-0">OSCAR</span>
              <span className="hidden lg:inline text-xs font-semibold text-slate-600 dark:text-[#9BA8BA] truncate">
                — Operational Statement Classification, Analysis & Reconciliation
              </span>
            </div>
            <p className="text-[10.5px] font-medium text-slate-500 dark:text-[#9BA8BA] tracking-wide truncate">
              Financial Document Intelligence
            </p>
          </div>
        </Link>
      </div>

      <div className="flex items-center space-x-3">
        {/* Tesseract OCR Engine Status Indicator */}
        {ocrStatus && (
          <div
            className={`hidden sm:flex items-center space-x-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
              ocrStatus.available
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                : 'bg-slate-100 text-slate-700 border border-slate-200 dark:bg-navy-800 dark:text-slate-300 dark:border-navy-700'
            }`}
            title={ocrStatus.message}
          >
            {ocrStatus.available ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
            ) : (
              <ShieldCheck className="h-3.5 w-3.5 text-cobalt-500" />
            )}
            <span>{ocrStatus.message}</span>
          </div>
        )}

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle Theme"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} theme`}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:border-navy-700 dark:bg-navy-800 dark:text-slate-300 dark:hover:bg-navy-700 dark:hover:text-[#F4F1E9] transition-colors cursor-pointer"
        >
          {theme === 'dark' ? <Sun className="h-4 w-4 text-gold-400" /> : <Moon className="h-4 w-4 text-navy-800" />}
        </button>

        {/* Quick Upload CTA */}
        <Link
          to="/upload"
          className="inline-flex items-center space-x-1.5 rounded-lg bg-gold-400 hover:bg-gold-500 text-navy-950 px-3.5 py-1.5 text-xs font-bold shadow-sm transition-colors"
        >
          <UploadCloud className="h-4 w-4" />
          <span>Upload Statement</span>
        </Link>
      </div>
    </header>
  );
};
