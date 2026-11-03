import { useLayoutEffect, useRef } from 'react'
import { useLocation, useNavigationType } from 'react-router-dom'

/**
 * Opens every new page at the top, without a visible scroll.
 *
 * Without this, a click on a link near the bottom of a long page (a lesson in
 * the course outline, say) kept the old scroll position, so the next page
 * flashed half-way down before jumping. Only a change of page counts: a new
 * `?query` on the same page (the course player's `?lesson=`) is left alone.
 * Back/forward (POP) is left alone so the browser can return the reader to
 * where they were, and `#anchor` links keep working.
 */
export function ScrollToTop() {
  const { pathname, hash } = useLocation()
  const navigationType = useNavigationType()
  const lastPath = useRef(pathname)

  useLayoutEffect(() => {
    if (lastPath.current === pathname) return
    lastPath.current = pathname
    if (navigationType === 'POP' || hash) return
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [pathname, hash, navigationType])

  return null
}
