import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { MainLayout } from './components/Layout/MainLayout';

import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';
import { StatementHistory } from './pages/StatementHistory';
import { StatementDetails } from './pages/StatementDetails';
import { TransactionExplorer } from './pages/TransactionExplorer';
import { ReviewExceptions } from './pages/ReviewExceptions';
import { ReconciliationCentre } from './pages/ReconciliationCentre';
import { FinancialAnalytics } from './pages/FinancialAnalytics';
import { ClassificationInsights } from './pages/ClassificationInsights';
import { ExportCentre } from './pages/ExportCentre';
import { AuditTrail } from './pages/AuditTrail';
import { Settings } from './pages/Settings';

export function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/statements" element={<StatementHistory />} />
            <Route path="/statements/:id" element={<StatementDetails />} />
            <Route path="/transactions" element={<TransactionExplorer />} />
            <Route path="/reviews" element={<ReviewExceptions />} />
            <Route path="/reconciliation" element={<ReconciliationCentre />} />
            <Route path="/reconciliation/:id" element={<ReconciliationCentre />} />
            <Route path="/analytics" element={<FinancialAnalytics />} />
            <Route path="/classification" element={<ClassificationInsights />} />
            <Route path="/exports" element={<ExportCentre />} />
            <Route path="/audit" element={<AuditTrail />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
