import React, { useEffect, useState } from 'react';
import {
  Settings as SettingsIcon,
  CheckCircle2,
  AlertTriangle,
  Sun,
  Moon,
  Layers,
  Database,
  ShieldCheck,
  Cpu,
  Scale,
  LineChart,
  FileSpreadsheet,
  Award,
} from 'lucide-react';
import { api } from '../services/api';
import { useTheme } from '../context/ThemeContext';

export const Settings: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [ocrStatus, setOcrStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getHealth()
      .then((data) => setOcrStatus(data.ocr_status))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
          System Settings &amp; Platform Identity
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Configure engine parameters, inspect OCR readiness, and review OSCAR brand specifications.
        </p>
      </div>

      {/* =========================================================================
          EXPLICIT BRAND IDENTITY & ABOUT OSCAR
         ========================================================================= */}
      <div className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm dark:border-slate-800/90 dark:bg-slate-900 space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center space-x-3.5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600 text-white font-black text-2xl shadow-sm ring-2 ring-brand-500/30">
              O
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-black tracking-tight text-slate-900 dark:text-white">
                  OSCAR
                </h2>
                <span className="rounded-md bg-brand-50 px-2 py-0.5 text-xs font-bold text-brand-700 dark:bg-brand-950 dark:text-brand-300 border border-brand-200 dark:border-brand-800">
                  v1.0.0 Enterprise
                </span>
              </div>
              <p className="text-xs font-bold text-brand-600 dark:text-brand-400">
                Financial Document Intelligence
              </p>
            </div>
          </div>

          <div className="rounded-xl bg-slate-50 px-4 py-2.5 text-right dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Official Tagline</span>
            <p className="text-xs font-bold italic text-slate-700 dark:text-slate-200">
              "Every transaction deserves an explanation."
            </p>
          </div>
        </div>

        {/* Complete Full-Form Expansion */}
        <div className="rounded-xl bg-brand-50/50 p-4 dark:bg-brand-950/20 border border-brand-200/60 dark:border-brand-800/40">
          <span className="text-[10px] font-bold uppercase tracking-wider text-brand-700 dark:text-brand-300">
            Complete Full-Form Specification
          </span>
          <p className="mt-1 text-base md:text-lg font-black text-slate-900 dark:text-white tracking-wide">
            Operational Statement Classification, Analysis &amp; Reconciliation
          </p>
          <p className="mt-1 text-xs text-slate-600 dark:text-slate-400">
            Designed to solve automated parsing, multi-layout bank extraction, explainable offline transaction categorization, and rigorous double-entry mathematical reconciliation.
          </p>
        </div>

        {/* 5-Card Letter Mapping Grid */}
        <div className="space-y-2">
          <span className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
            Brand Acronym Decomposition (Letter Mapping)
          </span>

          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 pt-1">
            <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 dark:border-slate-800 dark:bg-slate-800/50 flex flex-col justify-between">
              <div>
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white font-black text-sm">
                  O
                </span>
                <p className="font-bold text-xs text-slate-900 dark:text-white mt-2">Operational</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-snug">
                  Mission-critical accounting ledger, minor-unit arithmetic, and immutable audit logs.
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 dark:border-slate-800 dark:bg-slate-800/50 flex flex-col justify-between">
              <div>
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white font-black text-sm">
                  S
                </span>
                <p className="font-bold text-xs text-slate-900 dark:text-white mt-2">Statement</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-snug">
                  Multi-bank statement ingestion (Layouts A, B, C, digital text and scanned OCR).
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 dark:border-slate-800 dark:bg-slate-800/50 flex flex-col justify-between">
              <div>
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-600 text-white font-black text-sm">
                  C
                </span>
                <p className="font-bold text-xs text-slate-900 dark:text-white mt-2">Classification</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-snug">
                  Explainable hybrid engine: deterministic rules + dual TF-IDF Logistic Regression.
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 dark:border-slate-800 dark:bg-slate-800/50 flex flex-col justify-between">
              <div>
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-teal-600 text-white font-black text-sm">
                  A
                </span>
                <p className="font-bold text-xs text-slate-900 dark:text-white mt-2">Analysis</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-snug">
                  Deep analytics: Pareto merchant curve, payment channels, and cashflow intelligence.
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5 dark:border-slate-800 dark:bg-slate-800/50 flex flex-col justify-between">
              <div>
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600 text-white font-black text-sm">
                  R
                </span>
                <p className="font-bold text-xs text-slate-900 dark:text-white mt-2">Reconciliation</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-snug">
                  Mathematical proof: Opening + Credits - Debits = Closing with zero variance.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Theme Preferences */}
      <div className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900 space-y-3">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
          Interface Appearance (Light / Dark Mode)
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Persistent application-wide theme synchronized across sessions via local storage.
        </p>
        <div className="grid grid-cols-2 gap-3 max-w-sm pt-2">
          <button
            onClick={() => setTheme('light')}
            className={`flex items-center justify-center space-x-2 rounded-lg border p-3 text-xs font-bold transition cursor-pointer ${
              theme === 'light'
                ? 'border-brand-600 bg-brand-50 text-brand-700 dark:bg-brand-950/60 shadow-sm'
                : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'
            }`}
          >
            <Sun className="h-4 w-4 text-amber-500" />
            <span>Light Theme</span>
          </button>

          <button
            onClick={() => setTheme('dark')}
            className={`flex items-center justify-center space-x-2 rounded-lg border p-3 text-xs font-bold transition cursor-pointer ${
              theme === 'dark'
                ? 'border-brand-600 bg-brand-50 text-brand-700 dark:bg-brand-950/60 dark:text-brand-300 shadow-sm'
                : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'
            }`}
          >
            <Moon className="h-4 w-4 text-brand-400" />
            <span>Dark Theme</span>
          </button>
        </div>
      </div>

      {/* Tesseract OCR Diagnostics */}
      <div className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Tesseract OCR Windows Engine Diagnostics
          </h3>
          {ocrStatus && (
            <span
              className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                ocrStatus.available
                  ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                  : 'bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
              }`}
            >
              {ocrStatus.available ? 'OCR READY' : 'OCR NOT FOUND (TEXT ONLY)'}
            </span>
          )}
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Required only for scanned bitmap PDF statements; text-based digital PDFs extract directly at 100% fidelity without Tesseract.
        </p>

        {loading ? (
          <div className="text-xs text-slate-400">Checking Tesseract status...</div>
        ) : ocrStatus ? (
          <div className="rounded-lg bg-slate-50 p-4 text-xs dark:bg-slate-800/60 space-y-2 border border-slate-200/60 dark:border-slate-700/60">
            <div className="flex justify-between">
              <span className="text-slate-500">Detected Executable:</span>
              <span className="font-mono text-slate-800 dark:text-slate-200 font-semibold">
                {ocrStatus.executable_path || 'None (Path probe fallback active)'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Engine Diagnostics:</span>
              <span className="text-slate-800 dark:text-slate-200 font-medium">{ocrStatus.message}</span>
            </div>
            {!ocrStatus.available && (
              <div className="mt-3 rounded border border-amber-200 bg-amber-50/60 p-3 text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-300">
                <p className="font-semibold mb-1">Evaluator Setup Instructions:</p>
                <p>{ocrStatus.instructions}</p>
              </div>
            )}
          </div>
        ) : null}
      </div>

      {/* Supported Bank Layout Profiles */}
      <div className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900 space-y-3">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
          Active Multi-Layout Profiles
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Profiles supported and benchmarked by the dynamic table parser
        </p>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 text-xs pt-1">
          <div className="rounded-lg border border-slate-200/80 p-3.5 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
            <span className="font-bold text-brand-600 dark:text-brand-400">Layout A</span>
            <p className="font-semibold text-slate-800 dark:text-slate-200 mt-1">Separate Debit / Credit</p>
            <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-0.5">
              Standard 5-column layout with distinct Debit, Credit, and Running Balance columns.
            </p>
          </div>

          <div className="rounded-lg border border-slate-200/80 p-3.5 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
            <span className="font-bold text-amber-600 dark:text-amber-400">Layout B</span>
            <p className="font-semibold text-slate-800 dark:text-slate-200 mt-1">Combined Amount (DR/CR)</p>
            <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-0.5">
              Single transaction amount column with explicit "DR" / "CR" indicators or sign conventions.
            </p>
          </div>

          <div className="rounded-lg border border-slate-200/80 p-3.5 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
            <span className="font-bold text-emerald-600 dark:text-emerald-400">Layout C</span>
            <p className="font-semibold text-slate-800 dark:text-slate-200 mt-1">Multi-Page &amp; Wrapped</p>
            <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-0.5">
              Alternate headers (Value Date, Particulars, Withdrawals, Deposits), multiline row wrapping.
            </p>
          </div>
        </div>
      </div>

      {/* Local-First Architecture Details */}
      <div className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-slate-800/90 dark:bg-slate-900 space-y-3">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2">
          <Database className="h-4 w-4 text-brand-600" />
          <span>Local-First Deployment Architecture &amp; Privacy Guarantees</span>
        </h3>
        <div className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4 pt-1">
          <div className="rounded bg-slate-50 p-2.5 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-slate-400 text-[10px]">Backend Server</span>
            <p className="font-mono font-bold text-slate-800 dark:text-slate-200">127.0.0.1:8000</p>
          </div>
          <div className="rounded bg-slate-50 p-2.5 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-slate-400 text-[10px]">Frontend UI</span>
            <p className="font-mono font-bold text-slate-800 dark:text-slate-200">localhost:5173</p>
          </div>
          <div className="rounded bg-slate-50 p-2.5 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-slate-400 text-[10px]">Database</span>
            <p className="font-mono font-bold text-slate-800 dark:text-slate-200">SQLite (WAL mode)</p>
          </div>
          <div className="rounded bg-slate-50 p-2.5 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
            <span className="text-slate-400 text-[10px]">External APIs</span>
            <p className="font-mono font-bold text-emerald-600 dark:text-emerald-400">Zero (100% Offline)</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
