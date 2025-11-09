import { useEffect, useState } from 'react'
import { API_BASE, http } from '../lib/api'
import type { Location } from '../lib/types'
import Busy from '../components/Busy'
import ErrorBanner from '../components/ErrorBanner'
import SectionTitle from '../components/SectionTitle'
import { Database, Settings2, Trash2, Plus } from 'lucide-react'

export default function LocationsPanel(){
  const [rows, setRows] = useState<Location[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string|null>(null)
  const [busy, setBusy] = useState(false)
  const [form, setForm] = useState<Partial<Location>>({ VulnerabilityIndex:0, Population:0 })

  async function load(){
    setLoading(true); setError(null)
    try{
      const data = await http<Location[]>('/api/locations')
      setRows(data)
    }catch(e:any){
      setError(e.message || String(e))
    }finally{ setLoading(false) }
  }
  useEffect(()=>{ load() }, [])

  async function createLocation(){
    setBusy(true)
    try{
      await http('/api/locations', { method:'POST', body: JSON.stringify(form) })
      setForm({ VulnerabilityIndex:0, Population:0 })
      await load()
    }catch(e:any){ alert(e.message || String(e)) }finally{ setBusy(false) }
  }

  async function updateLocation(zip:string, patch: Partial<Location>){
    setBusy(true)
    try{
      await http(`/api/locations/${zip}`, { method:'PUT', body: JSON.stringify(patch) })
      await load()
    }catch(e:any){ alert(e.message || String(e)) }finally{ setBusy(false) }
  }

  async function deleteLocation(zip:string){
    if(!confirm(`Delete ${zip}?`)) return
    setBusy(true)
    try{
      await http(`/api/locations/${zip}`, { method:'DELETE' })
      await load()
    }catch(e:any){ alert(e.message || String(e)) }finally{ setBusy(false) }
  }

  return (
    <div className="relative w-full rounded-2xl border p-4">
      <Busy show={busy} />
      <SectionTitle icon={Database} title="Locations" hint="Create, read, update, delete" />

      <div className="mt-3 grid grid-cols-1 gap-2 rounded-2xl border p-3 md:grid-cols-5">
        <input className="rounded-xl border px-3 py-2" placeholder="ZipCode"
          value={form.ZipCode || ''} onChange={(e)=>setForm(f=>({ ...f, ZipCode: e.target.value }))}/>
        <input className="rounded-xl border px-3 py-2" placeholder="Location Name"
          value={form.LocationName || ''} onChange={(e)=>setForm(f=>({ ...f, LocationName: e.target.value }))}/>
        <input className="rounded-xl border px-3 py-2" placeholder="Population" type="number"
          value={form.Population ?? 0} onChange={(e)=>setForm(f=>({ ...f, Population: Number(e.target.value) }))}/>
        <input className="rounded-xl border px-3 py-2" placeholder="VulnerabilityIndex" type="number" step="0.01"
          value={form.VulnerabilityIndex ?? 0} onChange={(e)=>setForm(f=>({ ...f, VulnerabilityIndex: Number(e.target.value) }))}/>
        <button onClick={createLocation} className="flex items-center justify-center gap-2 rounded-xl bg-black px-3 py-2 text-white">
          <Plus className="h-4 w-4" /> Add
        </button>
      </div>

      <ErrorBanner message={error} />

      <div className="mt-3 overflow-auto rounded-2xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted/30">
            <tr>
              <th className="px-3 py-2 text-left">ZipCode</th>
              <th className="px-3 py-2 text-left">Name</th>
              <th className="px-3 py-2 text-left">Population</th>
              <th className="px-3 py-2 text-left">VulnerabilityIndex</th>
              <th className="px-3 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={5} className="px-3 py-4 text-center text-muted-foreground">Loading...</td></tr>
            )}
            {rows.map(row => (
              <tr key={row.ZipCode} className="border-t">
                <td className="px-3 py-2 font-medium">{row.ZipCode}</td>
                <td className="px-3 py-2">{row.LocationName}</td>
                <td className="px-3 py-2">{row.Population.toLocaleString()}</td>
                <td className="px-3 py-2">{row.VulnerabilityIndex}</td>
                <td className="px-3 py-2">
                  <div className="flex items-center gap-2">
                    <button className="flex items-center gap-1 rounded-xl border px-2 py-1"
                      onClick={()=>updateLocation(row.ZipCode, { VulnerabilityIndex: Number((row.VulnerabilityIndex + 0.1).toFixed(2)) })}>
                      <Settings2 className="h-4 w-4" /> Bump VI +0.1
                    </button>
                    <button className="flex items-center gap-1 rounded-xl border px-2 py-1 text-red-600"
                      onClick={()=>deleteLocation(row.ZipCode)}>
                      <Trash2 className="h-4 w-4" /> Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
