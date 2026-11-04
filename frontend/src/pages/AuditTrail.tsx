import React, { useEffect, useState, useMemo } from 'react';
import { History, Shield, Filter, Search, User, Cpu, X, RotateCcw } from 'lucide-react';
import { api } from '../services/api';
import { AuditEventItem } from '../types';

export const AuditTrail: React.FC = () => {
  const [events, setEvents] = useState<AuditEventItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [eventType, setEventType] = useState('');
  const [search, setSearch] = useState('');

  const loadAudit = () => {
    setLoading(true);
    api.getAuditEvents({
      event_type: eventType || undefined,
      limit: 100,
    })
      .then((res) => {
        setEvents(res.items || []);
        setTotal(res.total || 0);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAudit();
  }, [eventType]);

  // Client-side search across multiple fields
  const filteredEvents = useMemo(() => {
    if (!search.trim()) return events;
    const q = search.toLowerCase().trim();
    return events.filter((e) => {
      const typeMatch = e.event_type?.toLowerCase().includes(q);
      const actorMatch = e.actor?.toLowerCase().includes(q);
      const statementMatch = e.statement_id?.toLowerCase().includes(q);
      const detailsMatch = e.details?.toLowerCase().includes(q);
      const txnMatch = e.transaction_id ? String(e.transaction_id).includes(q) : false;
      return typeMatch || actorMatch || statementMatch || detailsMatch || txnMatch;
    });
  }, [events, search]);

  const hasActiveFilters = Boolean(search || eventType);

  const handleClearFilters = () => {
    setSearch('');
    setEventType('');
  };

  return (
    <div className="space-y-6">
      {/* Header and Summary */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center pb-2 border-b border-slate-200/80 dark:border-navy-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-[#F4F1E9]">
            Audit Trail
          </h1>
          <p className="text-sm text-slate-500 dark:text-[#9BA8BA] mt-1">
            Immutable, chronological record of all document ingestion, machine classification, and human review events.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="rounded-lg bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm border border-slate-200/80 dark:border-navy-700 dark:bg-navy-900 dark:text-[#F4F1E9]">
            Showing <strong className="text-gold-600 dark:text-gold-400 font-mono">{filteredEvents.length}</strong> of {total} events
          </span>
        </div>
      </div>

      {/* Prominent Search & Event Type Filter Bar */}
      <div className="rounded-xl border border-slate-200/90 bg-white p-3.5 shadow-sm dark:border-navy-800 dark:bg-navy-900 flex flex-col sm:flex-row items-center gap-3">
        {/* Search Input */}
        <div className="relative flex-1 w-full">
          <Search className="pointer-events-none absolute left-3.5 top-2.5 h-4 w-4 text-slate-400 dark:text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search event type, statement ID, actor, or details..."
            aria-label="Search Audit Trail"
            className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-9 text-xs text-slate-900 placeholder:text-slate-400 focus:border-gold-500 focus:outline-none focus:ring-1 focus:ring-gold-500 dark:border-navy-700 dark:bg-navy-950/80 dark:text-[#F4F1E9] dark:placeholder:text-slate-500"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              title="Clear search"
              className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Filter by Event Type */}
        <div className="flex items-center space-x-2 w-full sm:w-auto shrink-0">
          <div className="flex items-center space-x-1.5">
            <Filter className="h-4 w-4 text-slate-400 dark:text-[#9BA8BA]" />
            <span className="text-xs font-semibold text-slate-600 dark:text-[#9BA8BA] hidden sm:inline">Event:</span>
          </div>
          <select
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
            aria-label="Filter by Event Type"
            className="w-full sm:w-auto rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-900 shadow-sm focus:border-gold-500 focus:outline-none focus:ring-1 focus:ring-gold-500 dark:border-navy-700 dark:bg-navy-900 dark:text-[#F4F1E9] cursor-pointer"
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

          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              title="Reset all filters"
              className="inline-flex items-center space-x-1 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 dark:border-navy-700 dark:bg-navy-800 dark:text-slate-300 dark:hover:bg-navy-700 cursor-pointer shrink-0"
            >
              <RotateCcw className="h-3 w-3" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Events Table */}
      <div className="rounded-xl border border-slate-200/90 bg-white shadow-sm dark:border-navy-800 dark:bg-navy-900 overflow-hidden">
        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gold-500 border-t-transparent" />
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500 dark:text-[#9BA8BA] space-y-2">
            <p className="text-sm font-semibold text-slate-800 dark:text-[#F4F1E9]">
              {hasActiveFilters ? 'No matching audit records found' : 'No audit records found'}
            </p>
            <p className="text-slate-400 dark:text-[#9BA8BA]">
              {hasActiveFilters
                ? 'Try adjusting your search terms or clearing the event type filter.'
                : 'Transactions and system events will appear here once processed.'}
            </p>
            {hasActiveFilters && (
              <button
                onClick={handleClearFilters}
                className="mt-2 inline-flex items-center space-x-1 rounded-lg bg-gold-400 px-3 py-1.5 text-xs font-bold text-navy-950 hover:bg-gold-500 transition-colors"
              >
                <span>Clear All Filters</span>
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[760px]">
              <thead className="bg-slate-50/80 text-slate-700 dark:bg-navy-800/80 dark:text-[#9BA8BA]">
                <tr>
                  <th className="px-4 py-3 font-semibold">Timestamp</th>
                  <th className="px-4 py-3 font-semibold">Actor</th>
                  <th className="px-4 py-3 font-semibold">Event Type</th>
                  <th className="px-4 py-3 font-semibold">Statement Reference</th>
                  <th className="px-4 py-3 font-semibold">Audit Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-navy-800">
                {filteredEvents.map((e) => (
                  <tr key={e.id} className="hover:bg-slate-50/60 dark:hover:bg-navy-800/40 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap font-mono text-slate-500 dark:text-[#9BA8BA]">
                      {e.created_at ? new Date(e.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="inline-flex items-center space-x-1 font-semibold text-slate-800 dark:text-[#F4F1E9]">
                        {e.actor === 'USER' ? (
                          <User className="h-3.5 w-3.5 text-gold-500" />
                        ) : (
                          <Cpu className="h-3.5 w-3.5 text-blue-500" />
                        )}
                        <span>{e.actor}</span>
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className={`rounded px-2.5 py-0.5 text-[10px] font-bold ${
                          e.event_type === 'APPROVAL' || e.event_type === 'CORRECTION'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/60 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800'
                            : e.event_type === 'RECONCILIATION'
                            ? 'bg-purple-50 text-purple-700 border border-purple-200/60 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800'
                            : e.event_type === 'EXTRACTION'
                            ? 'bg-blue-50 text-blue-700 border border-blue-200/60 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800'
                            : e.event_type === 'UPLOAD'
                            ? 'bg-amber-50 text-amber-700 border border-amber-200/60 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800'
                            : 'bg-slate-100 text-slate-700 dark:bg-navy-800 dark:text-slate-300'
                        }`}
                      >
                        {e.event_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-500 dark:text-[#9BA8BA] whitespace-nowrap">
                      {e.statement_id ? (
                        <span title={e.statement_id}>{e.statement_id.slice(0, 12)}...</span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-800 dark:text-[#F4F1E9] max-w-md">
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
