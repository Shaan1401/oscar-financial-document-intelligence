import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileText,
  ChevronLeft,
  ChevronRight,
  Download,
  Scale,
  ShieldCheck,
  AlertTriangle,
  Layers,
  ArrowLeft,
  Eye,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../services/api';
import { StatementDetailResponse } from '../types';

export const StatementDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<StatementDetailResponse | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTxnId, setSelectedTxnId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api.getStatement(id)
      .then((res) => {
        setData(res);
        if (res.transactions.length > 0) {
          setSelectedTxnId(res.transactions[0].id);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 text-center text-xs text-rose-600">
        Error loading statement: {error || 'Statement not found'}
      </div>
    );
  }

  const { statement, account, transactions } = data;
  const selectedTxn = transactions.find((t) => t.id === selectedTxnId);

  return (
    <div className="space-y-4">
      {/* Top Bar Navigation & Actions */}
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center border-b border-slate-200 pb-4 dark:border-slate-800">
        <div className="flex items-center space-x-3">
          <Link
            to="/statements"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-slate-900 dark:text-white">
                {statement.filename}
              </h1>
              <span className="rounded bg-brand-100 px-2 py-0.5 text-[10px] font-semibold text-brand-700 dark:bg-brand-950 dark:text-brand-300 uppercase">
                {statement.pdf_type}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-mono">
              SHA-256: {statement.file_hash}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Link
            to={`/reconciliation/${statement.id}`}
            className="inline-flex items-center space-x-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <Scale className="h-3.5 w-3.5 text-purple-600" />
            <span>Reconcile</span>
          </Link>
          <a
            href={api.getExcelExportUrl(statement.id)}
            className="inline-flex items-center space-x-1.5 rounded-lg border border-emerald-300 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300"
            download
          >
            <Download className="h-3.5 w-3.5" />
            <span>Excel (.xlsx)</span>
          </a>
          <a
            href={api.getCsvExportUrl(statement.id)}
            className="inline-flex items-center space-x-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
            download
          >
            <Download className="h-3.5 w-3.5" />
            <span>CSV</span>
          </a>
        </div>
      </div>

      {/* Account Details & Reconciliation Summary Strip */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6 rounded-xl border border-slate-200 bg-white p-3.5 text-xs shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div>
          <span className="text-slate-400 text-[10px]">Bank Name</span>
          <p className="font-semibold text-slate-900 dark:text-white truncate">{statement.bank_name || 'Generic Bank'}</p>
        </div>
        <div>
          <span className="text-slate-400 text-[10px]">Account Holder</span>
          <p className="font-semibold text-slate-900 dark:text-white truncate">{account?.holder_name || 'N/A'}</p>
        </div>
        <div>
          <span className="text-slate-400 text-[10px]">Masked Account</span>
          <p className="font-semibold text-slate-900 dark:text-white font-mono">{account?.masked_number || 'N/A'}</p>
        </div>
        <div>
          <span className="text-slate-400 text-[10px]">IFSC Code</span>
          <p className="font-semibold text-slate-900 dark:text-white font-mono">{account?.ifsc_code || 'N/A'}</p>
        </div>
        <div>
          <span className="text-slate-400 text-[10px]">Statement Period</span>
          <p className="font-semibold text-slate-900 dark:text-white truncate">{statement.statement_period || 'N/A'}</p>
        </div>
        <div>
          <span className="text-slate-400 text-[10px]">Reconciliation</span>
          <p className={`font-semibold ${
            statement.reconciliation_status === 'RECONCILED' ? 'text-emerald-600' : 'text-rose-600'
          }`}>
            {statement.reconciliation_status}
          </p>
        </div>
      </div>

      {/* Split-Screen Evidence Viewer */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        {/* Left Panel: PDF Page Renderer */}
        <div className="lg:col-span-5 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
              <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                <Eye className="h-4 w-4 text-brand-600" />
                <span>Original Document Evidence</span>
              </span>
              <div className="flex items-center space-x-2">
                <button
                  disabled={currentPage <= 1}
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  className="rounded p-1 text-slate-500 hover:bg-slate-100 disabled:opacity-30 dark:hover:bg-slate-800"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <span className="text-xs font-mono font-medium text-slate-600 dark:text-slate-300">
                  {currentPage} / {statement.page_count}
                </span>
                <button
                  disabled={currentPage >= statement.page_count}
                  onClick={() => setCurrentPage((p) => Math.min(statement.page_count, p + 1))}
                  className="rounded p-1 text-slate-500 hover:bg-slate-100 disabled:opacity-30 dark:hover:bg-slate-800"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Document Preview Image */}
            <div className="mt-3 flex items-center justify-center rounded-lg border border-slate-200 bg-slate-50 p-2 dark:border-slate-800 dark:bg-slate-950/50 overflow-hidden">
              <img
                src={api.getPagePreviewUrl(statement.id, currentPage)}
                alt={`Page ${currentPage} of ${statement.filename}`}
                className="max-h-[560px] w-auto object-contain rounded shadow-sm"
              />
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
            <span>Rendered via PyMuPDF (200 DPI)</span>
            <span className="font-mono">Page {currentPage} of {statement.page_count}</span>
          </div>
        </div>

        {/* Right Panel: Extracted Transactions Table & Traceability */}
        <div className="lg:col-span-7 flex flex-col space-y-3">
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-800">
              <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                Extracted Transactions ({transactions.length})
              </span>
              <span className="text-[11px] text-slate-500">
                Click a transaction to view raw narration and bounding coordinates
              </span>
            </div>

            <div className="max-h-[380px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="sticky top-0 bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                  <tr>
                    <th className="px-3 py-2 font-semibold">#</th>
                    <th className="px-3 py-2 font-semibold">Date</th>
                    <th className="px-3 py-2 font-semibold">Description</th>
                    <th className="px-3 py-2 font-semibold text-right">Debit</th>
                    <th className="px-3 py-2 font-semibold text-right">Credit</th>
                    <th className="px-3 py-2 font-semibold">Category</th>
                    <th className="px-3 py-2 font-semibold">Method</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {transactions.map((t) => {
                    const isSelected = t.id === selectedTxnId;
                    return (
                      <tr
                        key={t.id}
                        onClick={() => {
                          setSelectedTxnId(t.id);
                          setCurrentPage(t.source_page);
                        }}
                        className={`cursor-pointer transition-colors ${
                          isSelected
                            ? 'bg-brand-50/80 font-medium dark:bg-brand-950/50'
                            : 'hover:bg-slate-50/60 dark:hover:bg-slate-800/40'
                        }`}
                      >
                        <td className="px-3 py-2 font-mono text-slate-400">{t.row_sequence}</td>
                        <td className="px-3 py-2 whitespace-nowrap font-mono">{t.date}</td>
                        <td className="px-3 py-2 max-w-[200px] truncate" title={t.description}>
                          {t.description}
                        </td>
                        <td className="px-3 py-2 text-right font-mono text-rose-600">
                          {t.debit > 0 ? `₹ ${t.debit.toFixed(2)}` : '-'}
                        </td>
                        <td className="px-3 py-2 text-right font-mono text-emerald-600">
                          {t.credit > 0 ? `₹ ${t.credit.toFixed(2)}` : '-'}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap">
                          <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                            {t.category}
                          </span>
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap">
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
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Selected Transaction Traceability Card */}
          {selectedTxn && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900 text-xs space-y-2">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2 dark:border-slate-800">
                <span className="font-semibold text-slate-900 dark:text-white">
                  Traceability Card (Row {selectedTxn.row_sequence})
                </span>
                <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-mono text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  Page {selectedTxn.source_page}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-1">
                <div>
                  <span className="text-slate-400 text-[10px]">Raw Narration from PDF</span>
                  <p className="font-mono text-slate-800 dark:text-slate-200 bg-slate-50 dark:bg-slate-800/60 p-2 rounded border border-slate-200 dark:border-slate-700 mt-0.5">
                    {selectedTxn.raw_description || selectedTxn.description}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px]">Classification Explanation</span>
                  <p className="text-slate-800 dark:text-slate-200 bg-slate-50 dark:bg-slate-800/60 p-2 rounded border border-slate-200 dark:border-slate-700 mt-0.5">
                    {selectedTxn.classification_reason || 'Standard classification'}
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                <span>Method: <strong>{selectedTxn.classification_method}</strong> ({selectedTxn.rule_id || selectedTxn.model_version || 'N/A'})</span>
                <span>Score: <strong>{selectedTxn.confidence_score ? (selectedTxn.confidence_score * 100).toFixed(1) + '%' : '100%'}</strong></span>
                <span>Status: <strong className={selectedTxn.review_status === 'APPROVED' ? 'text-emerald-600' : 'text-amber-600'}>{selectedTxn.review_status}</strong></span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

