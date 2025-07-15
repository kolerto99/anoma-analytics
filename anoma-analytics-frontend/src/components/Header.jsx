import { useState, useEffect } from 'react'
import { Menu, Search, Bell, Settings, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export function Header({ sidebarOpen, setSidebarOpen }) {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const handleRefresh = () => {
    setIsRefreshing(true)
    // Simulate refresh
    setTimeout(() => {
      setIsRefreshing(false)
      window.location.reload()
    }, 1000)
  }

  return (
    <header className="bg-card border-b border-border px-6 py-4 header-anoma">
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </Button>

          <div className="hidden lg:block">
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold text-foreground">
                Anoma Analytics
              </h1>
              <div className="anoma-diamond-accent"></div>
            </div>
            <p className="text-sm text-muted-foreground">
              Real-time blockchain analytics and insights
            </p>
          </div>
        </div>

        {/* Center - Search */}
        <div className="flex-1 max-w-md mx-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search transactions, addresses, blocks..."
              className="pl-10 pr-4 py-2 w-full border-border focus:ring-primary"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Current time */}
          <div className="hidden md:block text-sm text-muted-foreground">
            <div className="text-right">
              <div className="font-medium text-foreground">
                {currentTime.toLocaleTimeString()}
              </div>
              <div className="text-xs">
                {currentTime.toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Refresh button */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center space-x-2 border-border hover:bg-muted"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative hover:bg-muted">
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full text-xs text-primary-foreground flex items-center justify-center">
              3
            </span>
          </Button>

          {/* Settings */}
          <Button variant="ghost" size="sm" className="hover:bg-muted">
            <Settings className="w-5 h-5" />
          </Button>

          {/* Network status indicator */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-accent rounded-full anoma-pulse"></div>
            <span className="text-sm text-muted-foreground hidden sm:inline">
              Live
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

