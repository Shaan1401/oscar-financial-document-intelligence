import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Scale,
  CreditCard,
  Building2,
  Cpu,
  CheckCircle2,
  PieChart as PieIcon,
  BarChart3,
  Calendar,
  Layers,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  LineChart,
  Line,
  ComposedChart,
} from 'recharts';
import { api } from '../services/api';
import {
  SummaryMetrics,
  CategoryBreakdown,
  CashflowPoint,
  MerchantConcentrationResponse,
  PaymentChannelItem,
  ClassificationDeepResponse,
  ExtractionCompletenessResponse,
  MultiStatementResponse,
  CategoryTrendPoint,
} from '../types';

export const FinancialAnalytics: React.FC = () => {
  const [summary, setSummary] = useState<SummaryMetrics | null>(null);
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [merchants, setMerchants] = useState<MerchantConcentrationResponse | null>(null);
  const [channels, setChannels] = useState<PaymentChannelItem[]>([]);
  const [clsDeep, setClsDeep] = useState<ClassificationDeepResponse | null>(null);
  const [completeness, setCompleteness] = useState<ExtractionCompletenessResponse | null>(null);
  const [multiStmt, setMultiStmt] = useState<MultiStatementResponse | null>(null);
  const [trends, setTrends] = useState<CategoryTrendPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getAnalyticsSummary(),
      api.getCategoryAnalytics(),
      api.getMerchantConcentration(undefined, 8),
      api.getPaymentChannels(),
      api.getClassificationDeep(),
      api.getExtractionCompleteness(),
      api.getMultiStatementComparison(),
      api.getCategoryTrends(),
    ])
      .then(([sumData, catData, merchData, chanData, clsData, compData, multiData, trendData]) => {
        setSummary(sumData);
        setCategories(catData);
        setMerchants(merchData);
        setChannels(chanData);
        setClsDeep(clsData);
        setCompleteness(compData);
        setMultiStmt(multiData);
        setTrends(trendData);
      })
      .catch((err) => console.error('Financial Analytics load failed:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Title & Scope */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          Deep Financial Analytics & Intelligence
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Advanced capital flow analysis, merchant Pareto concentration, payment channel velocity, and classification audits.
        </p>
      </div>

      {/* Top 3 KPI Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Gross Portfolio Inflow</span>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </div>
          <p className="mt-2 text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            ₹ {(summary?.total_credits ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
          <span className="text-[10px] text-slate-400 mt-1 block">Deposits, payroll & inward remittances</span>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Gross Portfolio Outflow</span>
            <TrendingDown className="h-4 w-4 text-rose-500" />
          </div>
          <p className="mt-2 text-2xl font-bold font-mono text-rose-600 dark:text-rose-400">
            ₹ {(summary?.total_debits ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
          <span className="text-[10px] text-slate-400 mt-1 block">Operational expenses, EMIs & merchant debits</span>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Net Treasury Movement</span>
            <Scale className="h-4 w-4 text-brand-500" />
          </div>
          <p className={`mt-2 text-2xl font-bold font-mono ${
            (summary?.net_movement ?? 0) >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
          }`}>
            ₹ {(summary?.net_movement ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
          <span className="text-[10px] text-slate-400 mt-1 block">Net liquidity change across active statements</span>
        </div>
      </div>

      {/* Row 1: Merchant Concentration / Pareto & Payment Channels */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* MERCHANT CONCENTRATION / PARETO ANALYSIS */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center space-x-1.5">
                <Building2 className="h-4 w-4 text-brand-600" />
                <span>Merchant Concentration & Pareto Curve</span>
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Top merchant entities by spend and cumulative share (% Pareto).
              </p>
            </div>
            <span className="text-xs font-mono font-semibold text-slate-700 dark:text-slate-300">
              ₹ {merchants?.total_tracked_spending.toLocaleString('en-IN') ?? 0}
            </span>
          </div>

          <div className="mt-4 h-64 w-full">
            {!merchants || merchants.top_merchants.length === 0 ? (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">No merchant records identified</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={merchants.top_merchants} margin={{ top: 10, right: 35, left: 15, bottom: 35 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
                  <XAxis dataKey="merchant" tick={{ fontSize: 10, fill: '#94A3B8' }} interval={0} angle={-15} textAnchor="end" height={45} />
                  <YAxis yAxisId="left" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                  <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: '#94A3B8' }} domain={[0, 100]} unit="%" />
                  <Tooltip
                    formatter={(val: any, name: any) => [
                      name === 'cumulative_percentage' ? `${val}%` : `₹ ${Number(val).toLocaleString('en-IN')}`,
                      name === 'cumulative_percentage' ? 'Cumulative Share' : 'Merchant Spend',
                    ]}
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b', color: '#fff', fontSize: '11px' }}
                  />
                  <Bar yAxisId="left" dataKey="amount" fill="#3B82F6" name="amount" radius={[4, 4, 0, 0]} />
                  <Line yAxisId="right" type="monotone" dataKey="cumulative_percentage" stroke="#F59E0B" strokeWidth={2.5} name="cumulative_percentage" dot={{ r: 3 }} />
                </ComposedChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* PAYMENT CHANNEL BREAKDOWN */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center space-x-1.5">
                <CreditCard className="h-4 w-4 text-brand-600" />
                <span>Payment Channel Velocity</span>
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Recognized rail volume (UPI, NEFT, IMPS, ATM, POS, NACH).
              </p>
            </div>
            <span className="text-xs font-semibold text-slate-500">{channels.length} Rails Detected</span>
          </div>

          <div className="mt-4 h-64 w-full">
            {channels.length === 0 ? (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">No payment channels classified</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={channels} layout="vertical" margin={{ top: 10, right: 30, left: 15, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} opacity={0.3} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                  <YAxis type="category" dataKey="channel" tick={{ fontSize: 10, fill: '#94A3B8' }} width={110} />
                  <Tooltip
                    formatter={(val: any) => [`₹ ${Number(val).toLocaleString('en-IN')}`, 'Channel Volume']}
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b', color: '#fff', fontSize: '11px' }}
                  />
                  <Bar dataKey="total_amount" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Row 2: Category Timeline Trends & Classification Intelligence */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* CATEGORY TREND ANALYSIS */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                Category Spending Trends Over Time
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Daily expenditure velocity across leading expense categories.
              </p>
            </div>
            <Calendar className="h-4 w-4 text-slate-400" />
          </div>

          <div className="mt-4 h-64 w-full">
            {trends.length === 0 ? (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">No trend history available</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends} margin={{ top: 10, right: 30, left: 15, bottom: 15 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} />
                  <Tooltip
                    formatter={(val: any, name: any) => [`₹ ${Number(val).toLocaleString('en-IN')}`, String(name)]}
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b', color: '#fff', fontSize: '11px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11, paddingTop: 6 }} />
                  <Line type="monotone" dataKey="Food & Dining" stroke="#3B82F6" strokeWidth={2} dot={{ r: 2 }} />
                  <Line type="monotone" dataKey="Groceries" stroke="#10B981" strokeWidth={2} dot={{ r: 2 }} />
                  <Line type="monotone" dataKey="Shopping" stroke="#F59E0B" strokeWidth={2} dot={{ r: 2 }} />
                  <Line type="monotone" dataKey="Utilities" stroke="#EC4899" strokeWidth={2} dot={{ r: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* CLASSIFICATION INTELLIGENCE & CONFIDENCE BINS */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center space-x-1.5">
                <Cpu className="h-4 w-4 text-brand-600" />
                <span>Explainable Hybrid Classification Distribution</span>
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Rule engine vs traditional TF-IDF Logistic Regression confidence distribution.
              </p>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="rounded-lg bg-blue-50/70 p-2.5 dark:bg-blue-950/30 border border-blue-200/60 dark:border-blue-900/40">
                <span className="text-[10px] text-blue-700 dark:text-blue-300 font-semibold uppercase">Rule Based</span>
                <p className="font-mono text-base font-bold text-blue-900 dark:text-blue-200">
                  {clsDeep?.rule_based_percentage ?? 0}%
                </p>
                <span className="text-[10px] text-blue-600/70">{clsDeep?.rule_based_count ?? 0} txns</span>
              </div>

              <div className="rounded-lg bg-purple-50/70 p-2.5 dark:bg-purple-950/30 border border-purple-200/60 dark:border-purple-900/40">
                <span className="text-[10px] text-purple-700 dark:text-purple-300 font-semibold uppercase">Logistic Reg</span>
                <p className="font-mono text-base font-bold text-purple-900 dark:text-purple-200">
                  {clsDeep?.ml_based_percentage ?? 0}%
                </p>
                <span className="text-[10px] text-purple-600/70">{clsDeep?.ml_based_count ?? 0} txns</span>
              </div>

              <div className="rounded-lg bg-amber-50/70 p-2.5 dark:bg-amber-950/30 border border-amber-200/60 dark:border-amber-900/40">
                <span className="text-[10px] text-amber-700 dark:text-amber-300 font-semibold uppercase">Needs Review</span>
                <p className="font-mono text-base font-bold text-amber-900 dark:text-amber-200">
                  {clsDeep?.needs_review_count ?? 0}
                </p>
                <span className="text-[10px] text-amber-600/70">Flagged Exceptions</span>
              </div>
            </div>

            <div className="pt-2">
              <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-2">
                Calibrated Model Confidence Score Bins:
              </span>
              <div className="space-y-1.5">
                {clsDeep?.score_distribution.map((bin) => (
                  <div key={bin.range} className="flex items-center justify-between text-xs">
                    <span className="font-mono text-[11px] text-slate-600 dark:text-slate-400 w-44 truncate">
                      {bin.range}
                    </span>
                    <div className="flex-1 mx-3 h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-indigo-600 dark:bg-indigo-500"
                        style={{ width: `${bin.percentage}%` }}
                      />
                    </div>
                    <span className="font-mono text-[11px] text-slate-700 dark:text-slate-300 w-12 text-right">
                      {bin.count} ({bin.percentage}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Extraction Completeness & Multi-Statement Comparison */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* EXTRACTION COMPLETENESS METRICS */}
        <div className="lg:col-span-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                Field Completeness Audit
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Availability of extracted fields across all rows.
              </p>
            </div>
            <span className="font-mono text-xs font-bold text-emerald-600">
              {completeness?.overall_completeness_pct ?? 100}%
            </span>
          </div>

          <div className="mt-4 space-y-3 text-xs">
            {[
              { label: 'Date Completeness', val: completeness?.date_completeness_pct ?? 100 },
              { label: 'Description Completeness', val: completeness?.description_completeness_pct ?? 100 },
              { label: 'Amount Presence (DR/CR)', val: completeness?.amount_completeness_pct ?? 100 },
              { label: 'Balance Step Present', val: completeness?.balance_completeness_pct ?? 100 },
              { label: 'Page / Coordinate Traceability', val: completeness?.coordinates_completeness_pct ?? 100 },
            ].map((f) => (
              <div key={f.label} className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-600 dark:text-slate-400">{f.label}</span>
                  <span className="font-mono font-semibold text-slate-900 dark:text-white">{f.val}%</span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{ width: `${f.val}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* MULTI-STATEMENT COMPARISON (Strictly Partitioned by Currency) */}
        <div className="lg:col-span-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                Multi-Statement Comparative Ledger
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Financial comparison grouped strictly by currency (Zero currency mixing).
              </p>
            </div>
            <span className="text-xs font-mono rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
              Currency: INR (₹)
            </span>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[700px]">
              <thead className="bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                <tr>
                  <th className="px-3 py-2 font-semibold">Statement File</th>
                  <th className="px-3 py-2 font-semibold">Bank Entity</th>
                  <th className="px-3 py-2 font-semibold text-right">Inflow (Cr)</th>
                  <th className="px-3 py-2 font-semibold text-right">Outflow (Dr)</th>
                  <th className="px-3 py-2 font-semibold text-right">Net Liquidity</th>
                  <th className="px-3 py-2 font-semibold text-right">Closing Balance</th>
                  <th className="px-3 py-2 font-semibold text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px]">
                {multiStmt?.by_currency['INR']?.map((s) => (
                  <tr key={s.statement_id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                    <td className="px-3 py-2.5 font-sans font-medium text-slate-800 dark:text-slate-200 truncate max-w-[150px]" title={s.filename}>
                      {s.filename}
                    </td>
                    <td className="px-3 py-2.5 font-sans text-slate-500">{s.bank_name}</td>
                    <td className="px-3 py-2.5 text-right text-emerald-600 font-semibold">
                      ₹ {s.total_credits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-3 py-2.5 text-right text-rose-600 font-semibold">
                      ₹ {s.total_debits.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className={`px-3 py-2.5 text-right font-semibold ${
                      s.net_movement >= 0 ? 'text-emerald-600' : 'text-rose-600'
                    }`}>
                      ₹ {s.net_movement.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-3 py-2.5 text-right font-semibold text-slate-900 dark:text-white">
                      ₹ {s.closing_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-3 py-2.5 text-center">
                      <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                        s.reconciliation_status === 'RECONCILED'
                          ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                          : 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                      }`}>
                        {s.reconciliation_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialAnalytics;
