import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  UploadCloud,
  FileCheck,
  AlertCircle,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldCheck,
  FileText,
} from 'lucide-react';
import { api } from '../services/api';
import { Statement } from '../types';

export const Upload: React.FC = () => {
  const navigate = useNavigate();
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [currentStage, setCurrentStage] = useState<number>(0);
  const [result, setResult] = useState<Statement | null>(null);
  const [error, setError] = useState<string | null>(null);

  const STAGES = [
    'Validating PDF structure & SHA-256 hash',
    'Extracting text layers & table geometry',
    'Classifying transactions (Explainable Hybrid Rules + ML)',
    'Calculating financial reconciliation balances',
    'Finalizing persistence & audit trail',
  ];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      selectFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      selectFile(e.target.files[0]);
    }
  };

  const selectFile = (selectedFile: File) => {
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF bank statements are supported (.pdf).');
      return;
    }
    if (selectedFile.size > 20 * 1024 * 1024) {
      setError('File size exceeds 20 MB limit.');
      return;
    }
    setError(null);
    setResult(null);
    setFile(selectedFile);
  };

  const handleUploadAndProcess = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setCurrentStage(1);

    // Simulate stage visual progression while backend executes
    const timer1 = setTimeout(() => setCurrentStage(2), 500);
    const timer2 = setTimeout(() => setCurrentStage(3), 1000);
    const timer3 = setTimeout(() => setCurrentStage(4), 1600);

    try {
      const stmt = await api.uploadStatement(file);
      setCurrentStage(5);
      setResult(stmt);
    } catch (err: any) {
      setError(err.message || 'Processing failed. Please check document validity.');
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setUploading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          Upload Bank Statement
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Process text-based, scanned, or multi-page PDF statements with automated layout detection.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition ${
          dragActive
            ? 'border-brand-500 bg-brand-50/50 dark:border-brand-400 dark:bg-brand-950/20'
            : 'border-slate-300 bg-white hover:border-slate-400 dark:border-slate-800 dark:bg-slate-900'
        }`}
      >
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-400">
          <UploadCloud className="h-7 w-7" />
        </div>
        <h3 className="mt-4 text-sm font-semibold text-slate-900 dark:text-white">
          Drag and drop your bank statement PDF
        </h3>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Supports text, scanned, and mixed formats up to 20 MB
        </p>

        <label className="mt-4 inline-flex cursor-pointer items-center rounded-lg border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700">
          <span>Browse File</span>
          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleChange}
            className="sr-only"
            disabled={uploading}
          />
        </label>

        {file && (
          <div className="mt-4 flex items-center space-x-2 rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-800 dark:bg-slate-800 dark:text-slate-200">
            <FileText className="h-4 w-4 text-brand-600 dark:text-brand-400" />
            <span>{file.name}</span>
            <span className="text-slate-500 font-mono">({(file.size / 1024).toFixed(1)} KB)</span>
          </div>
        )}
      </div>

      {/* Action CTA */}
      {file && !uploading && !result && (
        <div className="flex justify-end">
          <button
            onClick={handleUploadAndProcess}
            className="inline-flex items-center space-x-2 rounded-lg bg-brand-600 px-5 py-2.5 text-xs font-semibold text-white shadow hover:bg-brand-700 transition"
          >
            <span>Start Automated Processing</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Processing Stages Progress */}
      {uploading && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-900 dark:text-white">
              Processing Statement...
            </span>
            <span className="text-xs font-mono text-brand-600 dark:text-brand-400 font-bold">
              Stage {currentStage} of {STAGES.length}
            </span>
          </div>
          <div className="space-y-2.5">
            {STAGES.map((stageName, idx) => {
              const stageNum = idx + 1;
              const isDone = stageNum < currentStage;
              const isCurrent = stageNum === currentStage;
              return (
                <div key={stageName} className="flex items-center space-x-3 text-xs">
                  {isDone ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                  ) : isCurrent ? (
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-brand-600 border-t-transparent shrink-0" />
                  ) : (
                    <Clock className="h-4 w-4 text-slate-300 dark:text-slate-600 shrink-0" />
                  )}
                  <span
                    className={
                      isDone
                        ? 'text-slate-500 dark:text-slate-400'
                        : isCurrent
                        ? 'font-semibold text-slate-900 dark:text-white'
                        : 'text-slate-400 dark:text-slate-600'
                    }
                  >
                    {stageName}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="flex items-center space-x-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-300">
          <AlertCircle className="h-5 w-5 shrink-0 text-rose-600 dark:text-rose-400" />
          <div className="flex-1">
            <p className="font-semibold">Processing Failed</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Success Extraction Summary */}
      {result && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/40 p-6 shadow-sm dark:border-emerald-900/50 dark:bg-emerald-950/20 space-y-4">
          <div className="flex items-center space-x-2 text-emerald-700 dark:text-emerald-300">
            <CheckCircle2 className="h-5 w-5" />
            <h3 className="text-sm font-semibold">Extraction & Classification Complete</h3>
          </div>

          <div className="grid grid-cols-2 gap-4 rounded-lg bg-white p-4 text-xs dark:bg-slate-900 border border-slate-200 dark:border-slate-800 sm:grid-cols-4">
            <div>
              <span className="text-slate-500">Bank Identified:</span>
              <p className="font-semibold text-slate-900 dark:text-white">{result.bank_name || 'Generic Bank'}</p>
            </div>
            <div>
              <span className="text-slate-500">Document Type:</span>
              <p className="font-semibold uppercase text-slate-900 dark:text-white">{result.pdf_type}</p>
            </div>
            <div>
              <span className="text-slate-500">Transactions:</span>
              <p className="font-semibold text-slate-900 dark:text-white font-mono">{result.transaction_count} rows</p>
            </div>
            <div>
              <span className="text-slate-500">Reconciliation:</span>
              <p className="font-semibold text-emerald-600 dark:text-emerald-400">{result.reconciliation_status}</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              onClick={() => {
                setFile(null);
                setResult(null);
              }}
              className="text-xs font-medium text-slate-600 hover:underline dark:text-slate-400"
            >
              Upload Another Statement
            </button>
            <Link
              to={`/statements/${result.id}`}
              className="inline-flex items-center space-x-1.5 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow hover:bg-brand-700"
            >
              <span>Inspect Evidence & Transactions</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

