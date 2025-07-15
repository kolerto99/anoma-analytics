import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { DashboardSimple as Dashboard } from '@/components/DashboardSimple'
import { ResourcesPageSimple as ResourcesPage } from '@/components/ResourcesPageSimple'
import { TransactionsPage } from '@/components/TransactionsPage'
import { IntentsPage } from '@/components/IntentsPage'
import { BlocksPage } from '@/components/BlocksPage'
import { NetworkStatsPageSimple as NetworkStatsPage } from '@/components/NetworkStatsPageSimple'
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <Router>
      <div className="min-h-screen bg-background anoma-theme anoma-bg-pattern">
        <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
        
        <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-16'}`}>
          <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
          
          <main className="p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/resources" element={<ResourcesPage />} />
              <Route path="/transactions" element={<TransactionsPage />} />
              <Route path="/intents" element={<IntentsPage />} />
              <Route path="/blocks" element={<BlocksPage />} />
              <Route path="/network" element={<NetworkStatsPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App
