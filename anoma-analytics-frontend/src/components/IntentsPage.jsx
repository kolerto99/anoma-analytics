import { useState, useEffect } from 'react'
import { Zap, Clock, User, Settings } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export function IntentsPage() {
  const [intents, setIntents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchIntents()
  }, [])

  const fetchIntents = async () => {
    try {
      const response = await fetch('/api/analytics/intents?per_page=50')
      const data = await response.json()
      setIntents(data.intents || [])
    } catch (error) {
      console.error('Error fetching intents:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      solved: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    }
    return colors[status] || colors.pending
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Intents</h1>
        <p className="text-gray-500 dark:text-gray-400">Intent processing and solver activity</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Intents</CardTitle>
          <CardDescription>Latest intent submissions and processing status</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(10)].map((_, i) => (
                <div key={i} className="animate-pulse h-20 bg-gray-200 rounded"></div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {intents.map((intent) => (
                <div key={intent.id} className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Zap className="w-5 h-5 text-yellow-500" />
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-sm">{intent.id.slice(0, 16)}...</span>
                          <Badge className={getStatusColor(intent.status)}>
                            {intent.status}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                          <div className="flex items-center space-x-1">
                            <User className="w-3 h-3" />
                            <span>{intent.creator.slice(0, 8)}...</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{new Date(intent.created_at).toLocaleString()}</span>
                          </div>
                          {intent.solver && (
                            <div className="flex items-center space-x-1">
                              <Settings className="w-3 h-3" />
                              <span>Solver: {intent.solver.slice(0, 8)}...</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    {intent.processing_time_ms && (
                      <div className="text-right">
                        <div className="text-sm text-gray-500">Processing Time</div>
                        <div className="text-lg font-semibold">{intent.processing_time_ms}ms</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

