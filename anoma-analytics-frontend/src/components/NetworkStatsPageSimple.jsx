import React, { useState, useEffect } from 'react'
import { api } from '../utils/api'

export function NetworkStatsPageSimple() {
  const [networkStats, setNetworkStats] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchNetworkStats()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchNetworkStats()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const fetchNetworkStats = async () => {
    try {
      const data = await api.get('/api/analytics/stats/network?hours=168') // 7 days
      setNetworkStats(data.stats || [])
    } catch (error) {
      console.error('Error fetching network stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const latest = networkStats[networkStats.length - 1] || {}

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Network Statistics</h1>
        <p className="text-gray-500 dark:text-gray-400">Network performance and health metrics</p>
      </div>

      {/* Current Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Current TPS</p>
              <p className="text-2xl font-bold">{latest.tps?.toFixed(1) || '0'}</p>
            </div>
            <span className="text-2xl">📈</span>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Avg Processing Time</p>
              <p className="text-2xl font-bold">{latest.avg_processing_time_ms?.toFixed(0) || '0'}ms</p>
            </div>
            <span className="text-2xl">🕒</span>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Active Resources</p>
              <p className="text-2xl font-bold">{latest.active_resources?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">⚡</span>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Pending Intents</p>
              <p className="text-2xl font-bold">{latest.pending_intents?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">🔗</span>
          </div>
        </div>
      </div>

      {/* Network Stats Table */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold">Network Performance History</h3>
          <p className="text-gray-500">Last 7 days of network statistics</p>
        </div>
        <div className="p-6">
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-12 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4">Timestamp</th>
                    <th className="text-left py-3 px-4">TPS</th>
                    <th className="text-left py-3 px-4">Processing Time (ms)</th>
                    <th className="text-left py-3 px-4">Active Resources</th>
                    <th className="text-left py-3 px-4">Pending Intents</th>
                  </tr>
                </thead>
                <tbody>
                  {networkStats.slice(-10).map((stat, index) => (
                    <tr key={index} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="py-3 px-4">
                        {new Date(stat.timestamp).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 font-mono">
                        {stat.tps?.toFixed(2) || '0.00'}
                      </td>
                      <td className="py-3 px-4 font-mono">
                        {stat.avg_processing_time_ms?.toFixed(0) || '0'}
                      </td>
                      <td className="py-3 px-4 font-mono">
                        {stat.active_resources?.toLocaleString() || '0'}
                      </td>
                      <td className="py-3 px-4 font-mono">
                        {stat.pending_intents?.toLocaleString() || '0'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {networkStats.length === 0 && !loading && (
                <div className="text-center py-8 text-gray-500">
                  No network statistics available
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-2">Performance Metrics</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• Average TPS: {networkStats.length > 0 ? (networkStats.reduce((sum, stat) => sum + (stat.tps || 0), 0) / networkStats.length).toFixed(2) : '0.00'}</li>
              <li>• Peak TPS: {networkStats.length > 0 ? Math.max(...networkStats.map(stat => stat.tps || 0)).toFixed(2) : '0.00'}</li>
              <li>• Average Processing Time: {networkStats.length > 0 ? (networkStats.reduce((sum, stat) => sum + (stat.avg_processing_time_ms || 0), 0) / networkStats.length).toFixed(0) : '0'}ms</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Resource Statistics</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• Current Active Resources: {latest.active_resources?.toLocaleString() || '0'}</li>
              <li>• Current Pending Intents: {latest.pending_intents?.toLocaleString() || '0'}</li>
              <li>• Data Points: {networkStats.length}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

