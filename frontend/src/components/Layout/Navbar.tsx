import React, { useEffect, useState } from 'react';
import { Sun, Moon, UploadCloud, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
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
            message: data.ocr_status.available ? 'OCR Engine Active' : 'OCR Unavailable (Text PDF Only)',
          });
        }
      })
      .catch(() => {
        setOcrStatus(null);
      });
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/90 px-6 backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
      <div className="flex items-center space-x-3">
        <Link to="/" className="flex items-center space-x-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white font-bold tracking-wider shadow-sm">
            O
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-slate-900 dark:text-white tracking-tight">OSCAR</span>
              <span className="rounded bg-brand-100 px-1.5 py-0.5 text-[10px] font-semibold text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                v1.0.0
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">Financial Document Intelligence</p>
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
                : 'bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800'
            }`}
            title={ocrStatus.message}
          >
            {ocrStatus.available ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
            )}
            <span>{ocrStatus.message}</span>
          </div>
        )}

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle Theme"
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white transition-colors"
        >
          {theme === 'dark' ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4" />}
        </button>

        {/* Quick Upload CTA */}
        <Link
          to="/upload"
          className="inline-flex items-center space-x-1.5 rounded-lg bg-brand-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow hover:bg-brand-700 transition-colors"
        >
          <UploadCloud className="h-4 w-4" />
          <span>Upload Statement</span>
        </Link>
      </div>
    </header>
  );
};

