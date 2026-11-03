import { useState } from 'react'
import { ChevronDown, Clapperboard, PlayCircle } from 'lucide-react'
import { VideoEmbed } from '@/components/courses/VideoEmbed'
import { cn } from '@/utils/cn'

export interface LectureVideo {
  title: string
  url: string
  minutes?: number | null
}

function youtubeThumb(url: string): string | null {
  const m = url.match(/(?:v=|youtu\.be\/|embed\/)([\w-]{11})/)
  return m ? `https://i.ytimg.com/vi/${m[1]}/mqdefault.jpg` : null
}

function fmt(minutes?: number | null): string {
  if (!minutes) return ''
  if (minutes < 60) return `${minutes} min`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m ? `${h} h ${m} min` : `${h} h`
}

/**
 * "Go deeper" -- the longer full-lecture videos under a lesson's short video.
 * Each one loads only when the student opens it, so a lesson page with three
 * long lectures stays as fast as one with none.
 */
export function FullLectures({ videos }: { videos: LectureVideo[] }) {
  const [open, setOpen] = useState<number | null>(null)
  if (!videos.length) return null
  return (
    <div className="rounded-2xl border border-slate-200 bg-panel p-4 sm:p-5">
      <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-accent-600">
        <Clapperboard className="size-4" aria-hidden="true" /> Go deeper — full lecture{videos.length > 1 ? 's' : ''}
      </p>
      <p className="mt-1 text-sm text-slate-500">
        Longer videos that explain every part of this lesson in detail. Watch them after the short video, or whenever you want more.
      </p>
      <ul className="mt-3 space-y-2.5">
        {videos.map((v, i) => {
          const thumb = youtubeThumb(v.url)
          const isOpen = open === i
          return (
            <li key={v.url + i} className="overflow-hidden rounded-xl border border-slate-200">
              <button
                type="button"
                onClick={() => setOpen(isOpen ? null : i)}
                aria-expanded={isOpen}
                className="flex w-full items-center gap-3 p-2.5 text-left transition-colors hover:bg-slate-50"
              >
                <span className="relative block h-14 w-24 shrink-0 overflow-hidden rounded-lg bg-slate-900 sm:h-16 sm:w-28">
                  {thumb && <img src={thumb} alt="" loading="lazy" className="size-full object-cover opacity-90" />}
                  <PlayCircle className="absolute inset-0 m-auto size-7 text-white drop-shadow" aria-hidden="true" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block text-sm font-semibold text-slate-900">{v.title}</span>
                  {v.minutes ? <span className="mt-0.5 block text-xs text-slate-500">{fmt(v.minutes)} · full lecture</span> : null}
                </span>
                <ChevronDown className={cn('size-4 shrink-0 text-slate-400 transition-transform', isOpen && 'rotate-180')} aria-hidden="true" />
              </button>
              {isOpen && (
                <div className="border-t border-slate-200 p-2.5">
                  <VideoEmbed url={v.url} title={v.title} />
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
