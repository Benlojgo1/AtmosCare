import { useState } from 'react'
import { API_BASE } from './lib/api'
import LocationsPanel from './panels/LocationsPanel'
import WeatherPanel from './panels/WeatherPanel'
import HighRiskQuery from './queries/HighRiskQuery'
import HeatOutliersQuery from './queries/HeatOutliersQuery'
import AlertsByRiskQuery from './queries/AlertsByRiskQuery'
import AllocationQuery from './queries/AllocationQuery'
import CompareZipsQuery from './queries/CompareZipsQuery'
import { Tabs, TabPanel } from './components/Tabs'

export default function App(){
  const [tab, setTab] = useState('high-risk')
  return (
    <div className="mx-auto max-w-7xl space-y-6 p-4">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">☁️ AtmosCare</h1>
          <p className="text-sm text-muted-foreground">Infrastructure Resiliency Tracker — UI</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>API:</span>
          <code className="rounded-md bg-muted px-2 py-1">{API_BASE}</code>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <LocationsPanel />
        <WeatherPanel />
      </div>

      <div className="mt-6">
        <Tabs
          tabs={[
            { id:'high-risk', label:'High-Risk Exposure' },
            { id:'heat-outliers', label:'Heat Outliers' },
            { id:'risk-alerts', label:'Alerts by Risk' },
            { id:'allocation', label:'Resource Allocation' },
            { id:'compare', label:'Compare ZIPs' },
          ]}
          value={tab}
          onChange={setTab}
        />
        <TabPanel active={tab==='high-risk'}><HighRiskQuery /></TabPanel>
        <TabPanel active={tab==='heat-outliers'}><HeatOutliersQuery /></TabPanel>
        <TabPanel active={tab==='risk-alerts'}><AlertsByRiskQuery /></TabPanel>
        <TabPanel active={tab==='allocation'}><AllocationQuery /></TabPanel>
        <TabPanel active={tab==='compare'}><CompareZipsQuery /></TabPanel>
      </div>

      <footer className="pt-8 text-center text-xs text-muted-foreground">
        Built with React, Tailwind, lucide-react, and Recharts.
      </footer>
    </div>
  )
}
