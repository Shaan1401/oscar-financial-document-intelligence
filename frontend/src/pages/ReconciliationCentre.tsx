import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Scale,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  FileSpreadsheet,
  ArrowRight,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import { api } from '../services/api';
import { Statement, ReconciliationResult } from '../types';

export const ReconciliationCentre: React.FC = () => {
  const { id: paramId } = useParams<{ id?: string }>();
  const [statements, setStatements] = useState<Statement[]>([]);
  const [selectedId, setSelectedId] = useState<string>(paramId || '');
  const [result, setResult] = useState<ReconciliationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    api.getStatements().then((list) => {
      setStatements(list);
      if (!selectedId && list.length > 0) {
        setSelectedId(list[0].id);
      }
    });
  }, []);

  const loadReconciliation = (stmtId: string) => {
    if (!stmtId) return;
    setLoading(true);
    api.getReconciliation(stmtId)
      .then(setResult)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (selectedId) {
      loadReconciliation(selectedId);
    }
  }, [selectedId]);

  const handleRunFresh = async () => {
    if (!selectedId) return;
    setRunning(true);
    try {
      const res = await api.runReconciliation(selectedId);
      setResult(res);
    } catch (err: any) {
      alert(`Reconciliation run failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Reconciliation Centre
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Mathematical proof of statement integrity, closing balance variance, and running ledger verification.
          </p>
        </div>

        {/* Statement Selector Dropdown */}
        <div className="flex items-center space-x-3">
          <select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-900 shadow-sm focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
          >
            {statements.map((s) => (
              <option key={s.id} value={s.id}>
                {s.filename} ({s.bank_name || 'Bank'})
              </option>
            ))}
          </select>

          <button
            onClick={handleRunFresh}
            disabled={running || !selectedId}
            className="inline-flex items-center space-x-1.5 rounded-lg bg-brand-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow hover:bg-brand-700 disabled:opacity-50 transition"
          >
            <RotateCcw className={`h-3.5 w-3.5 ${running ? 'animate-spin' : ''}`} />
            <span>Recalculate</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
        </div>
      ) : !result ? (
        <div className="p-12 text-center text-xs text-slate-500">
          Select a statement to view its financial balance reconciliation.
        </div>
      ) : (
        <>
          {/* Accounting Formula Banner */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              Core Accounting Reconciliation Law
            </span>
            <div className="mt-2 flex flex-wrap items-center gap-2 font-mono text-sm font-bold text-slate-800 dark:text-slate-200">
              <span className="rounded bg-slate-100 px-2.5 py-1 dark:bg-slate-800">
                Opening Balance
              </span>
              <span className="text-emerald-500">+</span>
              <span className="rounded bg-emerald-50 px-2.5 py-1 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                Total Credits
              </span>
              <span className="text-rose-500">-</span>
              <span className="rounded bg-rose-50 px-2.5 py-1 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">
                Total Debits
              </span>
              <span className="text-slate-400">=</span>
              <span className="rounded bg-brand-50 px-2.5 py-1 text-brand-700 dark:bg-brand-950/60 dark:text-brand-300">
                Expected Closing Balance
              </span>
            </div>
          </div>

          {/* Balance Cards Grid */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <span className="text-[11px] text-slate-500">Opening Balance</span>
              <p className="mt-2 text-lg font-bold font-mono text-slate-900 dark:text-white">
                ₹ {result.opening_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <span className="text-[11px] text-slate-500">Total Credits (+)</span>
              <p className="mt-2 text-lg font-bold font-mono text-emerald-600 dark:text-emerald-400">
                ₹ {result.total_credits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <span className="text-[11px] text-slate-500">Total Debits (-)</span>
              <p className="mt-2 text-lg font-bold font-mono text-rose-600 dark:text-rose-400">
                ₹ {result.total_debits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <span className="text-[11px] text-slate-500">Expected Closing</span>
              <p className="mt-2 text-lg font-bold font-mono text-slate-900 dark:text-white">
                ₹ {result.expected_closing_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <span className="text-[11px] text-slate-500">Document Closing</span>
              <p className="mt-2 text-lg font-bold font-mono text-slate-900 dark:text-white">
                ₹ {result.actual_closing_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
            </div>

            <div
              className={`rounded-xl border p-4 shadow-sm ${
                result.is_reconciled
                  ? 'border-emerald-200 bg-emerald-50/50 dark:border-emerald-900/60 dark:bg-emerald-950/30'
                  : 'border-rose-200 bg-rose-50/50 dark:border-rose-900/60 dark:bg-rose-950/30'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-300">Variance</span>
                {result.is_reconciled ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-rose-600" />
                )}
              </div>
              <p
                className={`mt-2 text-lg font-bold font-mono ${
                  result.is_reconciled
                    ? 'text-emerald-700 dark:text-emerald-300'
                    : 'text-rose-700 dark:text-rose-300'
                }`}
              >
                ₹ {result.variance.toFixed(2)}
              </p>
              <span className="text-[10px] uppercase font-bold tracking-wider">
                {result.status}
              </span>
            </div>
          </div>

          {/* Running Balance & Exceptions Section */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                Step-by-Step Running Ledger Status
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Verifies consecutive mathematical increments across all transaction rows
              </p>
              <div className="mt-4 rounded-lg bg-slate-50 p-4 dark:bg-slate-800/60 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Inconsistent Running Balance Rows:</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-white">
                    {result.running_balance_errors}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Potential Duplicate Candidates:</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-white">
                    {result.duplicate_count}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Ledger Verification Status:</span>
                  <span className={`font-semibold ${result.running_balance_errors === 0 ? 'text-emerald-600' : 'text-amber-600'}`}>
                    {result.running_balance_errors === 0 ? 'Fully Consistent' : 'Requires Review'}
                  </span>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                Reconciliation Exceptions Log
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Automated auditing of variances or mathematical flags
              </p>
              <div className="mt-4 space-y-2 text-xs">
                {result.exceptions.length === 0 ? (
                  <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 py-3">
                    <CheckCircle2 className="h-4 w-4 shrink-0" />
                    <span>No mathematical exceptions detected. Document is fully reconciled.</span>
                  </div>
                ) : (
                  result.exceptions.map((exc, idx) => (
                    <div
                      key={idx}
                      className="flex items-center space-x-2 rounded-lg bg-rose-50 p-2.5 text-rose-800 dark:bg-rose-950/40 dark:text-rose-300"
                    >
                      <AlertTriangle className="h-4 w-4 shrink-0 text-rose-600" />
                      <span>{exc}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

