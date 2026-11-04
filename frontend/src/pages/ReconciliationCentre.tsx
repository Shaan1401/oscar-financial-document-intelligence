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
  XCircle,
  Clock,
} from 'lucide-react';
import { api } from '../services/api';
import { Statement, ReconciliationResult } from '../types';
import { SearchableSelect } from '../components/Common/SearchableSelect';

export const ReconciliationCentre: React.FC = () => {
  const { id: paramId } = useParams<{ id?: string }>();
  const [statements, setStatements] = useState<Statement[]>([]);
  const [selectedId, setSelectedId] = useState<string>(paramId || '');
  const [result, setResult] = useState<ReconciliationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [recalcSuccess, setRecalcSuccess] = useState<{
    timestamp: string;
    variance: number;
    status: string;
  } | null>(null);
  const [recalcError, setRecalcError] = useState<string | null>(null);

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
    setRecalcError(null);
    api.getReconciliation(stmtId)
      .then((res) => {
        setResult(res);
        setRecalcSuccess(null);
      })
      .catch((err) => {
        console.error(err);
        setRecalcError(err.message || 'Failed to load statement reconciliation');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (selectedId) {
      loadReconciliation(selectedId);
    }
  }, [selectedId]);

  const handleRunFresh = async () => {
    if (running || !selectedId) return;
    setRunning(true);
    setRecalcError(null);
    try {
      const res = await api.runReconciliation(selectedId);
      setResult(res);
      const timeStr = res.recalculated_at
        ? new Date(res.recalculated_at).toLocaleTimeString()
        : new Date().toLocaleTimeString();
      setRecalcSuccess({
        timestamp: timeStr,
        variance: res.variance,
        status: res.status,
      });
    } catch (err: any) {
      setRecalcError(err.message || 'Reconciliation recalculation failed');
      setRecalcSuccess(null);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Responsive Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80 dark:border-navy-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-[#F4F1E9]">
            Reconciliation Centre
          </h1>
          <p className="text-sm text-slate-500 dark:text-[#9BA8BA] mt-1">
            Mathematical proof of statement integrity, closing balance variance, and running ledger verification.
          </p>
        </div>

        {/* Statement Selector Dropdown & Recalculate CTA */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 w-full sm:w-auto">
          <SearchableSelect
            options={statements.map((s) => ({
              value: s.id,
              label: s.filename,
              sublabel: `${s.bank_name || 'Bank'} (${s.transaction_count ?? 0} txns)`,
              badge: s.reconciliation_status,
            }))}
            value={selectedId}
            onChange={(val) => setSelectedId(val)}
            placeholder="Select Statement..."
            searchPlaceholder="Search statements by name or bank..."
            aria-label="Select Statement"
            className="w-full sm:w-80"
          />

          {/* Real Backend Recalculate Button with Explicit State Management */}
          <button
            onClick={handleRunFresh}
            disabled={running || !selectedId}
            aria-label={running ? 'Recalculating balances...' : 'Recalculate balances'}
            className="inline-flex items-center justify-center space-x-2 rounded-lg bg-navy-900 hover:bg-navy-800 text-gold-400 border border-gold-500/50 px-4 py-2 text-sm font-semibold shadow-sm disabled:opacity-50 transition-colors cursor-pointer shrink-0 dark:bg-navy-800 dark:hover:bg-navy-700"
          >
            <RotateCcw className={`h-4 w-4 ${running ? 'animate-spin' : ''}`} />
            <span>{running ? 'Recalculating balances...' : 'Recalculate'}</span>
          </button>
        </div>
      </div>

      {/* Recalculation Notification State Banners */}
      {recalcSuccess && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/80 p-3.5 dark:border-emerald-900/60 dark:bg-emerald-950/40 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-sm shadow-sm transition-all animate-fadeIn">
          <div className="flex items-center space-x-2 text-emerald-800 dark:text-emerald-200">
            <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
            <span>
              Balances successfully recalculated from database ledger. Status: <strong>{recalcSuccess.status}</strong> (Variance: ₹{recalcSuccess.variance.toFixed(2)}).
            </span>
          </div>
          <div className="flex items-center space-x-1 text-xs text-emerald-700 dark:text-emerald-300">
            <Clock className="h-3.5 w-3.5" />
            <span>Last calculated: {recalcSuccess.timestamp}</span>
          </div>
        </div>
      )}

      {recalcError && (
        <div className="rounded-xl border border-rose-200 bg-rose-50/80 p-3.5 dark:border-rose-900/60 dark:bg-rose-950/40 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-sm shadow-sm transition-all animate-fadeIn">
          <div className="flex items-center space-x-2 text-rose-800 dark:text-rose-200">
            <AlertTriangle className="h-4 w-4 text-rose-500 shrink-0" />
            <span>Recalculation error: {recalcError}</span>
          </div>
          <button
            onClick={handleRunFresh}
            className="text-xs font-bold text-rose-700 dark:text-rose-300 underline hover:no-underline self-start sm:self-auto cursor-pointer"
          >
            Retry Recalculation
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-gold-500 border-t-transparent" />
        </div>
      ) : !result ? (
        <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-sm text-slate-500 dark:border-navy-800 dark:bg-navy-900">
          Select a statement to view its financial balance reconciliation.
        </div>
      ) : (
        <>
          {/* Core Accounting Formula Banner with High-Contrast Elements */}
          <div className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-navy-800 dark:bg-navy-900">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-[#9BA8BA]">
              Core Accounting Reconciliation Law
            </span>
            <div className="mt-3 flex flex-wrap items-center gap-2.5 text-sm font-semibold text-slate-800 dark:text-[#F4F1E9]">
              <span className="rounded-lg bg-white px-3 py-1.5 text-slate-800 border border-slate-200 dark:bg-navy-800 dark:text-slate-200 dark:border-navy-700">
                Opening Balance
              </span>
              <span className="text-emerald-500 font-bold text-base">+</span>
              <span className="rounded-lg bg-emerald-50 px-3 py-1.5 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                Total Credits
              </span>
              <span className="text-rose-500 font-bold text-base">-</span>
              <span className="rounded-lg bg-rose-50 px-3 py-1.5 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
                Total Debits
              </span>
              <span className="text-slate-400 font-bold text-base">=</span>
              <span className="rounded-lg bg-[#FDFBF7] px-3.5 py-1.5 text-navy-950 font-bold border border-gold-400/60 shadow-sm dark:bg-navy-900 dark:text-gold-400 dark:border-gold-500/40">
                Expected Closing Balance
              </span>
            </div>
          </div>

          {/* Balance Cards Grid (23-26px values, tabular numerals, proper contrast) */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-navy-800 dark:bg-navy-900 flex flex-col justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-[#9BA8BA]">Opening Balance</span>
              <p className="mt-2 text-2xl font-bold tabular-nums text-slate-900 dark:text-[#F4F1E9]">
                ₹ {result.opening_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
              <span className="text-xs text-slate-400 dark:text-[#9BA8BA] mt-1 block">Baseline Ledger</span>
            </div>

            <div className="rounded-xl border border-emerald-200/80 bg-white p-4 shadow-sm dark:border-emerald-900/50 dark:bg-navy-900 flex flex-col justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">Total Credits</span>
              <p className="mt-2 text-2xl font-bold tabular-nums text-emerald-600 dark:text-emerald-400">
                ₹ {result.total_credits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
              <span className="text-xs text-emerald-600/80 dark:text-emerald-400/80 mt-1 block">Inflows</span>
            </div>

            <div className="rounded-xl border border-rose-200/80 bg-white p-4 shadow-sm dark:border-rose-900/50 dark:bg-navy-900 flex flex-col justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-rose-700 dark:text-rose-400">Total Debits</span>
              <p className="mt-2 text-2xl font-bold tabular-nums text-rose-600 dark:text-rose-400">
                ₹ {result.total_debits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
              <span className="text-xs text-rose-600/80 dark:text-rose-400/80 mt-1 block">Outflows</span>
            </div>

            {/* Expected Closing Card — Theme-Aware Surface */}
            <div className="rounded-xl border border-gold-400/60 bg-[#FDFBF7] p-4 shadow-sm text-navy-950 dark:border-gold-500/40 dark:bg-navy-900 dark:text-gold-400 flex flex-col justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-gold-800 dark:text-gold-300">Expected Closing Balance</span>
              <p className="mt-2 text-2xl font-bold tabular-nums text-navy-950 dark:text-gold-400">
                ₹ {result.expected_closing_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
              <span className="text-xs text-slate-600 dark:text-gold-400/80 mt-1 block">Calculated Balance</span>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-navy-800 dark:bg-navy-900 flex flex-col justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-[#9BA8BA]">Document Closing Balance</span>
              <p className="mt-2 text-2xl font-bold tabular-nums text-slate-900 dark:text-[#F4F1E9]">
                ₹ {result.actual_closing_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </p>
              <span className="text-xs text-slate-400 dark:text-[#9BA8BA] mt-1 block">Extracted Ledger</span>
            </div>

            <div
              className={`rounded-xl border p-4 shadow-sm flex flex-col justify-between ${
                result.is_reconciled
                  ? 'border-emerald-300 bg-emerald-50/60 dark:border-emerald-800 dark:bg-emerald-950/40'
                  : 'border-rose-300 bg-rose-50/60 dark:border-rose-800 dark:bg-rose-950/40'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`text-xs font-bold uppercase tracking-wider ${
                  result.is_reconciled ? 'text-emerald-800 dark:text-emerald-300' : 'text-rose-800 dark:text-rose-300'
                }`}>
                  Variance
                </span>
                {result.is_reconciled ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-rose-600 dark:text-rose-400" />
                )}
              </div>
              <p
                className={`mt-2 text-2xl font-bold tabular-nums ${
                  result.is_reconciled
                    ? 'text-emerald-700 dark:text-emerald-300'
                    : 'text-rose-700 dark:text-rose-300'
                }`}
              >
                ₹ {result.variance.toFixed(2)}
              </p>
              <span className={`text-xs uppercase font-bold tracking-wider ${
                result.is_reconciled ? 'text-emerald-700 dark:text-emerald-400' : 'text-rose-700 dark:text-rose-400'
              }`}>
                {result.status}
              </span>
            </div>
          </div>

          {/* Running Balance & Exceptions Section */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-navy-800 dark:bg-navy-900">
              <h3 className="text-base font-semibold text-slate-900 dark:text-[#F4F1E9]">
                Step-by-Step Running Ledger Status
              </h3>
              <p className="text-xs text-slate-500 dark:text-[#9BA8BA] mt-0.5">
                Verifies consecutive mathematical increments across all transaction rows
              </p>
              <div className="mt-4 rounded-lg bg-slate-50 p-4 dark:bg-navy-800/80 space-y-2.5 text-sm border border-slate-200/50 dark:border-navy-700/50">
                <div className="flex justify-between">
                  <span className="text-slate-600 dark:text-[#9BA8BA]">Inconsistent Running Balance Rows:</span>
                  <span className="font-semibold tabular-nums text-slate-900 dark:text-[#F4F1E9]">
                    {result.running_balance_errors}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600 dark:text-[#9BA8BA]">Potential Duplicate Candidates:</span>
                  <span className="font-semibold tabular-nums text-slate-900 dark:text-[#F4F1E9]">
                    {result.duplicate_count}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600 dark:text-[#9BA8BA]">Ledger Verification Status:</span>
                  <span className={`font-bold ${result.running_balance_errors === 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
                    {result.running_balance_errors === 0 ? 'Fully Consistent (₹0.00 Running Variance)' : 'Requires Human Review'}
                  </span>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm dark:border-navy-800 dark:bg-navy-900">
              <h3 className="text-base font-semibold text-slate-900 dark:text-[#F4F1E9]">
                Reconciliation Exceptions Log
              </h3>
              <p className="text-xs text-slate-500 dark:text-[#9BA8BA] mt-0.5">
                Automated auditing of variances or mathematical flags
              </p>
              <div className="mt-4 space-y-2.5 text-sm">
                {result.exceptions.length === 0 ? (
                  <div className="flex items-center space-x-2.5 rounded-lg bg-emerald-50/70 p-3.5 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200/60 dark:border-emerald-800/60">
                    <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
                    <span className="font-medium">No mathematical exceptions detected. Document is mathematically verified and 100% reconciled.</span>
                  </div>
                ) : (
                  result.exceptions.map((exc, idx) => (
                    <div
                      key={idx}
                      className="flex items-center space-x-2.5 rounded-lg bg-rose-50 p-3 text-rose-800 dark:bg-rose-950/40 dark:text-rose-300 border border-rose-200/60 dark:border-rose-800/60 font-medium"
                    >
                      <AlertTriangle className="h-4 w-4 shrink-0 text-rose-600 dark:text-rose-400" />
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

export default ReconciliationCentre;
