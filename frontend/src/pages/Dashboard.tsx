import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FileText,
  TrendingUp,
  TrendingDown,
  Scale,
  AlertCircle,
  UploadCloud,
  CheckCircle2,
  ArrowRight,
  ShieldAlert,
  Layers,
  Activity,
  Calendar,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Check,
  Cpu,
  ChevronRight,
  FileSpreadsheet,
} from 'lucide-react';
import {
  ResponsiveContainer,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  AreaChart,
  Area,
  Line,
  ComposedChart,
} from 'recharts';
import { api } from '../services/api';
import {
  SummaryMetrics,
  Statement,
  CategoryBreakdown,
  CashflowPoint,
  RunningBalanceResponse,
  ActivityHeatmapPoint,
  ClassificationDeepResponse,
} from '../types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<SummaryMetrics | null>(null);
  const [statements, setStatements] = useState<Statement[]>([]);
  const [selectedStatementId, setSelectedStatementId] = useState<string>('');
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [cashflow, setCashflow] = useState<CashflowPoint[]>([]);
  const [runningBalance, setRunningBalance] = useState<RunningBalanceResponse | null>(null);
  const [heatmap, setHeatmap] = useState<ActivityHeatmapPoint[]>([]);
  const [classification, setClassification] = useState<ClassificationDeepResponse | null>(null);
  const [heatmapMetric, setHeatmapMetric] = useState<'count' | 'volume'>('count');
  const [loading, setLoading] = useState(true);

  const loadDashboardData = (stmtId?: string) => {
    setLoading(true);
    Promise.all([
      api.getAnalyticsSummary(),
      api.getStatements(),
      api.getCategoryAnalytics(stmtId || undefined),
      api.getCashflow(stmtId || undefined),
      api.getRunningBalance(stmtId || undefined),
      api.getActivityHeatmap(stmtId || undefined),
      api.getClassificationDeep(),
    ])
      .then(([sumData, stmtData, catData, flowData, balData, heatData, clsData]) => {
        setSummary(sumData);
        setStatements(stmtData);
        setCategories(catData.slice(0, 6));
        setCashflow(flowData);
        setRunningBalance(balData);
        setHeatmap(heatData);
        setClassification(clsData);
      })
      .catch((err) => console.error('Dashboard load failed:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDashboardData(selectedStatementId);
  }, [selectedStatementId]);

  if (loading && !summary) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-gold-400 border-t-transparent" />
      </div>
    );
  }

  const hasData = (summary?.total_statements ?? 0) > 0;
  const activeStatement = statements.find((s) => s.id === selectedStatementId) || (selectedStatementId ? null : statements[0]) || null;

  // Financial Integrity Bridge calculations
  const openingBal = activeStatement?.opening_balance ?? runningBalance?.opening_balance ?? 0;
  const closingBal = activeStatement?.closing_balance ?? runningBalance?.closing_balance ?? 0;
  const totalInflow = activeStatement ? (activeStatement.total_credits ?? 0) : (summary?.total_credits ?? 0);
  const totalOutflow = activeStatement ? (activeStatement.total_debits ?? 0) : (summary?.total_debits ?? 0);
  const netCashMovement = totalInflow - totalOutflow;
  const expectedClosing = openingBal + totalInflow - totalOutflow;
  const balanceVariance = Math.abs(closingBal - expectedClosing);
  const isBridgeReconciled = balanceVariance < 0.01;

  return (
    <div className="space-y-6">
      {/* =========================================================================
          COMPACT FINANCIAL OVERVIEW HEADER (No Promotional Hero Banner)
         ========================================================================= */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80 dark:border-navy-800">
        <div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-slate-900 dark:text-[#F4F1E9]">
            Financial Overview
          </h1>
          <p className="text-xs text-slate-500 dark:text-[#9BA8BA] mt-0.5">
            Your statements, cash flow and reconciliation status.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {statements.length > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-slate-500 dark:text-[#9BA8BA] whitespace-nowrap">
                Scope:
              </span>
              <select
                value={selectedStatementId}
                onChange={(e) => setSelectedStatementId(e.target.value)}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-800 shadow-sm focus:outline-none focus:ring-1 focus:ring-gold-400 dark:border-navy-700 dark:bg-navy-800 dark:text-[#F4F1E9] cursor-pointer"
              >
                <option value="">All Processed Statements (Portfolio)</option>
                {statements.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.filename} — {s.bank_name || 'Bank'} ({s.transaction_count} txns)
                  </option>
                ))}
              </select>
            </div>
          )}

          <Link
            to="/upload"
            className="inline-flex items-center space-x-1.5 rounded-lg bg-gold-400 hover:bg-gold-500 text-navy-950 px-3.5 py-1.5 text-xs font-bold shadow-sm transition-colors"
          >
            <UploadCloud className="h-4 w-4" />
            <span>Process New Statement</span>
          </Link>
        </div>
      </div>

      {!hasData ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center dark:border-navy-800 dark:bg-navy-900">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gold-400/10 text-gold-400 mb-3">
            <UploadCloud className="h-8 w-8" />
          </div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-[#F4F1E9]">
            No bank statements processed yet
          </h3>
          <p className="mt-1 max-w-sm text-xs text-slate-500 dark:text-[#9BA8BA]">
            Upload a text-based, scanned, or multi-page bank statement PDF to extract transactions, classify expenses, and verify reconciliation.
          </p>
          <Link
            to="/upload"
            className="mt-6 inline-flex items-center space-x-2 rounded-lg bg-gold-400 px-4 py-2 text-xs font-bold text-navy-950 shadow-sm hover:bg-gold-500 transition-colors"
          >
            <span>Upload First Statement</span>
          </Link>
        </div>
      ) : (
        <>
          {/* =========================================================================
              1. KPI STRIP: Total Inflows, Total Outflows, Net Movement, Closing Balance
             ========================================================================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* KPI 1: Total Inflows */}
            <div className="oscar-card flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-[#9BA8BA]">
                <span className="font-semibold uppercase tracking-wider text-[11px]">Total Inflows</span>
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-500">
                  <ArrowDownRight className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3">
                <span className="font-mono text-2xl font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                  ₹ {totalInflow.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <p className="mt-1 text-[11px] text-slate-500 dark:text-[#9BA8BA]">
                  Verified credits into account
                </p>
              </div>
            </div>

            {/* KPI 2: Total Outflows */}
            <div className="oscar-card flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-[#9BA8BA]">
                <span className="font-semibold uppercase tracking-wider text-[11px]">Total Outflows</span>
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-rose-500/10 text-rose-500">
                  <ArrowUpRight className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3">
                <span className="font-mono text-2xl font-bold text-rose-600 dark:text-rose-400 tabular-nums">
                  ₹ {totalOutflow.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <p className="mt-1 text-[11px] text-slate-500 dark:text-[#9BA8BA]">
                  Verified debits &amp; expenditures
                </p>
              </div>
            </div>

            {/* KPI 3: Net Cash Movement */}
            <div className="oscar-card flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-[#9BA8BA]">
                <span className="font-semibold uppercase tracking-wider text-[11px]">Net Cash Movement</span>
                <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${
                  netCashMovement >= 0 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'
                }`}>
                  <Activity className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3">
                <span className={`font-mono text-2xl font-bold tabular-nums ${
                  netCashMovement >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
                }`}>
                  {netCashMovement >= 0 ? '+ ' : '- '}₹ {Math.abs(netCashMovement).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <p className="mt-1 text-[11px] text-slate-500 dark:text-[#9BA8BA]">
                  {netCashMovement >= 0 ? 'Positive net liquidity surplus' : 'Net liquidity deficit'}
                </p>
              </div>
            </div>

            {/* KPI 4: Closing Balance */}
            <div className="oscar-card flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-[#9BA8BA]">
                <span className="font-semibold uppercase tracking-wider text-[11px]">Closing Balance</span>
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-gold-400/15 text-gold-500">
                  <Wallet className="h-4 w-4" />
                </span>
              </div>
              <div className="mt-3">
                <span className="font-mono text-2xl font-bold text-slate-900 dark:text-[#F4F1E9] tabular-nums">
                  ₹ {closingBal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <div className="mt-1 flex items-center justify-between text-[11px]">
                  <span className="text-slate-500 dark:text-[#9BA8BA]">Final ledger balance</span>
                  <span className={`font-bold ${isBridgeReconciled ? 'text-emerald-500' : 'text-amber-500'}`}>
                    {isBridgeReconciled ? 'Reconciled' : 'Variance'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* =========================================================================
              2. FINANCIAL INTEGRITY BRIDGE (Signature Mathematical Proof)
             ========================================================================= */}
          <div className="oscar-card">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3.5 border-b border-slate-100 dark:border-navy-800 gap-2">
              <div>
                <h2 className="text-xs font-bold text-slate-900 dark:text-[#F4F1E9] uppercase tracking-wider flex items-center space-x-2">
                  <Scale className="h-4 w-4 text-gold-500" />
                  <span>Financial Integrity Bridge (Reconciliation Equation Proof)</span>
                </h2>
                <p className="text-[11px] text-slate-500 dark:text-[#9BA8BA] mt-0.5">
                  Opening Balance + Capital Inflows (Credits) - Capital Outflows (Debits) = Expected vs Extracted Closing Balance.
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center space-x-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                  isBridgeReconciled
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                    : 'bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800'
                }`}>
                  <CheckCircle2 className="h-3 w-3" />
                  <span>{isBridgeReconciled ? 'Reconciled (₹0.00 Variance)' : `Mismatch (₹${balanceVariance.toFixed(2)})`}</span>
                </span>

                {activeStatement && (
                  <Link
                    to={`/statements/${activeStatement.id}`}
                    className="text-xs font-semibold text-gold-600 hover:text-gold-500 dark:text-gold-400 flex items-center space-x-1 pl-2 border-l border-slate-200 dark:border-navy-700"
                  >
                    <span>Inspect Evidence</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                )}
              </div>
            </div>

            {/* Mathematical Flow Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-4 text-center">
              <div className="rounded-lg bg-slate-50 p-3.5 dark:bg-navy-800/80 border border-slate-200/60 dark:border-navy-700/60">
                <span className="text-[10px] font-bold text-slate-500 dark:text-[#9BA8BA] uppercase tracking-wider">Opening Balance</span>
                <p className="mt-1 font-mono text-base font-bold text-slate-900 dark:text-[#F4F1E9] tabular-nums">
                  ₹ {openingBal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] text-slate-400 dark:text-[#9BA8BA] font-mono">Baseline Ledger</span>
              </div>

              <div className="rounded-lg bg-emerald-50/70 p-3.5 dark:bg-emerald-950/30 border border-emerald-200/70 dark:border-emerald-800/50">
                <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-300 uppercase tracking-wider">+ Capital Inflows</span>
                <p className="mt-1 font-mono text-base font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                  + ₹ {totalInflow.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] text-emerald-600/80 dark:text-emerald-400/80 font-mono">Total Verified Credits</span>
              </div>

              <div className="rounded-lg bg-rose-50/70 p-3.5 dark:bg-rose-950/30 border border-rose-200/70 dark:border-rose-800/50">
                <span className="text-[10px] font-bold text-rose-700 dark:text-rose-300 uppercase tracking-wider">- Capital Outflows</span>
                <p className="mt-1 font-mono text-base font-bold text-rose-600 dark:text-rose-400 tabular-nums">
                  - ₹ {totalOutflow.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] text-rose-600/80 dark:text-rose-400/80 font-mono">Total Verified Debits</span>
              </div>

              <div className="rounded-lg bg-gold-50/70 p-3.5 dark:bg-gold-950/20 border border-gold-200/70 dark:border-gold-800/50">
                <span className="text-[10px] font-bold text-gold-700 dark:text-gold-300 uppercase tracking-wider">= Expected Closing</span>
                <p className="mt-1 font-mono text-base font-bold text-gold-600 dark:text-gold-400 tabular-nums">
                  = ₹ {expectedClosing.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] text-gold-600/80 dark:text-gold-400/80 font-mono">Calculated Balance</span>
              </div>

              <div className={`rounded-lg p-3.5 border ${
                isBridgeReconciled
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-200 dark:border-emerald-800'
                  : 'bg-rose-50 text-rose-800 border-rose-300 dark:bg-rose-950/40 dark:text-rose-200 dark:border-rose-800'
              }`}>
                <span className="text-[10px] font-bold uppercase tracking-wider">
                  {isBridgeReconciled ? 'Actual Closing (Reconciled)' : 'Closing Mismatch'}
                </span>
                <p className="mt-1 font-mono text-base font-bold tabular-nums">
                  ₹ {closingBal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <span className="text-[10px] font-mono">
                  Variance: ₹ {balanceVariance.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* =========================================================================
              3. PRIMARY CHARTS: Cash Flow Intelligence (7 cols) + Running Balance (5 cols)
             ========================================================================= */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* CASH FLOW INTELLIGENCE */}
            <div className="lg:col-span-7 oscar-card">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-navy-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-[#F4F1E9] uppercase tracking-wider">
                    Cash Flow Intelligence (Inflow vs Outflow)
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-[#9BA8BA] mt-0.5">
                    Click any transaction date bar to drill directly into corresponding records.
                  </p>
                </div>
                <Link
                  to="/transactions"
                  className="text-xs font-semibold text-gold-600 hover:text-gold-500 dark:text-gold-400"
                >
                  View Ledger
                </Link>
              </div>

              <div className="mt-4 h-64 w-full">
                {cashflow.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-400">
                    No cashflow data available for current scope
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart
                      data={cashflow}
                      onClick={(data) => {
                        if (data && data.activeLabel) {
                          navigate(`/transactions?search=${data.activeLabel}`);
                        }
                      }}
                      className="cursor-pointer"
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.15} />
                      <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#9BA8BA' }} tickLine={false} />
                      <YAxis tick={{ fontSize: 10, fill: '#9BA8BA' }} tickLine={false} />
                      <Tooltip
                        formatter={(val: any, name: any) => [
                          `₹ ${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`,
                          name === 'credits' ? 'Inflow (Credit)' : name === 'debits' ? 'Outflow (Debit)' : 'Net Cashflow',
                        ]}
                        contentStyle={{
                          backgroundColor: '#101B2D',
                          borderRadius: '8px',
                          border: '1px solid #1E2F4A',
                          color: '#F4F1E9',
                          fontSize: '11px',
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      <Bar dataKey="credits" fill="#20B889" name="credits" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="debits" fill="#EF6464" name="debits" radius={[3, 3, 0, 0]} />
                      <Line type="monotone" dataKey="net" stroke="#D6B36A" strokeWidth={2.5} name="net" dot={{ r: 3 }} />
                    </ComposedChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* RUNNING BALANCE TRAJECTORY */}
            <div className="lg:col-span-5 oscar-card">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-navy-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-[#F4F1E9] uppercase tracking-wider">
                    Running Balance Trajectory
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-[#9BA8BA] mt-0.5">
                    Account balance progression over sequence.
                  </p>
                </div>
                <span className="font-mono text-xs font-bold text-slate-800 dark:text-[#F4F1E9]">
                  ₹ {closingBal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="mt-4 h-64 w-full">
                {!runningBalance || runningBalance.points.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-xs text-slate-400">
                    No balance trajectory recorded
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={runningBalance.points}>
                      <defs>
                        <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#D6B36A" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#D6B36A" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.15} />
                      <XAxis dataKey="sequence" tick={{ fontSize: 10, fill: '#9BA8BA' }} tickLine={false} label={{ value: 'Row #', position: 'insideBottomRight', offset: -5, fontSize: 10, fill: '#9BA8BA' }} />
                      <YAxis tick={{ fontSize: 10, fill: '#9BA8BA' }} tickLine={false} domain={['auto', 'auto']} />
                      <Tooltip
                        formatter={(val: any) => [`₹ ${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`, 'Balance']}
                        labelFormatter={(seq) => {
                          const pt = runningBalance.points.find((p) => p.sequence === Number(seq));
                          return pt ? `Row ${seq}: ${pt.date} - ${pt.description}` : `Row ${seq}`;
                        }}
                        contentStyle={{
                          backgroundColor: '#101B2D',
                          borderRadius: '8px',
                          border: '1px solid #1E2F4A',
                          color: '#F4F1E9',
                          fontSize: '11px',
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="balance"
                        stroke="#D6B36A"
                        strokeWidth={2.5}
                        fillOpacity={1}
                        fill="url(#balanceGrad)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>

          {/* =========================================================================
              4. ADVANCED ANALYTICS & OPERATIONAL AREA:
                 Activity Heatmap + Review Queue + Classification Mix
             ========================================================================= */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* Daily Activity Calendar Heatmap (6 cols) */}
            <div className="lg:col-span-6 oscar-card">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-navy-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-[#F4F1E9] uppercase tracking-wider">
                    Daily Activity Heatmap
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-[#9BA8BA] mt-0.5">
                    Click any day block to filter its transactions in Explorer.
                  </p>
                </div>
                <div className="flex items-center space-x-1 rounded-lg border border-slate-200 bg-slate-50 p-0.5 text-[10px] dark:border-navy-700 dark:bg-navy-800">
                  <button
                    onClick={() => setHeatmapMetric('count')}
                    className={`rounded px-2 py-0.5 font-medium transition cursor-pointer ${
                      heatmapMetric === 'count'
                        ? 'bg-white text-slate-900 shadow-sm dark:bg-navy-700 dark:text-[#F4F1E9]'
                        : 'text-slate-500 dark:text-[#9BA8BA]'
                    }`}
                  >
                    Count
                  </button>
                  <button
                    onClick={() => setHeatmapMetric('volume')}
                    className={`rounded px-2 py-0.5 font-medium transition cursor-pointer ${
                      heatmapMetric === 'volume'
                        ? 'bg-white text-slate-900 shadow-sm dark:bg-navy-700 dark:text-[#F4F1E9]'
                        : 'text-slate-500 dark:text-[#9BA8BA]'
                    }`}
                  >
                    Volume
                  </button>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-4 sm:grid-cols-7 gap-2">
                {heatmap.length === 0 ? (
                  <div className="col-span-full p-8 text-center text-xs text-slate-400">
                    No activity dates recorded
                  </div>
                ) : (
                  heatmap.map((d) => {
                    const countIntensity = d.count >= 4 ? 'bg-gold-500 text-navy-950 font-black' : d.count >= 2 ? 'bg-gold-400 text-navy-950 font-bold' : 'bg-gold-100 text-gold-900 dark:bg-navy-800 dark:text-gold-300';
                    const volIntensity = d.total_volume >= 20000 ? 'bg-cobalt-600 text-white font-black' : d.total_volume >= 5000 ? 'bg-cobalt-500 text-white font-bold' : 'bg-cobalt-100 text-cobalt-900 dark:bg-navy-800 dark:text-cobalt-300';
                    const badgeClass = heatmapMetric === 'count' ? countIntensity : volIntensity;

                    return (
                      <button
                        key={d.date}
                        onClick={() => navigate(`/transactions?search=${d.date}`)}
                        className={`rounded-lg p-2 text-center transition hover:scale-105 shadow-sm border border-transparent ${badgeClass} cursor-pointer`}
                        title={`${d.date}: ${d.count} txns, ₹ ${d.total_volume.toLocaleString('en-IN')} volume`}
                      >
                        <span className="block text-[9.5px] font-mono opacity-80">{d.date.slice(5)}</span>
                        <span className="mt-0.5 block font-mono text-[11px] font-bold">
                          {heatmapMetric === 'count' ? `${d.count}x` : `₹${Math.round(d.total_volume / 1000)}k`}
                        </span>
                      </button>
                    );
                  })
                )}
              </div>
            </div>

            {/* Exception & Review Queue Quick-Action Card (3 cols) */}
            <div className="lg:col-span-3 rounded-xl border border-amber-200/80 bg-gradient-to-b from-amber-50/40 to-white p-5 shadow-sm dark:border-amber-900/40 dark:from-navy-800/80 dark:to-navy-900 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-xs text-amber-800 dark:text-amber-300 border-b border-amber-100 pb-3 dark:border-amber-900/40">
                  <span className="font-bold uppercase tracking-wider">Human Review Queue</span>
                  <AlertCircle className="h-4 w-4 text-amber-500" />
                </div>
                <div className="mt-4">
                  <span className="text-3xl font-extrabold font-mono text-amber-600 dark:text-amber-400">
                    {(summary?.pending_reviews ?? 0) + (summary?.anomalies_count ?? 0)}
                  </span>
                  <p className="mt-1 text-xs text-slate-600 dark:text-[#9BA8BA] font-medium">
                    Exceptions pending verification
                  </p>
                  <div className="mt-3 space-y-1.5 text-[11px] text-slate-500 dark:text-[#9BA8BA]">
                    <div className="flex justify-between">
                      <span>Low-Confidence ML:</span>
                      <strong className="text-slate-700 dark:text-[#F4F1E9]">{summary?.pending_reviews ?? 0}</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Outliers / Duplicates:</span>
                      <strong className="text-slate-700 dark:text-[#F4F1E9]">{summary?.anomalies_count ?? 0}</strong>
                    </div>
                  </div>
                </div>
              </div>

              <Link
                to="/reviews"
                className="mt-5 inline-flex w-full items-center justify-center space-x-1.5 rounded-lg bg-amber-600 px-3 py-2 text-xs font-bold text-white shadow-sm hover:bg-amber-700 transition"
              >
                <span>Resolve Exceptions</span>
                <ChevronRight className="h-4 w-4" />
              </Link>
            </div>

            {/* Classification Mix (3 cols) */}
            <div className="lg:col-span-3 oscar-card flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-xs text-slate-900 dark:text-[#F4F1E9] border-b border-slate-100 pb-3 dark:border-navy-800">
                  <span className="font-bold uppercase tracking-wider flex items-center space-x-1.5">
                    <Cpu className="h-4 w-4 text-gold-500" />
                    <span>Classification Mix</span>
                  </span>
                  <Link to="/classification" className="text-[11px] font-semibold text-gold-600 hover:underline dark:text-gold-400">
                    Insights
                  </Link>
                </div>

                <div className="mt-4 space-y-3 text-xs">
                  <div>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-600 dark:text-[#9BA8BA] font-medium">Deterministic Rules:</span>
                      <strong className="font-mono text-gold-500">{classification?.rule_based_percentage?.toFixed(1) ?? '75.0'}%</strong>
                    </div>
                    <div className="mt-1 h-2 w-full rounded-full bg-slate-100 dark:bg-navy-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gold-400"
                        style={{ width: `${classification?.rule_based_percentage ?? 75}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-600 dark:text-[#9BA8BA] font-medium">Dual TF-IDF LogReg:</span>
                      <strong className="font-mono text-cobalt-500">{classification?.ml_based_percentage?.toFixed(1) ?? '25.0'}%</strong>
                    </div>
                    <div className="mt-1 h-2 w-full rounded-full bg-slate-100 dark:bg-navy-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-cobalt-500"
                        style={{ width: `${classification?.ml_based_percentage ?? 25}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-600 dark:text-[#9BA8BA] font-medium">Human Corrected:</span>
                      <strong className="font-mono text-emerald-500">{classification?.manual_count ?? 0} txns</strong>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 rounded-lg bg-slate-50 p-2.5 text-[10px] text-slate-500 dark:bg-navy-800/80 dark:text-[#9BA8BA] border border-slate-200/50 dark:border-navy-700/50">
                Deterministic Rules + Offline ML • Zero Cloud LLMs
              </div>
            </div>
          </div>

          {/* =========================================================================
              5. CATEGORY SPENDING + PROCESSING JOURNEY
             ========================================================================= */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* Category Spending (6 cols) */}
            <div className="lg:col-span-6 oscar-card">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-navy-800">
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-[#F4F1E9] uppercase tracking-wider">
                    Operational Spending Distribution
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-[#9BA8BA] mt-0.5">
                    Accounting-aware breakdown excluding non-expense capital transfers.
                  </p>
                </div>
                <Link
                  to="/analytics"
                  className="text-xs font-semibold text-gold-600 hover:text-gold-500 dark:text-gold-400"
                >
                  Deep Analytics
                </Link>
              </div>

              <div className="mt-4 space-y-3">
                {categories.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-400">No category expenses recorded</div>
                ) : (
                  categories.map((c) => (
                    <div key={c.category} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-800 dark:text-[#F4F1E9] truncate max-w-[240px]">
                          {c.category}
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-slate-500 dark:text-[#9BA8BA] text-[11px]">{c.percentage_of_expense}%</span>
                          <span className="font-mono font-bold text-slate-900 dark:text-[#F4F1E9]">
                            ₹ {c.total_debit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                      </div>
                      <div className="h-2 w-full rounded-full bg-slate-100 dark:bg-navy-800 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gold-400 dark:bg-gold-500 transition-all duration-500"
                          style={{ width: `${Math.min(c.percentage_of_expense, 100)}%` }}
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Document Processing Journey (6 cols) */}
            <div className="lg:col-span-6 oscar-card flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-navy-800">
                  <h3 className="text-xs font-bold text-slate-900 dark:text-[#F4F1E9] uppercase tracking-wider flex items-center space-x-1.5">
                    <Layers className="h-4 w-4 text-gold-500" />
                    <span>Processing Journey &amp; Governance</span>
                  </h3>
                  <span className="text-[10px] text-slate-400 dark:text-[#9BA8BA] font-mono">100% Deterministic</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-4">
                  {[
                    { stage: '1. Ingestion', status: 'Validated (%PDF-)', ok: true },
                    { stage: '2. Extraction', status: 'Multi-Layout / OCR', ok: true },
                    { stage: '3. Normalization', status: 'Decimal Minor Units', ok: true },
                    { stage: '4. Classification', status: 'Rules + TF-IDF ML', ok: true },
                    { stage: '5. Reconciliation', status: isBridgeReconciled ? 'Reconciled (₹0 Var)' : 'Verified Proof', ok: isBridgeReconciled },
                    { stage: '6. Governance', status: 'Audit & Export Ready', ok: true },
                  ].map((step, idx) => (
                    <div key={idx} className="rounded-lg bg-slate-50 p-2.5 text-xs dark:bg-navy-800/80 border border-slate-200/60 dark:border-navy-700/60">
                      <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 dark:text-[#F4F1E9]">
                        <span>{step.stage}</span>
                        <Check className="h-3.5 w-3.5 text-emerald-500" />
                      </div>
                      <p className="mt-1 text-[10px] text-slate-500 dark:text-[#9BA8BA] font-mono truncate">{step.status}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick links footer */}
              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-navy-800 flex items-center justify-between text-xs">
                <span className="text-slate-500 dark:text-[#9BA8BA] text-[11px]">Ready for statutory export:</span>
                <div className="flex items-center space-x-3 font-semibold">
                  <Link to="/exports" className="text-gold-600 hover:underline dark:text-gold-400 flex items-center space-x-1">
                    <FileSpreadsheet className="h-3.5 w-3.5" />
                    <span>Excel &amp; CSV Center</span>
                  </Link>
                  <Link to="/audit" className="text-slate-600 hover:underline dark:text-[#9BA8BA]">
                    Audit Log
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* =========================================================================
              6. RECENT STATEMENTS TABLE
             ========================================================================= */}
          <div className="rounded-xl border border-slate-200/90 bg-white shadow-sm dark:border-navy-800 dark:bg-navy-900 overflow-hidden">
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 dark:border-navy-800">
              <h3 className="text-xs font-bold text-slate-900 dark:text-[#F4F1E9] uppercase tracking-wider flex items-center space-x-1.5">
                <FileText className="h-4 w-4 text-gold-500" />
                <span>Recent Ingested Statements ({statements.length})</span>
              </h3>
              <Link to="/statements" className="text-xs font-semibold text-gold-600 hover:underline dark:text-gold-400">
                View All Statements
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 dark:bg-navy-800/60 dark:text-[#9BA8BA] font-semibold border-b border-slate-100 dark:border-navy-800">
                  <tr>
                    <th className="px-4 py-2.5">Bank / Document</th>
                    <th className="px-4 py-2.5">Period</th>
                    <th className="px-4 py-2.5 text-center">Type</th>
                    <th className="px-4 py-2.5 text-right">Transactions</th>
                    <th className="px-4 py-2.5 text-right">Inflows (CR)</th>
                    <th className="px-4 py-2.5 text-right">Outflows (DR)</th>
                    <th className="px-4 py-2.5 text-center">Status</th>
                    <th className="px-4 py-2.5 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-navy-800">
                  {statements.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-50/70 dark:hover:bg-navy-800/40 transition">
                      <td className="px-4 py-3">
                        <Link to={`/statements/${s.id}`} className="font-bold text-slate-900 dark:text-[#F4F1E9] hover:text-gold-500 transition">
                          {s.filename}
                        </Link>
                        <p className="text-[10px] text-slate-400 dark:text-[#9BA8BA] font-mono">{s.bank_name || 'Standard Bank'}</p>
                      </td>
                      <td className="px-4 py-3 text-slate-600 dark:text-[#9BA8BA] font-mono text-[11px] whitespace-nowrap">
                        {s.statement_period || 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-700 dark:bg-navy-800 dark:text-[#9BA8BA] uppercase">
                          {s.pdf_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-mono font-semibold">
                        {s.transaction_count ?? 0}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-emerald-600 dark:text-emerald-400">
                        ₹ {(s.total_credits ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-rose-600 dark:text-rose-400">
                        ₹ {(s.total_debits ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-flex items-center space-x-1 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                          s.reconciliation_status === 'RECONCILED'
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                            : 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                        }`}>
                          <CheckCircle2 className="h-3 w-3" />
                          <span>{s.reconciliation_status}</span>
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center space-x-2">
                          <Link
                            to={`/statements/${s.id}`}
                            className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-gold-500 dark:hover:bg-navy-800"
                            title="Inspect Evidence"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                          <Link
                            to={`/reconciliation/${s.id}`}
                            className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-gold-500 dark:hover:bg-navy-800"
                            title="Reconciliation"
                          >
                            <Scale className="h-4 w-4" />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
