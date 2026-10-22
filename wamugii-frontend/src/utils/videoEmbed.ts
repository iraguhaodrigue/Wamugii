/**
 * Safe YouTube / Vimeo embed helpers.
 *
 * The lesson store carries a plain URL and the player needs to render a video.
 * We never pass the raw URL into the DOM: we parse out the provider and video
 * id, decide whether we trust the pair, and render the official embed iframe
 * ourselves. Any URL that isn't a YouTube or Vimeo video we recognise is
 * refused -- a lesson shows "video unavailable" rather than embedding
 * something else.
 *
 * The parsers deliberately rely on `URL`, not substring matching, so a URL
 * like `https://evil.example/youtu.be/XXXXXXX` can't impersonate YouTube: we
 * check the actual host.
 */

export type VideoProvider = 'youtube' | 'vimeo'

export interface ParsedVideo {
  provider: VideoProvider
  id: string
  /** The URL we render in the iframe `src`, pre-escaped by `URL`. */
  embedUrl: string
}

const YOUTUBE_HOSTS = new Set([
  'youtube.com',
  'www.youtube.com',
  'm.youtube.com',
  'youtu.be',
])
const VIMEO_HOSTS = new Set(['vimeo.com', 'www.vimeo.com', 'player.vimeo.com'])

// 11-char YouTube id, 1+ digit Vimeo id. Both are deliberately strict -- a
// `v` param pulled off a crafted URL that doesn't match the real id shape
// is refused rather than embedded.
const YOUTUBE_ID_RE = /^[A-Za-z0-9_-]{11}$/
const VIMEO_ID_RE = /^\d+$/

/**
 * Parse a URL to the provider + id we trust, or null.
 *
 * null means "we can't embed this safely" and the player should fall back to
 * the external-link treatment rather than render anything.
 */
export function parseVideoUrl(input: string | null | undefined): ParsedVideo | null {
  if (!input) return null
  const trimmed = input.trim()
  if (!trimmed) return null

  let parsed: URL
  try {
    parsed = new URL(trimmed)
  } catch {
    return null
  }
  if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') return null

  const host = parsed.hostname.toLowerCase()

  if (YOUTUBE_HOSTS.has(host)) {
    const id = extractYouTubeId(parsed)
    if (!id || !YOUTUBE_ID_RE.test(id)) return null
    return {
      provider: 'youtube',
      id,
      // The nocookie host doesn't drop a cookie for anonymous viewers -- a
      // small privacy win worth having since the catalogue page is public.
      embedUrl: `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}`,
    }
  }

  if (VIMEO_HOSTS.has(host)) {
    const id = extractVimeoId(parsed)
    if (!id || !VIMEO_ID_RE.test(id)) return null
    return {
      provider: 'vimeo',
      id,
      embedUrl: `https://player.vimeo.com/video/${encodeURIComponent(id)}`,
    }
  }

  return null
}

/**
 * The two YouTube URL shapes we recognise:
 *   * https://www.youtube.com/watch?v=XXXXXXXXXXX
 *   * https://youtu.be/XXXXXXXXXXX
 * The `/embed/XXXXXXXXXXX` and `/shorts/XXXXXXXXXXX` paths come through too,
 * so a URL copied from a creator's own embed snippet works.
 */
function extractYouTubeId(url: URL): string | null {
  const host = url.hostname.toLowerCase()
  if (host === 'youtu.be') {
    // The path is `/{id}`; drop the leading slash and any trailing junk.
    return url.pathname.replace(/^\//, '').split('/')[0] || null
  }
  // youtube.com variants: `/watch?v=`, `/embed/{id}`, `/shorts/{id}`.
  if (url.pathname === '/watch') {
    return url.searchParams.get('v')
  }
  const segments = url.pathname.split('/').filter(Boolean)
  if (segments.length >= 2 && (segments[0] === 'embed' || segments[0] === 'shorts')) {
    return segments[1] ?? null
  }
  return null
}

/**
 * The two Vimeo shapes we recognise:
 *   * https://vimeo.com/{id}
 *   * https://player.vimeo.com/video/{id}
 * The id is always the trailing numeric segment.
 */
function extractVimeoId(url: URL): string | null {
  const segments = url.pathname.split('/').filter(Boolean)
  for (let i = segments.length - 1; i >= 0; i -= 1) {
    const segment = segments[i]
    if (segment && VIMEO_ID_RE.test(segment)) return segment
  }
  return null
}

/**
 * `true` iff a URL parses into a safe embed. Convenience for admin forms that
 * want to validate the field as the user types without rendering anything.
 */
export function isSupportedVideoUrl(input: string | null | undefined): boolean {
  return parseVideoUrl(input) !== null
}
