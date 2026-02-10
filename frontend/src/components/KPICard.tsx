interface KPICardProps {
  title: string
  value: number
  count?: number
  format?: 'currency' | 'number' | 'percent'
  loading?: boolean
  color?: 'blue' | 'green' | 'red' | 'purple'
}

const colorMap = {
  blue: 'bg-blue-50 text-blue-700 border-blue-200',
  green: 'bg-green-50 text-green-700 border-green-200',
  red: 'bg-red-50 text-red-700 border-red-200',
  purple: 'bg-purple-50 text-purple-700 border-purple-200',
}

function formatValue(value: number, format: string): string {
  if (format === 'currency') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }
  if (format === 'percent') return `${value.toFixed(1)}%`
  return new Intl.NumberFormat('en-US').format(value)
}

export default function KPICard({
  title,
  value,
  count,
  format = 'number',
  loading = false,
  color = 'blue',
}: KPICardProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-24 mb-3" />
        <div className="h-8 bg-gray-200 rounded w-32" />
      </div>
    )
  }

  return (
    <div className={`rounded-xl shadow-sm border p-6 ${colorMap[color]}`}>
      <p className="text-sm font-medium opacity-80">{title}</p>
      <p className="text-2xl font-bold mt-1">{formatValue(value, format)}</p>
      {count !== undefined && (
        <p className="text-sm opacity-70 mt-1">{count} opportunities</p>
      )}
    </div>
  )
}
