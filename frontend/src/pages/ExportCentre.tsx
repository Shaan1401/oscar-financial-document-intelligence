import React, { useEffect, useState } from 'react';
import {
  Download,
  FileSpreadsheet,
  FileText,
  CheckCircle2,
  Layers,
  ShieldCheck,
  Table,
} from 'lucide-react';
import { api } from '../services/api';
import { Statement } from '../types';
import { SearchableSelect } from '../components/Common/SearchableSelect';

export const ExportCentre: React.FC = () => {
  const [statements, setStatements] = useState<Statement[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getStatements()
      .then((list) => {
        setStatements(list);
        if (list.length > 0) {
          setSelectedId(list[0].id);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const selectedStmt = statements.find((s) => s.id === selectedId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          Export Centre
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Generate production-ready multi-sheet Excel (.xlsx) workbooks and CSV files with financial precision.
        </p>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
        </div>
      ) : statements.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-xs text-slate-500 dark:border-navy-800 dark:bg-navy-900">
          No bank statements available to export. Upload a statement first.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 w-full max-w-full">
          {/* Left Column: Statement Selector & Download Cards */}
          <div className="min-w-0 w-full max-w-full space-y-4">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-navy-800 dark:bg-navy-900 min-w-0 w-full max-w-full">
              <label className="block text-xs font-semibold text-slate-800 dark:text-slate-200 mb-2">
                Select Statement to Export:
              </label>
              <div className="w-full min-w-0 max-w-full">
                <SearchableSelect
                  options={statements.map((s) => ({
                    value: s.id,
                    label: s.filename,
                    sublabel: `${s.bank_name || 'Bank'} (${s.transaction_count ?? 0} txns)`,
                    badge: s.reconciliation_status,
                  }))}
                  value={selectedId}
                  onChange={(val) => setSelectedId(val)}
                  placeholder="Select statement..."
                  searchPlaceholder="Search statements by name or bank..."
                  aria-label="Select Statement to Export"
                  className="w-full min-w-0 max-w-full"
                />
              </div>

              {selectedStmt && (
                <div className="mt-4 rounded-lg bg-[#FDFBF7] p-3.5 text-xs dark:bg-navy-800/60 border border-slate-200/80 dark:border-navy-700/60 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Document Type:</span>
                    <span className="font-semibold uppercase">{selectedStmt.pdf_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Extracted Rows:</span>
                    <span className="font-mono font-bold">{selectedStmt.transaction_count} transactions</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Reconciliation:</span>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                      {selectedStmt.reconciliation_status}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Download Cards */}
            {selectedStmt && (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 w-full max-w-full">
                <a
                  href={api.getExcelExportUrl(selectedStmt.id)}
                  download
                  className="flex flex-col justify-between rounded-xl border border-emerald-200 bg-emerald-50/50 p-5 shadow-sm hover:bg-emerald-100/50 dark:border-emerald-900/60 dark:bg-emerald-950/30 transition group min-w-0"
                >
                  <div>
                    <div className="flex items-center space-x-2 text-emerald-700 dark:text-emerald-300">
                      <FileSpreadsheet className="h-6 w-6 shrink-0" />
                      <h4 className="font-bold text-sm truncate">Excel Workbook</h4>
                    </div>
                    <p className="mt-2 text-[11px] text-slate-600 dark:text-slate-400">
                      Formatted multi-tab .xlsx with Transactions, Category Summary, and Reconciliation Audit.
                    </p>
                  </div>
                  <div className="mt-4 flex items-center space-x-1.5 text-xs font-semibold text-emerald-700 dark:text-emerald-300">
                    <Download className="h-4 w-4 shrink-0" />
                    <span>Download .XLSX</span>
                  </div>
                </a>

                <a
                  href={api.getCsvExportUrl(selectedStmt.id)}
                  download
                  className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:bg-slate-50 dark:border-navy-800 dark:bg-navy-900 dark:hover:bg-navy-800/60 transition group min-w-0"
                >
                  <div>
                    <div className="flex items-center space-x-2 text-slate-800 dark:text-slate-200">
                      <FileText className="h-6 w-6 text-brand-600 shrink-0" />
                      <h4 className="font-bold text-sm truncate">Standard CSV</h4>
                    </div>
                    <p className="mt-2 text-[11px] text-slate-600 dark:text-slate-400">
                      Clean UTF-8 CSV with assigned categories and formula injection protection.
                    </p>
                  </div>
                  <div className="mt-4 flex items-center space-x-1.5 text-xs font-semibold text-brand-600 dark:text-brand-400">
                    <Download className="h-4 w-4 shrink-0" />
                    <span>Download .CSV</span>
                  </div>
                </a>
              </div>
            )}
          </div>

          {/* Right Column: Workbook Structure Preview */}
          <div className="min-w-0 w-full max-w-full rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-navy-800 dark:bg-navy-900 space-y-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center space-x-2">
              <Table className="h-4 w-4 text-brand-600" />
              <span>Multi-Sheet Workbook Specifications</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="rounded-lg border border-slate-200 p-3 dark:border-navy-800">
                <span className="font-semibold text-brand-600 dark:text-brand-400">
                  Sheet 1: Transactions
                </span>
                <p className="text-slate-500 dark:text-slate-400 mt-1">
                  Date, Description, Debit (₹), Credit (₹), Balance (₹), Assigned Category, Classification Method, Confidence Score, Review Status, Source Page.
                </p>
              </div>

              <div className="rounded-lg border border-slate-200 p-3 dark:border-navy-800">
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                  Sheet 2: Account Summary
                </span>
                <p className="text-slate-500 dark:text-slate-400 mt-1">
                  Bank Name, Account Holder Name, Masked Account Number, IFSC Code, Statement Period, Currency Code.
                </p>
              </div>

              <div className="rounded-lg border border-slate-200 p-3 dark:border-navy-800">
                <span className="font-semibold text-purple-600 dark:text-purple-400">
                  Sheet 3: Reconciliation
                </span>
                <p className="text-slate-500 dark:text-slate-400 mt-1">
                  Opening Balance, Total Credits, Total Debits, Expected Closing Balance, Actual Closing Balance, Mathematical Variance, Reconciliation Status.
                </p>
              </div>

              <div className="rounded-lg border border-slate-200 p-3 dark:border-navy-800">
                <span className="font-semibold text-slate-600 dark:text-slate-300">
                  Sheet 4: Processing Audit
                </span>
                <p className="text-slate-500 dark:text-slate-400 mt-1">
                  SHA-256 File Hash, Ingestion Timestamp, Extractor Version, OCR Status, Model Version.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

