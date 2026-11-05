import {
  Statement,
  StatementDetailResponse,
  Transaction,
  SummaryMetrics,
  CategoryBreakdown,
  CashflowPoint,
  MethodDistribution,
  ReconciliationResult,
  AuditEventItem,
  RunningBalanceResponse,
  ActivityHeatmapPoint,
  MerchantConcentrationResponse,
  PaymentChannelItem,
  ClassificationDeepResponse,
  ExtractionCompletenessResponse,
  MultiStatementResponse,
  CategoryTrendPoint,
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    let errorMsg = `API Error ${res.status}: ${res.statusText}`;
    try {
      const errData = await res.json();
      if (errData.detail) errorMsg = errData.detail;
      else if (errData.error) errorMsg = errData.error;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  // Health
  getHealth: () => fetchJson<{ status: string; ocr_status: any }>(`${API_BASE}/health`),

  // Statements
  getStatements: () => fetchJson<Statement[]>(`${API_BASE}/statements`),
  getStatement: (id: string) => fetchJson<StatementDetailResponse>(`${API_BASE}/statements/${id}`),
  uploadStatement: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetchJson<Statement>(`${API_BASE}/statements/upload`, {
      method: 'POST',
      body: formData,
    });
  },
  deleteStatement: (id: string) =>
    fetchJson<{ message: string; statement_id: string }>(`${API_BASE}/statements/${id}`, {
      method: 'DELETE',
    }),
  getPagePreviewUrl: (id: string, pageNumber: number) =>
    `${API_BASE}/statements/${id}/pages/${pageNumber}/preview`,

  // Transactions
  getTransactions: (params?: {
    statement_id?: string;
    category?: string;
    search?: string;
    method?: string;
    review_status?: string;
    limit?: number;
    offset?: number;
  }) => {
    const q = new URLSearchParams();
    if (params?.statement_id) q.set('statement_id', params.statement_id);
    if (params?.category) q.set('category', params.category);
    if (params?.search) q.set('search', params.search);
    if (params?.method) q.set('method', params.method);
    if (params?.review_status) q.set('review_status', params.review_status);
    if (params?.limit) q.set('limit', String(params.limit));
    if (params?.offset) q.set('offset', String(params.offset));
    return fetchJson<{ total: number; items: Transaction[] }>(`${API_BASE}/transactions?${q.toString()}`);
  },

  // Reconciliation
  getReconciliation: (statementId: string) =>
    fetchJson<ReconciliationResult>(`${API_BASE}/reconciliation/${statementId}`),
  runReconciliation: (statementId: string) =>
    fetchJson<ReconciliationResult>(`${API_BASE}/reconciliation/${statementId}/run`, {
      method: 'POST',
    }),

  // Reviews
  getReviewQueue: (statementId?: string) => {
    const q = statementId ? `?statement_id=${statementId}` : '';
    return fetchJson<{ total: number; items: Transaction[] }>(`${API_BASE}/reviews${q}`);
  },
  approveTransaction: (id: number, reason?: string) =>
    fetchJson<{ status: string; transaction_id: number; category: string; review_status?: string; message?: string }>(
      `${API_BASE}/reviews/${id}/approve`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      }
    ),
  correctTransaction: (
    id: number,
    data: { new_category?: string; new_description?: string; new_debit?: number; new_credit?: number; reason?: string }
  ) =>
    fetchJson<{ status: string; transaction_id: number; category: string; description?: string; review_status?: string; message?: string }>(
      `${API_BASE}/reviews/${id}/correct`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }
    ),

  // Classification
  getClassificationMetrics: () =>
    fetchJson<{ status: string; metadata: any; metrics: any }>(`${API_BASE}/classification/metrics`),
  getClassificationRules: () =>
    fetchJson<{ count: number; rules: any[] }>(`${API_BASE}/classification/rules`),
  reclassify: (payload: { transaction_id?: number; description?: string }) =>
    fetchJson<any>(`${API_BASE}/classification/reclassify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  retrainModel: () =>
    fetchJson<any>(`${API_BASE}/classification/retrain`, {
      method: 'POST',
    }),

  // Analytics
  getAnalyticsSummary: () => fetchJson<SummaryMetrics>(`${API_BASE}/analytics/summary`),
  getCategoryAnalytics: (statementId?: string) => {
    const q = statementId ? `?statement_id=${statementId}` : '';
    return fetchJson<CategoryBreakdown[]>(`${API_BASE}/analytics/categories${q}`);
  },
  getCashflow: (statementId?: string) => {
    const q = statementId ? `?statement_id=${statementId}` : '';
    return fetchJson<CashflowPoint[]>(`${API_BASE}/analytics/cashflow${q}`);
  },
  getDistribution: () => fetchJson<MethodDistribution[]>(`${API_BASE}/analytics/distribution`),
  getRunningBalance: (statementId?: string) => {
    const q = statementId ? `?statement_id=${statementId}` : '';
    return fetchJson<RunningBalanceResponse>(`${API_BASE}/analytics/running-balance${q}`);
  },
  getActivityHeatmap: (statementId?: string) => {
    const q = statementId ? `?statement_id=${statementId}` : '';
    return fetchJson<ActivityHeatmapPoint[]>(`${API_BASE}/analytics/activity-heatmap${q}`);
  },
  getMerchantConcentration: (statementId?: string, limit: number = 10) => {
    const params = new URLSearchParams();
    if (statementId) params.set('statement_id', statementId);
    if (limit) params.set('limit', String(limit));
    const qs = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<MerchantConcentrationResponse>(`${API_BASE}/analytics/merchants${qs}`);
  },
  getPaymentChannels: (statementId?: string) => {
    const q = statementId ? `?statement_id=${statementId}` : '';
    return fetchJson<PaymentChannelItem[]>(`${API_BASE}/analytics/channels${q}`);
  },
  getClassificationDeep: () => fetchJson<ClassificationDeepResponse>(`${API_BASE}/analytics/classification-deep`),
  getExtractionCompleteness: (statementId?: string) => {
    const q = statementId ? `?statement_id=${statementId}` : '';
    return fetchJson<ExtractionCompletenessResponse>(`${API_BASE}/analytics/completeness${q}`);
  },
  getMultiStatementComparison: () => fetchJson<MultiStatementResponse>(`${API_BASE}/analytics/multi-statement`),
  getCategoryTrends: (statementId?: string) => {
    const q = statementId ? `?statement_id=${statementId}` : '';
    return fetchJson<CategoryTrendPoint[]>(`${API_BASE}/analytics/category-trends${q}`);
  },

  // Audit
  getAuditEvents: (params?: { event_type?: string; statement_id?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.event_type) q.set('event_type', params.event_type);
    if (params?.statement_id) q.set('statement_id', params.statement_id);
    if (params?.limit) q.set('limit', String(params.limit || 100));
    return fetchJson<{ total: number; items: AuditEventItem[] }>(`${API_BASE}/audit?${q.toString()}`);
  },

  // Exports URLs
  getExcelExportUrl: (statementId: string) => `${API_BASE}/exports/${statementId}/excel`,
  getCsvExportUrl: (statementId: string) => `${API_BASE}/exports/${statementId}/csv`,
};

