import { useState } from 'react'
import { opportunityApi } from '../services/api'
import { useApi } from '../hooks/useApi'
import FilterBar from './FilterBar'
import type { OpportunityListResponse } from '../types'

export default function OpportunityTable() {
  const [stage, setStage] = useState('')
  const [sortBy, setSortBy] = useState('CloseDate')
  const [minAmount, setMinAmount] = useState('')
  const [offset, setOffset] = useState(0)
  const limit = 25

  const { data, loading, error } = useApi<OpportunityListResponse>(
    () =>
      opportunityApi.list({
        limit,
        offset,
        stage: stage || undefined,
        sort_by: sortBy,
        min_amount: minAmount ? Number(minAmount) : undefined,
      }),
    [stage, sortBy, minAmount, offset],
  )

  const formatCurrency = (val: number | null) =>
    val != null
      ? new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
        }).format(val)
      : '—'

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Opportunities</h2>

      <FilterBar
        stage={stage}
        onStageChange={(s) => {
          setStage(s)
          setOffset(0)
        }}
        sortBy={sortBy}
        onSortChange={setSortBy}
        minAmount={minAmount}
        onMinAmountChange={(a) => {
          setMinAmount(a)
          setOffset(0)
        }}
      />

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {error && (
          <div className="p-4 bg-red-50 text-red-700 text-sm">{error}</div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Name
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Account
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Stage
                </th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">
                  Amount
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Close Date
                </th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">
                  Probability
                </th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">
                  Owner
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      {Array.from({ length: 7 }).map((_, j) => (
                        <td key={j} className="px-4 py-3">
                          <div className="h-4 bg-gray-200 rounded w-20" />
                        </td>
                      ))}
                    </tr>
                  ))
                : data?.records.map((opp) => (
                    <tr
                      key={opp.Id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-4 py-3 font-medium text-gray-800">
                        {opp.Name}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {opp.Account?.Name ?? '—'}
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
                          {opp.StageName}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-gray-800">
                        {formatCurrency(opp.Amount)}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {opp.CloseDate ?? '—'}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-600">
                        {opp.Probability != null
                          ? `${opp.Probability}%`
                          : '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {opp.Owner?.Name ?? '—'}
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
            <p className="text-sm text-gray-600">
              Showing {offset + 1}–{Math.min(offset + limit, data.total)} of{' '}
              {data.total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= data.total}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
