export interface Statement {
  id: string;
  filename: string;
  file_hash: string;
  bank_name?: string | null;
  layout_type: string;
  pdf_type: 'text' | 'scanned' | 'mixed';
  page_count: number;
  statement_period?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  opening_balance?: number | null;
  closing_balance?: number | null;
  total_debits?: number;
  total_credits?: number;
  expected_closing?: number | null;
  variance?: number | null;
  currency: string;
  reconciliation_status: 'RECONCILED' | 'MISMATCH' | 'INSUFFICIENT_DATA' | 'REVIEW_REQUIRED' | 'PENDING';
  status: 'UPLOADED' | 'PARSING' | 'PROCESSING' | 'PROCESSED' | 'FAILED';
  error_message?: string | null;
  transaction_count?: number;
  created_at?: string;
}

export interface Transaction {
  id: number;
  statement_id: string;
  date: string;
  description: string;
  raw_description: string;
  debit: number;
  credit: number;
  balance?: number | null;
  currency: string;
  category: string;
  classification_method: 'RULE_BASED' | 'MACHINE_LEARNING' | 'MANUAL' | 'NEEDS_REVIEW' | 'NONE';
  confidence_score?: number | null;
  classification_reason?: string | null;
  rule_id?: string | null;
  model_version?: string | null;
  review_status: 'APPROVED' | 'NEEDS_REVIEW' | 'CORRECTED';
  validation_status: 'VALID' | 'WARNING' | 'ANOMALY';
  validation_warnings?: string | null;
  is_duplicate: boolean;
  is_anomaly: boolean;
  source_page: number;
  row_sequence: number;
  extraction_method: string;
  bounding_box?: string | null;
}

export interface AccountInfo {
  holder_name?: string | null;
  account_number?: string | null;
  masked_number?: string | null;
  ifsc_code?: string | null;
  branch?: string | null;
  currency?: string;
}

export interface StatementDetailResponse {
  statement: Statement;
  account?: AccountInfo | null;
  transactions: Transaction[];
}

export interface SummaryMetrics {
  total_statements: number;
  total_transactions: number;
  total_debits: number;
  total_credits: number;
  net_movement: number;
  pending_reviews: number;
  anomalies_count: number;
  reconciled_statements: number;
}

export interface CategoryBreakdown {
  category: string;
  count: number;
  total_debit: number;
  total_credit: number;
  percentage_of_expense: number;
}

export interface CashflowPoint {
  date: string;
  debits: number;
  credits: number;
  net: number;
  count: number;
}

export interface MethodDistribution {
  method: string;
  count: number;
  percentage: number;
}

export interface ReconciliationResult {
  statement_id: string;
  bank_name?: string | null;
  period?: string | null;
  status: string;
  currency: string;
  opening_balance: number;
  total_credits: number;
  total_debits: number;
  expected_closing_balance: number;
  actual_closing_balance: number;
  variance: number;
  is_reconciled: boolean;
  running_balance_errors: number;
  duplicate_count: number;
  exceptions: string[];
}

export interface AuditEventItem {
  id: number;
  actor: string;
  event_type: string;
  statement_id?: string | null;
  transaction_id?: number | null;
  details?: string | null;
  created_at?: string | null;
}

