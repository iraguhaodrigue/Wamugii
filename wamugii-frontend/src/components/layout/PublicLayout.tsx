import { Outlet } from 'react-router-dom'
import { AnnouncementBar } from './AnnouncementBar'
import { Header } from './Header'
import { Footer } from './Footer'

/**
 * The public marketing site is permanently dark — it reuses the same `.dark`
 * token scope the dashboard's theme toggle applies to `<body>` (see
 * ThemeContext), just applied unconditionally here instead of driven by a
 * toggle, since there's no light/dark switch on the public site. Every
 * `bg-panel` / `text-slate-*` / `bg-brand-*` utility below this element
 * therefore resolves to its dark value automatically — no `dark:` variants.
 */
export function PublicLayout() {
  return (
    <div className="dark app-atmosphere flex min-h-svh flex-col text-slate-400">
      <AnnouncementBar />
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
