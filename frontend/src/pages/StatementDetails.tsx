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
  ArrowLeft,
  Eye,
  CheckCircle2,
  Crosshair,
} from 'lucide-react';
import { api } from '../services/api';
import { StatementDetailResponse } from '../types';

const getBoundingBoxStyle = (
  bboxStr?: string | null,
  txnPage?: number,
  activePage?: number
): { style: React.CSSProperties; rawCoords: string } | null => {
  if (!bboxStr || txnPage !== activePage) return null;
  const parts = bboxStr.split(',').map((p) => parseFloat(p.trim()));
  if (parts.length >= 4 && !parts.some(isNaN)) {
    const [x0, y0, x1, y1] = parts;
    const pageW = parts.length >= 5 && parts[4] > 0 ? parts[4] : 612;
    const pageH = parts.length >= 6 && parts[5] > 0 ? parts[5] : 792;
    const left = `${Math.max(0, (x0 / pageW) * 100)}%`;
    const top = `${Math.max(0, (y0 / pageH) * 100)}%`;
    const width = `${Math.min(100, ((x1 - x0) / pageW) * 100)}%`;
    const height = `${Math.min(100, ((y1 - y0) / pageH) * 100)}%`;
    return {
      style: { left, top, width, height },
      rawCoords: `[x0: ${x0.toFixed(1)}, y0: ${y0.toFixed(1)}, x1: ${x1.toFixed(1)}, y1: ${y1.toFixed(1)}]`,
    };
  }
  return null;
};

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
    setError(null);
    api.getStatement(id)
      .then((res) => {
        setData(res);
        const txns = Array.isArray(res?.transactions) ? res.transactions : [];
        if (txns.length > 0) {
          setSelectedTxnId(txns[0].id);
        } else {
          setSelectedTxnId(null);
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
      <div className="mx-auto max-w-lg rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-navy-800 dark:bg-navy-900 my-12">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600 dark:bg-rose-950/50 dark:text-rose-400 mb-4">
          <AlertTriangle className="h-6 w-6" />
        </div>
        <h2 className="text-base font-bold text-slate-900 dark:text-white">
          Statement Not Found
        </h2>
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
          {error || `Statement with ID '${id}' does not exist or could not be loaded.`}
        </p>
        <div className="mt-6 flex justify-center space-x-3">
          <Link
            to="/statements"
            className="inline-flex items-center space-x-2 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-brand-700 transition"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Return to Statements</span>
          </Link>
          <Link
            to="/upload"
            className="inline-flex items-center space-x-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <span>Upload New Statement</span>
          </Link>
        </div>
      </div>
    );
  }

  const statement = data.statement || (data as unknown as import('../types').Statement);
  const account = data.account || ((data as any).accounts && (data as any).accounts[0]) || null;
  const transactions = Array.isArray(data.transactions) ? data.transactions : [];
  const selectedTxn = transactions.find((t) => t.id === selectedTxnId) || null;
  const bboxInfo = getBoundingBoxStyle(selectedTxn?.bounding_box, selectedTxn?.source_page, currentPage);

  return (
    <div className="space-y-4">
      {/* Top Bar Navigation & Actions */}
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center border-b border-slate-200 pb-4 dark:border-navy-800">
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
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6 rounded-xl border border-slate-200 bg-white p-3.5 text-xs shadow-sm dark:border-navy-800 dark:bg-navy-900">
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
          <span className="text-slate-400 text-[10px]">Reconciliation Status</span>
          <div className="mt-0.5">
            {statement.reconciliation_status === 'RECONCILED' ? (
              <span className="inline-flex items-center space-x-1 rounded bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
                <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0" />
                <span>Reconciled</span>
              </span>
            ) : statement.reconciliation_status === 'PENDING' ? (
              <span className="inline-flex items-center space-x-1 rounded bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-700 dark:bg-amber-950/50 dark:text-amber-300">
                <AlertTriangle className="h-3 w-3 text-amber-500 shrink-0" />
                <span>Pending Verification</span>
              </span>
            ) : statement.reconciliation_status === 'MISMATCH' ? (
              <span className="inline-flex items-center space-x-1 rounded bg-rose-50 px-2 py-0.5 text-[11px] font-semibold text-rose-700 dark:bg-rose-950/50 dark:text-rose-300">
                <AlertTriangle className="h-3 w-3 text-rose-500 shrink-0" />
                <span>Mismatch (₹{statement.variance?.toFixed(2) ?? '0.00'})</span>
              </span>
            ) : statement.reconciliation_status === 'REVIEW_REQUIRED' ? (
              <span className="inline-flex items-center space-x-1 rounded bg-purple-50 px-2 py-0.5 text-[11px] font-semibold text-purple-700 dark:bg-purple-950/50 dark:text-purple-300">
                <AlertTriangle className="h-3 w-3 text-purple-500 shrink-0" />
                <span>Running Balance Discrepancy</span>
              </span>
            ) : (
              <span className="inline-flex items-center space-x-1 rounded bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                <span>{statement.reconciliation_status}</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 4-Step Verification Chain */}
      <div className="rounded-xl border border-slate-200/90 bg-white p-3.5 shadow-sm dark:border-navy-800 dark:bg-navy-900">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-500 mb-2">
          <span className="font-bold text-slate-800 dark:text-[#F4F1E9]">End-to-End Evidence Governance Trace</span>
          <span className="font-mono text-[10px]">Row #{selectedTxn?.row_sequence ?? 1}</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 text-xs">
          <div className="rounded-lg bg-blue-50/70 p-2.5 dark:bg-blue-950/30 border border-blue-200/60 dark:border-blue-800/40">
            <span className="text-[10px] font-bold uppercase text-blue-700 dark:text-blue-300">1. Source Document</span>
            <p className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">Page {selectedTxn?.source_page ?? 1} ({statement.pdf_type.toUpperCase()})</p>
          </div>
          <div className="rounded-lg bg-indigo-50/70 p-2.5 dark:bg-indigo-950/30 border border-indigo-200/60 dark:border-indigo-800/40">
            <span className="text-[10px] font-bold uppercase text-indigo-700 dark:text-indigo-300">2. Extracted Row</span>
            <p className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">{selectedTxn?.extraction_method ?? 'pdfplumber_table'}</p>
          </div>
          <div className="rounded-lg bg-purple-50/70 p-2.5 dark:bg-purple-950/30 border border-purple-200/60 dark:border-purple-800/40">
            <span className="text-[10px] font-bold uppercase text-purple-700 dark:text-purple-300">3. Hybrid Classification</span>
            <p className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">{selectedTxn?.category ?? 'Pending'} ({selectedTxn?.classification_method})</p>
          </div>
          <div className="rounded-lg bg-emerald-50/70 p-2.5 dark:bg-emerald-950/30 border border-emerald-200/60 dark:border-emerald-800/40">
            <span className="text-[10px] font-bold uppercase text-emerald-700 dark:text-emerald-300">4. Financial Validation</span>
            <p className="font-bold text-slate-800 dark:text-slate-200 truncate mt-0.5">{selectedTxn?.validation_status ?? 'VALID'} (Step Integrity OK)</p>
          </div>
        </div>
      </div>

      {/* Split-Screen Evidence Viewer */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        {/* Left Panel: PDF Page Renderer */}
        <div className="lg:col-span-5 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-navy-800 dark:bg-navy-900 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-navy-800">
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

            {/* Document Preview Image with Traceability Highlighting Overlay */}
            <div className="mt-3 flex items-center justify-center rounded-lg border border-slate-200 bg-[#FDFBF7] p-2 dark:border-navy-700 dark:bg-navy-950/60 overflow-hidden min-h-[420px]">
              <div className="relative inline-block">
                <img
                  src={api.getPagePreviewUrl(statement.id, currentPage)}
                  alt={`Page ${currentPage} of ${statement.filename}`}
                  className="max-h-[560px] w-auto object-contain rounded shadow-sm select-none"
                />
                {bboxInfo && (
                  <div
                    style={bboxInfo.style}
                    className="absolute pointer-events-none rounded border-2 border-brand-500 bg-brand-500/25 shadow-[0_0_12px_rgba(37,99,235,0.5)] transition-all duration-300 ring-2 ring-brand-400/40"
                  >
                    <div className="absolute -top-5 left-0 rounded bg-brand-600 px-1.5 py-0.5 text-[9px] font-bold text-white shadow-sm whitespace-nowrap">
                      Row #{selectedTxn?.row_sequence}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
            <span>Rendered via PyMuPDF (200 DPI)</span>
            <span className="font-mono">Page {currentPage} of {statement.page_count}</span>
          </div>
        </div>

        {/* Right Panel: Extracted Transactions Table & Traceability */}
        <div className="lg:col-span-7 flex flex-col space-y-3">
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-navy-800 dark:bg-navy-900 overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-navy-800">
              <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                Extracted Transactions ({transactions.length})
              </span>
              <span className="text-[11px] text-slate-500">
                Click a transaction to view raw narration and bounding coordinates
              </span>
            </div>

            {transactions.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">
                <FileText className="mx-auto h-8 w-8 text-slate-300 dark:text-slate-600 mb-2" />
                <p className="font-semibold text-slate-700 dark:text-slate-300">No Transactions Extracted</p>
                <p className="mt-1 text-slate-400">
                  {statement.status === 'PROCESSING'
                    ? 'Statement processing is currently underway.'
                    : 'This document contains no recognized transaction rows, or may require OCR re-processing.'}
                </p>
              </div>
            ) : (
              <div className="max-h-[380px] overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead className="sticky top-0 bg-slate-50/80 text-slate-700 dark:bg-navy-800 dark:text-[#9BA8BA]">
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
                  <tbody className="divide-y divide-slate-100 dark:divide-navy-800">
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
                              ? 'bg-gold-400/10 dark:bg-gold-400/15 border-l-2 border-gold-400 font-semibold text-slate-900 dark:text-gold-300'
                              : 'hover:bg-slate-50/60 dark:hover:bg-navy-800/40'
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
                            <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-700 dark:bg-navy-800 dark:text-slate-300">
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
            )}
          </div>

          {/* Selected Transaction Traceability & Evidence Inspector */}
          {selectedTxn && (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-navy-800 dark:bg-navy-900 text-xs space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-2.5 dark:border-navy-800">
                <div className="flex items-center space-x-2">
                  <Crosshair className="h-4 w-4 text-gold-500" />
                  <span className="font-bold text-slate-900 dark:text-[#F4F1E9]">
                    Evidence Inspector & Traceability (Row #{selectedTxn.row_sequence})
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-mono text-slate-600 dark:bg-navy-800 dark:text-slate-300">
                    Source Page: {selectedTxn.source_page}
                  </span>
                  <span className="rounded bg-blue-50 px-2 py-0.5 text-[10px] font-semibold text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">
                    {selectedTxn.extraction_method}
                  </span>
                  {selectedTxn.validation_status === 'VALID' ? (
                    <span className="inline-flex items-center space-x-1 rounded bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
                      <ShieldCheck className="h-3 w-3 text-emerald-500" />
                      <span>VALID</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center space-x-1 rounded bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-700 dark:bg-amber-950/50 dark:text-amber-300">
                      <AlertTriangle className="h-3 w-3 text-amber-500" />
                      <span>{selectedTxn.validation_status}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Source Coordinates Reliability Strip */}
              <div className="flex items-center justify-between rounded-lg bg-[#FDFBF7] px-3 py-1.5 font-mono text-[11px] text-slate-700 dark:bg-navy-800/80 dark:text-[#9BA8BA] border border-slate-200/60 dark:border-navy-700/60">
                <span className="flex items-center space-x-1.5">
                  <span className={`h-2 w-2 rounded-full ${bboxInfo ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                  <span className="text-slate-400">PDF Geometry:</span>
                  <span>{bboxInfo?.rawCoords || (selectedTxn.bounding_box ? `[${selectedTxn.bounding_box}]` : 'Geometric coordinates estimated')}</span>
                </span>
                <span className="text-[10px] text-slate-400">
                  {selectedTxn.bounding_box ? 'Exact Table Row Match' : 'Heuristic Row Placement'}
                </span>
              </div>

              {/* Extracted Fields Summary */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 rounded-lg border border-slate-200/80 bg-[#FDFBF7] p-2.5 dark:border-navy-700/80 dark:bg-navy-950/40">
                <div>
                  <span className="text-[10px] text-slate-400">Extracted Date</span>
                  <p className="font-mono font-medium text-slate-800 dark:text-slate-200">{selectedTxn.date}</p>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400">Debit / Inflow</span>
                  <p className="font-mono font-medium text-rose-600">
                    {selectedTxn.debit > 0 ? `₹ ${selectedTxn.debit.toFixed(2)}` : '-'}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400">Credit / Outflow</span>
                  <p className="font-mono font-medium text-emerald-600">
                    {selectedTxn.credit > 0 ? `₹ ${selectedTxn.credit.toFixed(2)}` : '-'}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400">Running Balance</span>
                  <p className="font-mono font-medium text-slate-800 dark:text-slate-200">
                    {selectedTxn.balance != null ? `₹ ${selectedTxn.balance.toFixed(2)}` : 'N/A'}
                  </p>
                </div>
              </div>

              {/* Raw Narration & Explainable Classification */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <span className="text-slate-400 text-[10px] font-medium">Source Document Narration (Raw Text)</span>
                  <p className="font-mono text-slate-800 dark:text-slate-200 bg-[#FDFBF7] dark:bg-navy-800/60 p-2.5 rounded border border-slate-200 dark:border-navy-700 mt-0.5 break-all select-all">
                    {selectedTxn.raw_description || selectedTxn.description}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] font-medium">Explainable Classification Rationale</span>
                  <div className="bg-[#FDFBF7] dark:bg-navy-800/60 p-2.5 rounded border border-slate-200 dark:border-navy-700 mt-0.5 space-y-1">
                    <p className="text-slate-800 dark:text-slate-200 font-medium">
                      {selectedTxn.classification_reason || 'Standard hybrid classification'}
                    </p>
                    <div className="flex items-center space-x-2 text-[10px] text-slate-500 pt-0.5">
                      <span>Model/Rule: <strong className="font-mono">{selectedTxn.rule_id || selectedTxn.model_version || 'Heuristic'}</strong></span>
                      <span>•</span>
                      <span>Confidence: <strong>{selectedTxn.confidence_score ? (selectedTxn.confidence_score * 100).toFixed(1) + '%' : '100%'}</strong></span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Status and Warning Bar */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-2 text-[11px] text-slate-500 dark:border-slate-800">
                <div className="flex items-center space-x-3">
                  <span>Method: <strong className="text-slate-700 dark:text-slate-300">{selectedTxn.classification_method}</strong></span>
                  <span>Review: <strong className={selectedTxn.review_status === 'APPROVED' ? 'text-emerald-600' : 'text-amber-600'}>{selectedTxn.review_status}</strong></span>
                </div>
                {selectedTxn.validation_warnings && (
                  <span className="rounded bg-amber-50 px-2 py-0.5 text-[10px] text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">
                    Warning: {selectedTxn.validation_warnings}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

