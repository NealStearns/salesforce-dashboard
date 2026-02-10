import { Link, useLocation } from 'react-router-dom'
import { authApi } from '../services/api'

const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/opportunities', label: 'Opportunities', icon: '💰' },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-blue-600">SF Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Salesforce Analytics</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              location.pathname === item.path
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span>{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-200">
        <button
          onClick={() => authApi.logout()}
          className="w-full px-4 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          Sign Out
        </button>
      </div>
    </aside>
  )
}
