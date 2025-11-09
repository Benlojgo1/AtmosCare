import React from 'react'

type Tab = { id:string; label:string }
export function Tabs({ tabs, value, onChange }:{ tabs:Tab[]; value:string; onChange:(id:string)=>void }){
  return (
    <div className="w-full">
      <div className="grid gap-2 sm:grid-cols-3 lg:grid-cols-5">
        {tabs.map(t => (
          <button key={t.id}
            className={`rounded-xl border px-3 py-2 text-sm ${value===t.id ? 'bg-black text-white' : 'bg-muted'}`}
            onClick={()=>onChange(t.id)}>{t.label}</button>
        ))}
      </div>
    </div>
  )
}

export function TabPanel({ active, children }:{ active:boolean; children:React.ReactNode }){
  if(!active) return null
  return <div className="mt-3">{children}</div>
}
