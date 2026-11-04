import React, { useEffect, useState } from 'react';
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

  // Modal correction form state
  const [newCategory, setNewCategory] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newDebit, setNewDebit] = useState<string>('');
  const [newCredit, setNewCredit] = useState<string>('');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadQueue = () => {
    setLoading(true);
    api.getReviewQueue()
      .then((res) => setItems(res.items))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleApprove = async (id: number) => {
    try {
      await api.approveTransaction(id, 'Approved via Review Centre');
      loadQueue();
    } catch (err: any) {
      alert(`Approval failed: ${err.message}`);
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
    setSubmitting(true);
    try {
      await api.correctTransaction(selectedTxn.id, {
        new_category: newCategory,
        new_description: newDesc,
        new_debit: newDebit ? parseFloat(newDebit) : undefined,
        new_credit: newCredit ? parseFloat(newCredit) : undefined,
        reason: reason || 'Human correction via Review Centre',
      });
      setSelectedTxn(null);
      loadQueue();
    } catch (err: any) {
      alert(`Correction failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          Review & Exceptions Centre
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Audit flagged transactions, resolve confidence warnings, and apply explainable human corrections.
        </p>
      </div>

      {/* Queue Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
        <div className="border-b border-slate-200 px-4 py-3 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 text-amber-500" />
            <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
              Pending Exceptions ({items.length})
            </span>
          </div>
          <span className="text-[11px] text-slate-400">
            Transactions with rule conflicts, low ML confidence, or anomaly indicators
          </span>
        </div>

        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-7 w-7 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
          </div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 dark:text-slate-400">
            <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-500 mb-2" />
            <p className="font-semibold text-slate-800 dark:text-slate-200">All exceptions resolved!</p>
            <p className="mt-0.5">There are currently no transactions requiring human review.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-semibold">Date & Description</th>
                  <th className="px-4 py-3 font-semibold">Flag / Reason</th>
                  <th className="px-4 py-3 font-semibold text-right">Amount</th>
                  <th className="px-4 py-3 font-semibold">Assigned Category</th>
                  <th className="px-4 py-3 font-semibold">Method / Score</th>
                  <th className="px-4 py-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {items.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                    <td className="px-4 py-3 max-w-[260px]">
                      <span className="font-mono text-slate-400">{t.date}</span>
                      <p className="truncate font-medium text-slate-900 dark:text-white mt-0.5">{t.description}</p>
                    </td>
                    <td className="px-4 py-3 max-w-[260px]">
                      <span className="rounded bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800">
                        {t.validation_warnings || t.classification_reason || 'Human review flagged'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono">
                      {t.debit > 0 ? (
                        <span className="text-rose-600">- ₹ {t.debit.toFixed(2)}</span>
                      ) : (
                        <span className="text-emerald-600">+ ₹ {t.credit.toFixed(2)}</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                        {t.category}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-medium text-slate-700 dark:text-slate-300">
                        {t.classification_method}
                      </span>
                      {t.confidence_score && (
                        <span className="text-slate-400 ml-1 font-mono">
                          ({(t.confidence_score * 100).toFixed(0)}%)
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleApprove(t.id)}
                          className="rounded bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950/50 dark:text-emerald-300"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => openCorrectModal(t)}
                          className="rounded bg-brand-50 px-2.5 py-1 text-[11px] font-semibold text-brand-700 hover:bg-brand-100 dark:bg-brand-950/50 dark:text-brand-300"
                        >
                          Correct
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

