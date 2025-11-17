import { Loader2 } from 'lucide-react'

export default function Busy({ show }:{ show:boolean }){
  if(!show) return null
  return (
    <div className="absolute inset-0 z-10 grid place-items-center rounded-2xl bg-white/60">
      <Loader2 className="h-6 w-6 animate-spin" />
    </div>
  )
}
