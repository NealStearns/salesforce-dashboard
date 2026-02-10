import { authApi } from '../services/api'

export default function LoginPrompt() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
        <div className="text-5xl mb-4">📊</div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          Salesforce Dashboard
        </h1>
        <p className="text-gray-500 mb-6">
          Connect your Salesforce account to view opportunity analytics and
          pipeline insights.
        </p>
        <button
          onClick={() => authApi.login()}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-xl transition-colors"
        >
          Connect to Salesforce
        </button>
      </div>
    </div>
  )
}
