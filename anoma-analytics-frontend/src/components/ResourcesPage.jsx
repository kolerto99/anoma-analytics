import React, { useState, useEffect } from 'react'
import { Search, Filter, Download, ExternalLink, Clock, User } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export function ResourcesPage() {
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    kind: '',
    owner: '',
    is_consumed: ''
  })
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  })

  useEffect(() => {
    fetchResources()
  }, [filters, pagination.page])

  const fetchResources = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.per_page.toString(),
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      })

      const response = await fetch(`/api/analytics/resources?${params}`)
      const data = await response.json()
      
      setResources(data.resources || [])
      setPagination(prev => ({ ...prev, ...data.pagination }))
    } catch (error) {
      console.error('Error fetching resources:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPagination(prev => ({ ...prev, page: 1 }))
  }

  const getResourceKindColor = (kind) => {
    const colors = {
      token: 'bg-blue-100 text-blue-800',
      nft: 'bg-purple-100 text-purple-800',
      intent: 'bg-yellow-100 text-yellow-800',
      custom: 'bg-gray-100 text-gray-800'
    }
    return colors[kind] || colors.custom
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  const truncateHash = (hash) => {
    return `${hash.slice(0, 8)}...${hash.slice(-8)}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Resources
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            Explore and analyze Anoma resources
          </p>
        </div>
        <Button variant="outline" className="flex items-center space-x-2">
          <Download className="w-4 h-4" />
          <span>Export</span>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filters</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Resource Kind</label>
              <Select value={filters.kind} onValueChange={(value) => handleFilterChange('kind', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="All kinds" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All kinds</SelectItem>
                  <SelectItem value="token">Token</SelectItem>
                  <SelectItem value="nft">NFT</SelectItem>
                  <SelectItem value="intent">Intent</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Owner</label>
              <Input
                placeholder="Enter owner address"
                value={filters.owner}
                onChange={(e) => handleFilterChange('owner', e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <Select value={filters.is_consumed} onValueChange={(value) => handleFilterChange('is_consumed', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All statuses</SelectItem>
                  <SelectItem value="false">Active</SelectItem>
                  <SelectItem value="true">Consumed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button 
                onClick={() => {
                  setFilters({ kind: '', owner: '', is_consumed: '' })
                  setPagination(prev => ({ ...prev, page: 1 }))
                }}
                variant="outline"
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resources Table */}
      <Card>
        <CardHeader>
          <CardTitle>Resources ({pagination.total.toLocaleString()})</CardTitle>
          <CardDescription>
            Showing {resources.length} of {pagination.total} resources
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {resources.map((resource) => (
                <div 
                  key={resource.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <Badge className={getResourceKindColor(resource.kind)}>
                          {resource.kind.toUpperCase()}
                        </Badge>
                        <span className="font-mono text-sm text-gray-600 dark:text-gray-400">
                          {truncateHash(resource.id)}
                        </span>
                        <Badge variant={resource.is_consumed ? "destructive" : "default"}>
                          {resource.is_consumed ? 'Consumed' : 'Active'}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="flex items-center space-x-2">
                          <User className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600 dark:text-gray-400">Owner:</span>
                          <span className="font-mono">{truncateHash(resource.owner)}</span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600 dark:text-gray-400">Created:</span>
                          <span>{formatTimestamp(resource.created_at)}</span>
                        </div>
                        
                        {resource.consumed_at && (
                          <div className="flex items-center space-x-2">
                            <Clock className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-600 dark:text-gray-400">Consumed:</span>
                            <span>{formatTimestamp(resource.consumed_at)}</span>
                          </div>
                        )}
                      </div>

                      {resource.value && (
                        <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-800 rounded text-sm">
                          <span className="text-gray-600 dark:text-gray-400">Value: </span>
                          <code className="text-xs">{resource.value}</code>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-gray-500">
                Page {pagination.page} of {pagination.pages}
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={pagination.page === 1}
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={pagination.page === pagination.pages}
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

