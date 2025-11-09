import { useMemo, useState } from 'react'
import { http } from '../lib/api'
import ErrorBanner from '../components/ErrorBanner'
import Busy from '../components/Busy'
import SectionTitle from '../components/SectionTitle'
import { Search } from 'lucide-react'
import { ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar } from 'recharts'

export default function AllocationQuery(){
  const [rows, setRows] = useState<any[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string|null>(null)

  async function run(){
    setBusy(true); setErr(null)
    try{
      const data = await http<any[]>('/api/queries/resource-allocation')
      setRows(data)
    }catch(e:any){ setErr(e.message || String(e)) }finally{ setBusy(false) }
  }

  const chartData = useMemo(()=> rows.map((r:any)=>({ group: r.VulnerabilityBucket, PercentUrgent: r.PercentUrgent })), [rows])

  return (
    <div className="relative rounded-2xl border p-4">
      <Busy show={busy} />
      <SectionTitle icon={Search} title="Resource Allocation Metric" hint="% locations urgent by vulnerability" />
      <button onClick={run} className="mt-3 rounded-xl bg-black px-3 py-2 text-white">Run</button>
      <ErrorBanner message={err} />

      {rows.length>0 && (
        <div className="mt-3 h-72 w-full rounded-2xl border p-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="group" />
              <YAxis unit="%" />
              <Tooltip />
              <Legend />
              <Bar dataKey="PercentUrgent" name="% Urgent" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="mt-3 overflow-auto rounded-2xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted/30">
            <tr>
              <th className="px-3 py-2 text-left">Vulnerability Group</th>
              <th className="px-3 py-2 text-left">% Urgent</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r,i)=>(
              <tr key={i} className="border-t">
                <td className="px-3 py-2">{r.VulnerabilityBucket}</td>
                <td className="px-3 py-2">{r.PercentUrgent}%</td>
              </tr>
            ))}
            {rows.length===0 && (<tr><td colSpan={2} className="px-3 py-4 text-center text-muted-foreground">No results yet. Run to calculate.</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  )
}
