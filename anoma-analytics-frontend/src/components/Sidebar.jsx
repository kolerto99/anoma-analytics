import { Link, useLocation } from 'react-router-dom'
import { 
  BarChart3, 
  Database, 
  Activity, 
  Zap, 
  Blocks, 
  Network,
  Menu,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const navigation = [
  { name: 'Dashboard', href: '/', icon: BarChart3 },
  { name: 'Resources', href: '/resources', icon: Database },
  { name: 'Transactions', href: '/transactions', icon: Activity },
  { name: 'Intents', href: '/intents', icon: Zap },
  { name: 'Blocks', href: '/blocks', icon: Blocks },
  { name: 'Network Stats', href: '/network', icon: Network },
]

export function Sidebar({ open, setOpen }) {
  const location = useLocation()

  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 flex flex-col
        ${open ? 'w-64' : 'w-16'} 
        bg-card border-r border-sidebar-border sidebar-anoma
        transition-all duration-300 ease-in-out
        ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-sidebar-border">
          {open && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 anoma-gradient rounded-lg flex items-center justify-center relative">
                <div className="anoma-diamond absolute"></div>
                <BarChart3 className="w-4 h-4 text-white relative z-10" />
              </div>
              <span className="text-xl font-bold text-foreground">
                Anoma Analytics
              </span>
            </div>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setOpen(!open)}
            className="lg:hidden"
          >
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-all duration-200 anoma-hover-lift
                  ${isActive 
                    ? 'anoma-gradient text-white nav-active' 
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }
                `}
              >
                <Icon className={`
                  ${open ? 'mr-3' : 'mx-auto'} 
                  w-5 h-5 flex-shrink-0
                  ${isActive ? 'text-white' : 'text-muted-foreground group-hover:text-primary'}
                `} />
                {open && (
                  <span className="truncate">{item.name}</span>
                )}
                {isActive && !open && (
                  <div className="absolute left-0 w-1 h-8 anoma-gradient rounded-r-full"></div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        {open && (
          <div className="p-4 border-t border-sidebar-border">
            <div className="flex items-center space-x-2 mb-2">
              <div className="anoma-diamond-accent"></div>
              <div className="text-xs text-muted-foreground">
                <p className="font-semibold text-foreground">Anoma Analytics v1.0</p>
                <p>Real-time blockchain analytics</p>
              </div>
            </div>
            <div className="flex items-center space-x-1 text-xs text-muted-foreground">
              <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
              <span>Connected to Anoma Network</span>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

