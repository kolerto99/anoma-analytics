import React, { useState, useEffect } from 'react'
import { api } from '../utils/api'

export function ResourcesPageSimple() {
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

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchResources()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [filters, pagination.page])

  const fetchResources = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.per_page.toString(),
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      })

      const response = await api.get(`/api/analytics/resources?${params}`)
      
      setResources(response.resources || [])
      setPagination(prev => ({ ...prev, ...response.pagination }))
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
    <div className="space-y-6 p-6">
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
        <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 flex items-center space-x-2">
          <span>📥</span>
          <span>Export</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <span>🔍</span>
          <span>Filters</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Resource Kind</label>
            <select 
              value={filters.kind} 
              onChange={(e) => handleFilterChange('kind', e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="">All kinds</option>
              <option value="token">Token</option>
              <option value="nft">NFT</option>
              <option value="intent">Intent</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Owner</label>
            <input
              type="text"
              placeholder="Enter owner address"
              value={filters.owner}
              onChange={(e) => handleFilterChange('owner', e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Status</label>
            <select 
              value={filters.is_consumed} 
              onChange={(e) => handleFilterChange('is_consumed', e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="">All statuses</option>
              <option value="false">Active</option>
              <option value="true">Consumed</option>
            </select>
          </div>

          <div className="flex items-end">
            <button 
              onClick={() => {
                setFilters({ kind: '', owner: '', is_consumed: '' })
                setPagination(prev => ({ ...prev, page: 1 }))
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Resources Table */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold">Resources ({pagination.total.toLocaleString()})</h3>
          <p className="text-gray-500">
            Showing {resources.length} of {pagination.total} resources
          </p>
        </div>
        <div className="p-6">
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
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getResourceKindColor(resource.kind)}`}>
                          {resource.kind.toUpperCase()}
                        </span>
                        <span className="font-mono text-sm text-gray-600 dark:text-gray-400">
                          {truncateHash(resource.id)}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          resource.is_consumed 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {resource.is_consumed ? 'Consumed' : 'Active'}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="flex items-center space-x-2">
                          <span>👤</span>
                          <span className="text-gray-600 dark:text-gray-400">Owner:</span>
                          <span className="font-mono">{truncateHash(resource.owner)}</span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <span>🕒</span>
                          <span className="text-gray-600 dark:text-gray-400">Created:</span>
                          <span>{formatTimestamp(resource.created_at)}</span>
                        </div>
                        
                        {resource.consumed_at && (
                          <div className="flex items-center space-x-2">
                            <span>🕒</span>
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
                      <button className="p-2 hover:bg-gray-100 rounded">
                        <span>🔗</span>
                      </button>
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
                <button
                  disabled={pagination.page === 1}
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                  className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>
                <button
                  disabled={pagination.page === pagination.pages}
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                  className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

