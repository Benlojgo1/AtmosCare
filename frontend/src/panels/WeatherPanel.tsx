import { useState } from 'react'
import { http } from '../lib/api'
import type { WeatherRecord } from '../lib/types'
import Busy from '../components/Busy'
import ErrorBanner from '../components/ErrorBanner'
import SectionTitle from '../components/SectionTitle'
import { RefreshCw, Search } from 'lucide-react'

export default function WeatherPanel(){
  const [zip, setZip] = useState('')
  const [rows, setRows] = useState<WeatherRecord[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string|null>(null)

  async function load(){
    setBusy(true); setError(null)
    try{
      const data = await http<WeatherRecord[]>(`/api/weather?zip=${encodeURIComponent(zip)}`)
      setRows(data)
    }catch(e:any){ setError(e.message || String(e)) }finally{ setBusy(false) }
  }
  async function ingest(){
    setBusy(true); setError(null)
    try{
      await http(`/api/weather`, { method:'POST', body: JSON.stringify({ zip }) })
      await load()
    }catch(e:any){ setError(e.message || String(e)) }finally{ setBusy(false) }
  }

  return (
    <div className="relative w-full rounded-2xl border p-4">
      <Busy show={busy} />
      <SectionTitle icon={RefreshCw} title="Weather Records" hint="Pull live data & view history by ZIP" />

      <div className="mt-3 flex flex-col gap-2 md:flex-row">
        <input className="rounded-xl border px-3 py-2" placeholder="ZipCode e.g., 78224" value={zip} onChange={e=>setZip(e.target.value)} />
        <div className="flex gap-2">
          <button onClick={load} className="flex items-center gap-2 rounded-xl border px-3 py-2">
            <Search className="h-4 w-4" /> View
          </button>
          <button onClick={ingest} className="flex items-center gap-2 rounded-xl bg-black px-3 py-2 text-white">
            <RefreshCw className="h-4 w-4" /> Ingest Now
          </button>
        </div>
      </div>

      <ErrorBanner message={error} />

      <div className="mt-3 overflow-auto rounded-2xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted/30">
            <tr>
              <th className="px-3 py-2 text-left">RecordID</th>
              <th className="px-3 py-2 text-left">Time</th>
              <th className="px-3 py-2 text-left">Temp (°F)</th>
              <th className="px-3 py-2 text-left">Humidity (%)</th>
              <th className="px-3 py-2 text-left">AQI</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.RecordID} className="border-t">
                <td className="px-3 py-2">{r.RecordID}</td>
                <td className="px-3 py-2">{new Date(r.TimeStamp).toLocaleString()}</td>
                <td className="px-3 py-2">{r.Temperature}</td>
                <td className="px-3 py-2">{r.Humidity}</td>
                <td className="px-3 py-2">{r.AirQualityIndex}</td>
              </tr>
            ))}
            {rows.length===0 && (
              <tr><td colSpan={5} className="px-3 py-4 text-center text-muted-foreground">No data yet — enter a ZIP and click Ingest/View.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
