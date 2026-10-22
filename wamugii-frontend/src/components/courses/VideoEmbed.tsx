import { AlertCircle, PlayCircle } from 'lucide-react'
import { parseVideoUrl } from '@/utils/videoEmbed'

export interface VideoEmbedProps {
  url: string | null | undefined
  title?: string
}

/**
 * Render a safely-embedded YouTube or Vimeo video.
 *
 * The URL goes through `parseVideoUrl`, which refuses anything that isn't a
 * recognised video on a trusted host and returns a pre-built embed URL. The
 * iframe is sandboxed to allow-scripts and allow-same-origin only -- enough
 * for the player to work, not enough for the embed to navigate the parent or
 * drive cross-site requests.
 *
 * An unrecognised URL isn't rendered at all; we show a plain message instead
 * so a lesson with a malformed video_url degrades to "unavailable" rather
 * than embedding something unexpected.
 */
export function VideoEmbed({ url, title }: VideoEmbedProps) {
  if (!url) return null
  const parsed = parseVideoUrl(url)

  if (!parsed) {
    return (
      <div
        role="alert"
        className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800"
      >
        <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
        <div>
          <p className="font-medium">Video unavailable</p>
          <p className="mt-0.5 text-xs">
            This lesson's video URL isn't a supported YouTube or Vimeo link.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative aspect-video overflow-hidden rounded-xl border border-slate-200 bg-slate-900">
      <iframe
        src={parsed.embedUrl}
        title={title ?? 'Lesson video'}
        className="absolute inset-0 size-full"
        loading="lazy"
        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
        allowFullScreen
        referrerPolicy="strict-origin-when-cross-origin"
        sandbox="allow-scripts allow-same-origin allow-presentation"
      />
    </div>
  )
}

/** Thumbnail-style placeholder for a lesson row that has no video attached. */
export function VideoPlaceholder() {
  return (
    <div className="flex aspect-video items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50 text-slate-400">
      <div className="flex flex-col items-center gap-1 text-xs">
        <PlayCircle className="size-6" aria-hidden="true" />
        No video for this lesson
      </div>
    </div>
  )
}
