import { useEffect } from 'react'

const SITE_NAME = 'WAMUGII TECH SOLUTIONS'

// Search engines cut a description around here, so a longer one is wasted
// bytes in the page and reads as truncated in results either way.
const MAX_DESCRIPTION = 160

/**
 * Sets the browser tab title, and optionally the meta description, for a page.
 *
 * Standalone on purpose. `usePageTitle` (PageTitleContext) feeds the dashboard
 * top bar and throws outside its provider, so public pages cannot use it --
 * which is why they all shared one title before. This hook talks to the
 * document directly and works anywhere in the tree.
 *
 * Titles come out as "Page name | WAMUGII TECH SOLUTIONS"; passing nothing
 * leaves the site name alone, which is what the home page wants.
 *
 * Both values are restored when the page unmounts, so navigating to a page
 * that sets no title of its own falls back to the site default instead of
 * keeping the previous page's.
 */
export function useDocumentTitle(title?: string | null, description?: string | null): void {
  useEffect(() => {
    const previous = document.title
    document.title = title ? `${title} | ${SITE_NAME}` : SITE_NAME
    return () => {
      document.title = previous
    }
  }, [title])

  useEffect(() => {
    if (!description) return

    let tag = document.querySelector<HTMLMetaElement>('meta[name="description"]')
    let created = false
    if (!tag) {
      // index.html ships one, but don't depend on that.
      tag = document.createElement('meta')
      tag.setAttribute('name', 'description')
      document.head.appendChild(tag)
      created = true
    }

    const previous = tag.getAttribute('content')
    const trimmed = description.trim()
    tag.setAttribute(
      'content',
      trimmed.length > MAX_DESCRIPTION ? `${trimmed.slice(0, MAX_DESCRIPTION - 1).trimEnd()}…` : trimmed,
    )

    return () => {
      if (created) {
        tag?.remove()
      } else if (previous !== null) {
        tag?.setAttribute('content', previous)
      }
    }
  }, [description])
}
