import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, ChevronLeft, ChevronRight, Download, ExternalLink, X } from 'lucide-react';
import { api } from '../services/api';
import { Transaction } from '../types';

export const TransactionExplorer: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [method, setMethod] = useState('');
  const [reviewStatus, setReviewStatus] = useState('');
  const [page, setPage] = useState(1);
  const limit = 25;

  const loadTransactions = () => {
    setLoading(true);
    api.getTransactions({
      search: search || undefined,
      category: category || undefined,
      method: method || undefined,
      review_status: reviewStatus || undefined,
      limit,
      offset: (page - 1) * limit,
    })
      .then((res) => {
        setTransactions(res.items);
        setTotal(res.total);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTransactions();
  }, [search, category, method, reviewStatus, page]);

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          Transaction Explorer
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Browse, filter, and inspect normalized transactions across all processed bank statements.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 rounded-xl border border-slate-200/90 bg-white p-3.5 shadow-sm dark:border-navy-800 dark:bg-navy-900">
        <div className="relative flex items-center rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 dark:border-navy-700 dark:bg-navy-950/80">
          <Search className="h-4 w-4 text-slate-400 mr-2 shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search description, merchant..."
            className="w-full bg-transparent text-xs text-slate-900 placeholder-slate-400 focus:outline-none dark:text-[#F4F1E9]"
          />
          {search && (
            <button
              onClick={() => {
                setSearch('');
                setPage(1);
              }}
              title="Clear search"
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 ml-1"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        <select
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-700 focus:outline-none dark:border-navy-700 dark:bg-navy-950/80 dark:text-slate-300 cursor-pointer"
        >
          <option value="">All Categories</option>
          <option value="Salary & Income">Salary & Income</option>
          <option value="Food & Dining">Food & Dining</option>
          <option value="Groceries">Groceries</option>
          <option value="Shopping">Shopping</option>
          <option value="Transportation & Fuel">Transportation & Fuel</option>
          <option value="Utilities">Utilities</option>
          <option value="Healthcare">Healthcare</option>
          <option value="Rent & Housing">Rent & Housing</option>
          <option value="Education">Education</option>
          <option value="Entertainment">Entertainment</option>
          <option value="Travel">Travel</option>
          <option value="Insurance">Insurance</option>
          <option value="Investments">Investments</option>
          <option value="Banking Charges">Banking Charges</option>
          <option value="ATM / Cash Withdrawal">ATM / Cash Withdrawal</option>
          <option value="Transfers">Transfers</option>
          <option value="Refunds & Reversals">Refunds & Reversals</option>
          <option value="EMI & Loans">EMI & Loans</option>
          <option value="Tax & Government">Tax & Government</option>
          <option value="Other / Unclassified">Other / Unclassified</option>
        </select>

        <select
          value={method}
          onChange={(e) => {
            setMethod(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-700 focus:outline-none dark:border-navy-700 dark:bg-navy-950/80 dark:text-slate-300 cursor-pointer"
        >
          <option value="">All Classification Methods</option>
          <option value="RULE_BASED">Rule Engine (Heuristics)</option>
          <option value="MACHINE_LEARNING">Traditional ML (TF-IDF)</option>
          <option value="MANUAL">Manual Human Correction</option>
          <option value="NEEDS_REVIEW">Needs Review</option>
        </select>

        <select
          value={reviewStatus}
          onChange={(e) => {
            setReviewStatus(e.target.value);
            setPage(1);
          }}
          className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-700 focus:outline-none dark:border-navy-700 dark:bg-navy-950/80 dark:text-slate-300 cursor-pointer"
        >
          <option value="">All Review Statuses</option>
          <option value="APPROVED">Approved</option>
          <option value="NEEDS_REVIEW">Needs Review</option>
          <option value="CORRECTED">Corrected</option>
        </select>
      </div>

      {/* Transactions Table */}
      <div className="rounded-xl border border-slate-200/90 bg-white shadow-sm dark:border-navy-800 dark:bg-navy-900 overflow-hidden">
        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gold-500 border-t-transparent" />
          </div>
        ) : transactions.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 dark:text-[#9BA8BA]">
            No transactions match the selected criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[850px]">
              <thead className="bg-slate-50/80 text-slate-700 dark:bg-navy-800/80 dark:text-[#9BA8BA]">
                <tr>
                  <th className="px-4 py-3 font-semibold">Date</th>
                  <th className="px-4 py-3 font-semibold">Description</th>
                  <th className="px-4 py-3 font-semibold">Category</th>
                  <th className="px-4 py-3 font-semibold text-right">Debit</th>
                  <th className="px-4 py-3 font-semibold text-right">Credit</th>
                  <th className="px-4 py-3 font-semibold text-right">Balance</th>
                  <th className="px-4 py-3 font-semibold">Method</th>
                  <th className="px-4 py-3 font-semibold">Status</th>
                  <th className="px-4 py-3 font-semibold text-right">Statement</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-navy-800">
                {transactions.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50/60 dark:hover:bg-navy-800/40">
                    <td className="px-4 py-3 whitespace-nowrap font-mono">{t.date}</td>
                    <td className="px-4 py-3 max-w-[280px]" title={t.raw_description}>
                      <p className="truncate font-medium text-slate-900 dark:text-white">{t.description}</p>
                      {t.validation_warnings && (
                        <p className="text-[10px] text-amber-600 dark:text-amber-400 truncate">
                          ⚠️ {t.validation_warnings}
                        </p>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                        {t.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-rose-600 whitespace-nowrap">
                      {t.debit > 0 ? `₹ ${t.debit.toFixed(2)}` : '-'}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-emerald-600 whitespace-nowrap">
                      {t.credit > 0 ? `₹ ${t.credit.toFixed(2)}` : '-'}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-slate-600 dark:text-slate-300 whitespace-nowrap">
                      {t.balance !== null && t.balance !== undefined ? `₹ ${t.balance.toFixed(2)}` : '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[9px] font-semibold ${
                          t.classification_method === 'RULE_BASED'
                            ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                            : t.classification_method === 'MACHINE_LEARNING'
                            ? 'bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300'
                            : 'bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                        }`}
                      >
                        {t.classification_method}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[9px] font-semibold ${
                          t.review_status === 'APPROVED'
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                            : t.review_status === 'CORRECTED'
                            ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                            : 'bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                        }`}
                      >
                        {t.review_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/statements/${t.statement_id}`}
                        title="View Statement Evidence"
                        className="rounded p-1 text-slate-400 hover:text-brand-600"
                      >
                        <ExternalLink className="h-3.5 w-3.5 inline" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 dark:border-slate-800 text-xs">
          <span className="text-slate-500 dark:text-slate-400">
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, total)} of {total} transactions
          </span>
          <div className="flex items-center space-x-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="rounded p-1 text-slate-500 hover:bg-slate-100 disabled:opacity-40 dark:hover:bg-slate-800"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="font-mono text-slate-700 dark:text-slate-300">
              Page {page} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="rounded p-1 text-slate-500 hover:bg-slate-100 disabled:opacity-40 dark:hover:bg-slate-800"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

