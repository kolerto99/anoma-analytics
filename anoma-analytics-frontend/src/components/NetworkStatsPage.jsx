import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Network, TrendingUp, Clock, Activity } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function NetworkStatsPage() {
  const [networkStats, setNetworkStats] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchNetworkStats()
  }, [])

  const fetchNetworkStats = async () => {
    try {
      const response = await fetch('/api/analytics/stats/network?hours=168') // 7 days
      const data = await response.json()
      setNetworkStats(data.stats || [])
    } catch (error) {
      console.error('Error fetching network stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const latest = networkStats[networkStats.length - 1] || {}

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Network Statistics</h1>
        <p className="text-gray-500 dark:text-gray-400">Network performance and health metrics</p>
      </div>

      {/* Current Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Current TPS</p>
                <p className="text-2xl font-bold">{latest.tps?.toFixed(1) || '0'}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Avg Processing Time</p>
                <p className="text-2xl font-bold">{latest.avg_processing_time_ms?.toFixed(0) || '0'}ms</p>
              </div>
              <Clock className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Active Resources</p>
                <p className="text-2xl font-bold">{latest.active_resources?.toLocaleString() || '0'}</p>
              </div>
              <Activity className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Pending Intents</p>
                <p className="text-2xl font-bold">{latest.pending_intents?.toLocaleString() || '0'}</p>
              </div>
              <Network className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* TPS Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Transactions Per Second (TPS)</CardTitle>
          <CardDescription>Network throughput over the last 7 days</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="h-80 bg-gray-200 animate-pulse rounded"></div>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={networkStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  formatter={(value) => [value.toFixed(2), 'TPS']}
                />
                <Line 
                  type="monotone" 
                  dataKey="tps" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Processing Time Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Average Processing Time</CardTitle>
          <CardDescription>Intent processing performance over time</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="h-80 bg-gray-200 animate-pulse rounded"></div>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={networkStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  formatter={(value) => [value.toFixed(0) + 'ms', 'Processing Time']}
                />
                <Line 
                  type="monotone" 
                  dataKey="avg_processing_time_ms" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

