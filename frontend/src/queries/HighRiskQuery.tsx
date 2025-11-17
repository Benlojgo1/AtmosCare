import { useState } from 'react'
import { http } from '../lib/api'
import ErrorBanner from '../components/ErrorBanner'
import Busy from '../components/Busy'
import SectionTitle from '../components/SectionTitle'
import { Search } from 'lucide-react'

export default function HighRiskQuery(){
  const [aqi, setAqi] = useState<number>(100)
  const [rows, setRows] = useState<any[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string|null>(null)

  async function run(){
    setBusy(true); setErr(null)
    try{
      const data = await http<any[]>(`/api/queries/high-risk?aqi=${aqi}`)
      setRows(data)
    }catch(e:any){ setErr(e.message || String(e)) }finally{ setBusy(false) }
  }

  return (
    <div className="relative rounded-2xl border p-4">
      <Busy show={busy} />
      <SectionTitle icon={Search} title="High-Risk Population Exposure" hint="AQI > threshold & high vulnerability" />
      <div className="mt-3 flex flex-col gap-2 md:flex-row md:items-center">
        <input type="number" className="rounded-xl border px-3 py-2" value={aqi} onChange={e=>setAqi(Number(e.target.value))} />
        <button onClick={run} className="rounded-xl bg-black px-3 py-2 text-white">Run</button>
      </div>
      <ErrorBanner message={err} />
      <div className="mt-3 overflow-auto rounded-2xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted/30">
            <tr>
              <th className="px-3 py-2 text-left">ZipCode</th>
              <th className="px-3 py-2 text-left">Location</th>
              <th className="px-3 py-2 text-left">VulnerabilityIndex</th>
              <th className="px-3 py-2 text-left">Latest AQI</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i)=>(
              <tr key={i} className="border-t">
                <td className="px-3 py-2">{r.ZipCode}</td>
                <td className="px-3 py-2">{r.LocationName}</td>
                <td className="px-3 py-2">{r.VulnerabilityIndex}</td>
                <td className="px-3 py-2">{r.AQI}</td>
              </tr>
            ))}
            {rows.length===0 && (<tr><td colSpan={4} className="px-3 py-4 text-center text-muted-foreground">No results yet. Try Run.</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  )
}
