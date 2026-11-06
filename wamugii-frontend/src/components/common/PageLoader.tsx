/**
 * Shown for the moment a page's code is being downloaded (pages load on
 * demand, see App.tsx). Kept tiny and dependency-free so it appears at once.
 */
export function PageLoader({ fullScreen = false }: { fullScreen?: boolean }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex items-center justify-center ${fullScreen ? 'min-h-screen' : 'min-h-[50vh]'}`}
    >
      <span className="h-8 w-8 animate-spin rounded-full border-2 border-brand-500/30 border-t-brand-400" />
      <span className="sr-only">Loading…</span>
    </div>
  )
}
