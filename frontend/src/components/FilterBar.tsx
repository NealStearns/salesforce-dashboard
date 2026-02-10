interface FilterBarProps {
  stage: string
  onStageChange: (stage: string) => void
  sortBy: string
  onSortChange: (sort: string) => void
  minAmount: string
  onMinAmountChange: (amount: string) => void
}

const STAGES = [
  'All Stages',
  'Prospecting',
  'Qualification',
  'Needs Analysis',
  'Value Proposition',
  'Id. Decision Makers',
  'Perception Analysis',
  'Proposal/Price Quote',
  'Negotiation/Review',
  'Closed Won',
  'Closed Lost',
]

export default function FilterBar({
  stage,
  onStageChange,
  sortBy,
  onSortChange,
  minAmount,
  onMinAmountChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap gap-4 items-end">
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">
          Stage
        </label>
        <select
          value={stage}
          onChange={(e) => onStageChange(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {STAGES.map((s) => (
            <option key={s} value={s === 'All Stages' ? '' : s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">
          Min Amount
        </label>
        <input
          type="number"
          value={minAmount}
          onChange={(e) => onMinAmountChange(e.target.value)}
          placeholder="e.g. 10000"
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-36 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">
          Sort By
        </label>
        <select
          value={sortBy}
          onChange={(e) => onSortChange(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="CloseDate">Close Date</option>
          <option value="Amount">Amount</option>
          <option value="Name">Name</option>
          <option value="StageName">Stage</option>
        </select>
      </div>
    </div>
  )
}
