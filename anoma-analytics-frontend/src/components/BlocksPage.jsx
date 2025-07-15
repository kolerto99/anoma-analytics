import { useState, useEffect } from 'react'
import { Blocks, Clock, Hash, Activity } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function BlocksPage() {
  const [blocks, setBlocks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchBlocks()
  }, [])

  const fetchBlocks = async () => {
    try {
      const response = await fetch('/api/analytics/blocks?per_page=50')
      const data = await response.json()
      setBlocks(data.blocks || [])
    } catch (error) {
      console.error('Error fetching blocks:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Blocks</h1>
        <p className="text-gray-500 dark:text-gray-400">Recent blocks and network activity</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Blocks</CardTitle>
          <CardDescription>Latest blocks produced on the Anoma network</CardDescription>
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
              {blocks.map((block) => (
                <div key={block.height} className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Blocks className="w-5 h-5 text-purple-500" />
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-lg font-semibold">#{block.height}</span>
                          <div className="flex items-center space-x-1 text-sm text-gray-500">
                            <Hash className="w-3 h-3" />
                            <span className="font-mono">{block.hash.slice(0, 16)}...</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                          <div className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{new Date(block.timestamp).toLocaleString()}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Activity className="w-3 h-3" />
                            <span>{block.transaction_count} transactions</span>
                          </div>
                          <span>{(block.size_bytes / 1024).toFixed(1)} KB</span>
                          {block.proposer && (
                            <span>Proposer: {block.proposer.slice(0, 8)}...</span>
                          )}
                        </div>
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

