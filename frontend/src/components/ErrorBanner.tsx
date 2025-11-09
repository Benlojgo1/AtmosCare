export default function ErrorBanner({ message }:{ message?: string | null }){
  if(!message) return null
  return (
    <div className="mt-3 rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
      {message}
    </div>
  )
}
