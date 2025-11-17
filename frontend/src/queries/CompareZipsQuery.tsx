import { useMemo, useState } from 'react'
import { http } from '../lib/api'
import ErrorBanner from '../components/ErrorBanner'
import Busy from '../components/Busy'
import SectionTitle from '../components/SectionTitle'
import { Search } from 'lucide-react'
import { ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, LineChart, Line } from 'recharts'

export default function CompareZipsQuery(){
  const [zip1, setZip1] = useState('')
  const [zip2, setZip2] = useState('')
  const [rows, setRows] = useState<any[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string|null>(null)

  async function run(){
    if(!zip1 || !zip2) return alert('Enter both ZIPs')
    setBusy(true); setErr(null)
    try{
      const data = await http<any[]>(`/api/queries/compare?zip1=${encodeURIComponent(zip1)}&zip2=${encodeURIComponent(zip2)}`)
      setRows(data)
    }catch(e:any){ setErr(e.message || String(e)) }finally{ setBusy(false) }
  }

  const chartData = useMemo(()=> rows.map((r:any)=>({ name:r.ZipCode, Temp:r.AvgTemp, Humidity:r.AvgHumidity })), [rows])

  return (
    <div className="relative rounded-2xl border p-4">
      <Busy show={busy} />
      <SectionTitle icon={Search} title="Compare ZIP Codes" hint="Avg Temp & Humidity (7 days)" />
      <div className="mt-3 flex flex-col gap-2 md:flex-row">
        <input className="rounded-xl border px-3 py-2" placeholder="ZIP 1" value={zip1} onChange={e=>setZip1(e.target.value)} />
        <input className="rounded-xl border px-3 py-2" placeholder="ZIP 2" value={zip2} onChange={e=>setZip2(e.target.value)} />
        <button onClick={run} className="rounded-xl bg-black px-3 py-2 text-white">Run</button>
      </div>
      <ErrorBanner message={err} />

      {rows.length>0 && (
        <div className="mt-3 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="h-72 w-full rounded-2xl border p-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Temp" name="Avg Temp (°F)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="h-72 w-full rounded-2xl border p-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="Humidity" name="Avg Humidity (%)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="mt-3 overflow-auto rounded-2xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted/30">
            <tr>
              <th className="px-3 py-2 text-left">ZipCode</th>
              <th className="px-3 py-2 text-left">Avg Temp (°F)</th>
              <th className="px-3 py-2 text-left">Avg Humidity (%)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r,i)=>(
              <tr key={i} className="border-t">
                <td className="px-3 py-2">{r.ZipCode}</td>
                <td className="px-3 py-2">{r.AvgTemp}</td>
                <td className="px-3 py-2">{r.AvgHumidity}</td>
              </tr>
            ))}
            {rows.length===0 && (<tr><td colSpan={3} className="px-3 py-4 text-center text-muted-foreground">No results yet. Run to compare.</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  )
}
