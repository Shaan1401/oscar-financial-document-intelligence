import React, { useEffect, useState } from 'react';
import { History, Shield, Filter, Search, User, Cpu } from 'lucide-react';
import { api } from '../services/api';
import { AuditEventItem } from '../types';

export const AuditTrail: React.FC = () => {
  const [events, setEvents] = useState<AuditEventItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [eventType, setEventType] = useState('');

  const loadAudit = () => {
    setLoading(true);
    api.getAuditEvents({
      event_type: eventType || undefined,
      limit: 100,
    })
      .then((res) => {
        setEvents(res.items);
        setTotal(res.total);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAudit();
  }, [eventType]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Audit Trail
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Immutable, chronological record of all document ingestion, machine classification, and human review events.
          </p>
        </div>

        {/* Filter by Event Type */}
        <select
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-900 shadow-sm focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        >
          <option value="">All Event Types</option>
          <option value="UPLOAD">UPLOAD</option>
          <option value="EXTRACTION">EXTRACTION</option>
          <option value="CLASSIFICATION">CLASSIFICATION</option>
          <option value="RECONCILIATION">RECONCILIATION</option>
          <option value="APPROVAL">APPROVAL</option>
          <option value="CORRECTION">CORRECTION</option>
          <option value="DELETION">DELETION</option>
        </select>
      </div>

      {/* Events Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-7 w-7 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
          </div>
        ) : events.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 dark:text-slate-400">
            No audit records found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[720px]">
              <thead className="bg-slate-50 text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-semibold">Timestamp</th>
                  <th className="px-4 py-3 font-semibold">Actor</th>
                  <th className="px-4 py-3 font-semibold">Event Type</th>
                  <th className="px-4 py-3 font-semibold">Statement Reference</th>
                  <th className="px-4 py-3 font-semibold">Audit Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {events.map((e) => (
                  <tr key={e.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                    <td className="px-4 py-3 whitespace-nowrap font-mono text-slate-500">
                      {e.created_at ? new Date(e.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="inline-flex items-center space-x-1 font-medium text-slate-700 dark:text-slate-300">
                        {e.actor === 'USER' ? (
                          <User className="h-3.5 w-3.5 text-brand-600" />
                        ) : (
                          <Cpu className="h-3.5 w-3.5 text-purple-600" />
                        )}
                        <span>{e.actor}</span>
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className={`rounded px-2 py-0.5 text-[10px] font-semibold ${
                          e.event_type === 'APPROVAL' || e.event_type === 'CORRECTION'
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                            : e.event_type === 'RECONCILIATION'
                            ? 'bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300'
                            : e.event_type === 'EXTRACTION'
                            ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                            : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                        }`}
                      >
                        {e.event_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      {e.statement_id ? e.statement_id.slice(0, 12) + '...' : '-'}
                    </td>
                    <td className="px-4 py-3 text-slate-800 dark:text-slate-200 max-w-md">
                      {e.details}
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

