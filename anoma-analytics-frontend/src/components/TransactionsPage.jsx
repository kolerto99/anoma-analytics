import { useState, useEffect } from 'react'
import { Activity, Clock, Hash, Zap, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export function TransactionsPage() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTransactions()
  }, [])

  const fetchTransactions = async () => {
    try {
      const response = await fetch('/api/analytics/transactions?per_page=50')
      const data = await response.json()
      setTransactions(data.transactions || [])
    } catch (error) {
      console.error('Error fetching transactions:', error)
    } finally {
      setLoading(false)
    }
  }

  const getTypeColor = (type) => {
    return type === 'balanced' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
  }

  const getStatusIcon = (status) => {
    return status === 'success' ? 
      <CheckCircle className="w-4 h-4 text-green-500" /> : 
      <XCircle className="w-4 h-4 text-red-500" />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Transactions</h1>
        <p className="text-gray-500 dark:text-gray-400">Recent transaction activity</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
          <CardDescription>Latest transactions on the Anoma network</CardDescription>
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
              {transactions.map((tx) => (
                <div key={tx.id} className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(tx.status)}
                      <div>
                        <div className="flex items-center space-x-2">
                          <Hash className="w-4 h-4 text-gray-400" />
                          <span className="font-mono text-sm">{tx.id.slice(0, 16)}...</span>
                          <Badge className={getTypeColor(tx.type)}>
                            {tx.type}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                          <span>Block #{tx.block_height}</span>
                          <span>{new Date(tx.timestamp).toLocaleString()}</span>
                          <span>{tx.size_bytes} bytes</span>
                          <span>{tx.gas_used} gas</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Resources</div>
                      <div className="text-lg font-semibold">
                        +{tx.created_resources_count} -{tx.consumed_resources_count}
                      </div>
                    </div>
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

