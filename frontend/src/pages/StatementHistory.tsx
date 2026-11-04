import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Download,
  Trash2,
  Scale,
  ExternalLink,
  Search,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { api } from '../services/api';
import { Statement } from '../types';

export const StatementHistory: React.FC = () => {
  const [statements, setStatements] = useState<Statement[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const loadStatements = () => {
    setLoading(true);
    api.getStatements()
      .then(setStatements)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadStatements();
  }, []);

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete statement "${name}" and its associated records?`)) {
      return;
    }
    try {
      await api.deleteStatement(id);
      loadStatements();
    } catch (err: any) {
      alert(`Deletion failed: ${err.message}`);
    }
  };

  const filtered = statements.filter((s) => {
    const q = search.toLowerCase();
    return (
      s.filename.toLowerCase().includes(q) ||
      (s.bank_name && s.bank_name.toLowerCase().includes(q)) ||
      s.reconciliation_status.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Statement History
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Audit-tracked bank statements, extracted summaries, and exports.
          </p>
        </div>
        <Link
          to="/upload"
          className="inline-flex items-center space-x-2 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-brand-700 transition"
        >
          <UploadCloud className="h-4 w-4" />
          <span>Upload Statement</span>
        </Link>
      </div>

      {/* Search Filter Bar */}
      <div className="flex items-center rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-sm dark:border-slate-800 dark:bg-slate-900 max-w-md">
        <Search className="h-4 w-4 text-slate-400 mr-2 shrink-0" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by filename, bank, or status..."
          className="w-full bg-transparent text-xs text-slate-900 placeholder-slate-400 focus:outline-none dark:text-white"
        />
      </div>

      {/* Statements Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-7 w-7 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 dark:text-slate-400">
            No matching bank statements found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-semibold">Document</th>
                  <th className="px-4 py-3 font-semibold">Bank & Period</th>
                  <th className="px-4 py-3 font-semibold">Pages / Layout</th>
                  <th className="px-4 py-3 font-semibold">Transactions</th>
                  <th className="px-4 py-3 font-semibold">Total Debits / Credits</th>
                  <th className="px-4 py-3 font-semibold">Reconciliation</th>
                  <th className="px-4 py-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {filtered.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                    <td className="px-4 py-3">
                      <Link to={`/statements/${s.id}`} className="font-semibold text-brand-600 hover:underline dark:text-brand-400">
                        {s.filename}
                      </Link>
                      <p className="text-[10px] text-slate-400 font-mono">ID: {s.id.slice(0, 8)}...</p>
                    </td>
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-800 dark:text-slate-200">{s.bank_name || 'Generic Bank'}</p>
                      <p className="text-[11px] text-slate-500">{s.statement_period || 'N/A'}</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                        {s.page_count} {s.page_count === 1 ? 'page' : 'pages'} • {s.pdf_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono font-medium">
                      {s.transaction_count ?? '-'}
                    </td>
                    <td className="px-4 py-3 font-mono">
                      <div className="text-rose-600">- ₹ {(s.total_debits ?? 0).toFixed(2)}</div>
                      <div className="text-emerald-600">+ ₹ {(s.total_credits ?? 0).toFixed(2)}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center space-x-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                          s.reconciliation_status === 'RECONCILED'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300'
                            : s.reconciliation_status === 'MISMATCH'
                            ? 'bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300'
                            : 'bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300'
                        }`}
                      >
                        {s.reconciliation_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <Link
                          to={`/statements/${s.id}`}
                          title="Inspect Evidence Viewer"
                          className="rounded p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Link>
                        <a
                          href={api.getExcelExportUrl(s.id)}
                          title="Download Excel (.xlsx)"
                          className="rounded p-1.5 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/40"
                          download
                        >
                          <Download className="h-4 w-4" />
                        </a>
                        <button
                          onClick={() => handleDelete(s.id, s.filename)}
                          title="Delete Statement"
                          className="rounded p-1.5 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40"
                        >
                          <Trash2 className="h-4 w-4" />
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
    </div>
  );
};

