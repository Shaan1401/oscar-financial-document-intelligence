import React, { useEffect, useState, useMemo } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  Edit3,
  Search,
  ShieldAlert,
  ArrowRight,
  ExternalLink,
  X,
} from 'lucide-react';
import { api } from '../services/api';
import { Transaction } from '../types';

export const ReviewExceptions: React.FC = () => {
  const [items, setItems] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTxn, setSelectedTxn] = useState<Transaction | null>(null);

  // Approval and feedback states
  const [approvingId, setApprovingId] = useState<number | null>(null);
  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Modal correction form state
  const [newCategory, setNewCategory] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newDebit, setNewDebit] = useState<string>('');
  const [newCredit, setNewCredit] = useState<string>('');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [search, setSearch] = useState('');

  const loadQueue = () => {
    setLoading(true);
    api.getReviewQueue()
      .then((res) => setItems(res.items))
      .catch((err) => {
        console.error('Failed to load review queue:', err);
        setActionMessage({
          type: 'error',
          text: `Failed to load review queue: ${err.message || 'Network error'}`,
        });
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const filteredItems = useMemo(() => {
    if (!search.trim()) return items;
    const q = search.toLowerCase().trim();
    return items.filter((t) => {
      const descMatch = t.description?.toLowerCase().includes(q);
      const catMatch = t.category?.toLowerCase().includes(q);
      const flagMatch = (t.validation_warnings || t.classification_reason)?.toLowerCase().includes(q);
      const methodMatch = t.classification_method?.toLowerCase().includes(q);
      return descMatch || catMatch || flagMatch || methodMatch;
    });
  }, [items, search]);

  const handleApprove = async (id: number) => {
    if (approvingId !== null) return; // Prevent duplicate requests
    setApprovingId(id);
    setActionMessage(null);

    // Save snapshot of current items before optimistic mutation
    const previousItems = items;

    // Optimistically remove from current list for instant UI feedback
    setItems((prev) => prev.filter((t) => t.id !== id));

    try {
      const res = await api.approveTransaction(id, 'Approved via Review Centre');
      setActionMessage({
        type: 'success',
        text: res.message || `Transaction #${id} successfully approved and recorded in Audit Trail.`,
      });
      loadQueue();
    } catch (err: any) {
      // Rollback optimistic removal if backend/network request failed
      setItems(previousItems);
      setActionMessage({
        type: 'error',
        text: `Approval failed: ${err.message || 'Unknown network error'}`,
      });
    } finally {
      setApprovingId(null);
    }
  };

  const openCorrectModal = (t: Transaction) => {
    setSelectedTxn(t);
    setNewCategory(t.category);
    setNewDesc(t.description);
    setNewDebit(t.debit > 0 ? String(t.debit) : '');
    setNewCredit(t.credit > 0 ? String(t.credit) : '');
    setReason('');
  };

  const handleCorrectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTxn) return;
    const targetId = selectedTxn.id;
    setSubmitting(true);
    setActionMessage(null);
    try {
      const res = await api.correctTransaction(targetId, {
        new_category: newCategory,
        new_description: newDesc,
        new_debit: newDebit ? parseFloat(newDebit) : undefined,
        new_credit: newCredit ? parseFloat(newCredit) : undefined,
        reason: reason || 'Human correction via Review Centre',
      });
      setSelectedTxn(null);
      setItems((prev) => prev.filter((t) => t.id !== targetId));
      setActionMessage({
        type: 'success',
        text: res.message || `Transaction #${targetId} successfully corrected and recorded in Audit Trail.`,
      });
      loadQueue();
    } catch (err: any) {
      setActionMessage({
        type: 'error',
        text: `Correction failed: ${err.message || 'Unknown network error'}`,
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-[#F4F1E9]">
          Review &amp; Exceptions Centre
        </h1>
        <p className="text-sm text-slate-500 dark:text-[#9BA8BA] mt-1">
          Audit flagged transactions, resolve confidence warnings, and apply explainable human corrections.
        </p>
      </div>

      {/* Action Notification Banner */}
      {actionMessage && (
        <div
          role="alert"
          className={`flex items-center justify-between rounded-xl px-4 py-3 text-xs font-medium border shadow-sm transition-all ${
            actionMessage.type === 'success'
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/80'
              : 'bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800/80'
          }`}
        >
          <div className="flex items-center space-x-2">
            {actionMessage.type === 'success' ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="h-4 w-4 text-rose-600 dark:text-rose-400 shrink-0" />
            )}
            <span>{actionMessage.text}</span>
          </div>
          <button
            type="button"
            onClick={() => setActionMessage(null)}
            className="ml-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            title="Dismiss message"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Queue Table */}
      <div className="rounded-xl border border-slate-200/90 bg-white shadow-sm dark:border-navy-800 dark:bg-navy-900 overflow-hidden">
        {/* Search & Header Control Strip */}
        <div className="border-b border-slate-100 px-5 py-3 dark:border-navy-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-amber-500 shrink-0" />
            <span className="text-sm font-semibold text-slate-900 dark:text-[#F4F1E9]">
              Pending Exceptions ({filteredItems.length}{search ? ` of ${items.length}` : ''})
            </span>
          </div>

          <div className="relative w-full sm:w-80">
            <Search className="pointer-events-none absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400 dark:text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search description, category, reason..."
              className="w-full rounded-lg border border-slate-200 bg-slate-50 py-1.5 pl-8 pr-7 text-xs text-slate-900 placeholder:text-slate-400 focus:border-gold-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-gold-500 dark:border-navy-700 dark:bg-navy-950/80 dark:text-[#F4F1E9] dark:placeholder:text-slate-500 dark:focus:bg-navy-900"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch('')}
                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>

        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gold-500 border-t-transparent" />
          </div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center text-sm text-slate-500 dark:text-slate-400">
            <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-500 mb-2" />
            <p className="font-semibold text-slate-800 dark:text-slate-200">All exceptions resolved!</p>
            <p className="mt-0.5">There are currently no transactions requiring human review.</p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 dark:text-[#9BA8BA] space-y-2">
            <p className="text-sm font-semibold text-slate-800 dark:text-[#F4F1E9]">No matching exceptions found</p>
            <p className="text-slate-400">No transactions match your search filter "{search}".</p>
            <button
              onClick={() => setSearch('')}
              className="mt-2 inline-flex items-center space-x-1 rounded-lg bg-gold-400 px-3 py-1.5 text-xs font-bold text-navy-950 hover:bg-gold-500 transition-colors"
            >
              <span>Clear Search</span>
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[820px]">
              <thead className="bg-slate-50 text-slate-500 dark:bg-navy-800/60 dark:text-[#9BA8BA]">
                <tr>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-xs min-w-[200px]">Date &amp; Description</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-xs min-w-[240px]">Flag / Reason</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-xs text-right">Amount</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-xs">Assigned Category</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-xs">Method / Score</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-xs text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-navy-800">
                {filteredItems.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50/60 dark:hover:bg-navy-800/40">
                    <td className="px-4 py-3 min-w-[200px] max-w-[300px]">
                      <span className="text-slate-400 dark:text-[#9BA8BA] block text-xs">{t.date}</span>
                      <p className="font-medium text-sm text-slate-900 dark:text-[#F4F1E9] mt-0.5 break-words whitespace-normal leading-snug">{t.description}</p>
                    </td>
                    <td className="px-4 py-3 min-w-[240px] max-w-[360px]">
                      <div className="inline-block rounded-md bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-800 border border-amber-200/80 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/80 leading-relaxed break-words whitespace-normal">
                        {t.validation_warnings || t.classification_reason || 'Human review flagged'}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-sm font-semibold">
                      {t.debit > 0 ? (
                        <span className="text-rose-600 dark:text-rose-400">- ₹ {t.debit.toFixed(2)}</span>
                      ) : (
                        <span className="text-emerald-600 dark:text-emerald-400">+ ₹ {t.credit.toFixed(2)}</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700 dark:bg-navy-800 dark:text-slate-300">
                        {t.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs">
                      <span className="font-medium text-slate-700 dark:text-[#9BA8BA]">
                        {t.classification_method}
                      </span>
                      {t.confidence_score && (
                        <span className="text-slate-400 ml-1 tabular-nums font-semibold">
                          ({(t.confidence_score * 100).toFixed(0)}%)
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          disabled={approvingId === t.id || submitting}
                          onClick={() => handleApprove(t.id)}
                          className="inline-flex items-center space-x-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-3 py-1.5 text-xs font-semibold shadow-sm transition-colors cursor-pointer"
                          title={`Approve exception for transaction #${t.id}`}
                        >
                          {approvingId === t.id ? (
                            <>
                              <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                              <span>Approving...</span>
                            </>
                          ) : (
                            <>
                              <CheckCircle2 className="h-3.5 w-3.5" />
                              <span>Approve</span>
                            </>
                          )}
                        </button>
                        <button
                          disabled={approvingId !== null || submitting}
                          onClick={() => openCorrectModal(t)}
                          className="inline-flex items-center space-x-1 rounded-lg bg-navy-900 hover:bg-navy-800 disabled:opacity-50 disabled:cursor-not-allowed text-gold-400 border border-gold-500/40 px-3 py-1.5 text-xs font-semibold shadow-sm transition-colors cursor-pointer dark:bg-navy-800 dark:hover:bg-navy-700"
                          title={`Correct transaction #${t.id}`}
                        >
                          <Edit3 className="h-3.5 w-3.5" />
                          <span>Correct</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Human Correction Modal */}
      {selectedTxn && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3 dark:border-slate-800">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center space-x-2">
                <Edit3 className="h-4 w-4 text-brand-600" />
                <span>Correct Transaction #{selectedTxn.id}</span>
              </h3>
              <button
                onClick={() => setSelectedTxn(null)}
                className="rounded p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleCorrectSubmit} className="mt-4 space-y-3 text-xs">
              <div>
                <label className="block text-slate-600 dark:text-slate-300 font-medium mb-1">
                  Category
                </label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-white p-2 text-slate-900 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                >
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
              </div>

              <div>
                <label className="block text-slate-600 dark:text-slate-300 font-medium mb-1">
                  Description
                </label>
                <input
                  type="text"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-white p-2 text-slate-900 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 dark:text-slate-300 font-medium mb-1">
                    Debit Amount (₹)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={newDebit}
                    onChange={(e) => setNewDebit(e.target.value)}
                    placeholder="0.00"
                    className="w-full rounded-lg border border-slate-300 bg-white p-2 text-slate-900 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 dark:text-slate-300 font-medium mb-1">
                    Credit Amount (₹)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={newCredit}
                    onChange={(e) => setNewCredit(e.target.value)}
                    placeholder="0.00"
                    className="w-full rounded-lg border border-slate-300 bg-white p-2 text-slate-900 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-600 dark:text-slate-300 font-medium mb-1">
                  Audit Correction Reason
                </label>
                <input
                  type="text"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="e.g. Verified merchant invoice / Reclassified to Investments"
                  className="w-full rounded-lg border border-slate-300 bg-white p-2 text-slate-900 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                  required
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-200 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setSelectedTxn(null)}
                  className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="rounded-lg bg-brand-600 px-4 py-2 font-semibold text-white shadow hover:bg-brand-700 disabled:opacity-50"
                >
                  {submitting ? 'Saving Correction...' : 'Save & Audit Correction'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

