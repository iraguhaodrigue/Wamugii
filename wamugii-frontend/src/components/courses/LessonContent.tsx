import { Fragment, useMemo, useState, type ReactNode } from 'react'
import { CheckCircle2, Circle, Lightbulb, PenLine, Sparkles, Target } from 'lucide-react'
import { Reveal } from '@/components/common/Reveal'
import { cn } from '@/utils/cn'

/**
 * Turns a lesson's markdown into an organised, animated lesson:
 *
 *  * each `## heading` becomes a numbered step card on a timeline,
 *  * `**Learning objective:**` becomes a goal card at the top,
 *  * `**Takeaway:**` becomes a highlighted "remember this" card,
 *  * a "Try it yourself" / practice / project section becomes an activity card
 *    the student can tick off,
 *  * a bullet list where every item starts with a bold term becomes term cards.
 *
 * A small, dependency-free parser covers what the WAMUGII lessons use:
 * headings, paragraphs, bullet and numbered lists, tables, code blocks,
 * quotes, and inline bold / italic / code / links. Nothing is injected as
 * HTML, so lesson text can never run script.
 */

// --- block parser ---------------------------------------------------------

type Block =
  | { kind: 'h3'; text: string }
  | { kind: 'p'; text: string }
  | { kind: 'ul'; items: string[] }
  | { kind: 'ol'; items: string[] }
  | { kind: 'code'; lang: string; text: string }
  | { kind: 'quote'; text: string }
  | { kind: 'table'; head: string[]; rows: string[][] }

interface Section {
  title: string | null
  blocks: Block[]
}

const UL = /^\s*[-*]\s+(.*)$/
const OL = /^\s*\d+[.)]\s+(.*)$/

function splitRow(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((c) => c.trim())
}

function parseBlocks(lines: string[]): Block[] {
  const blocks: Block[] = []
  let i = 0
  while (i < lines.length) {
    const line = lines[i]!
    if (!line.trim()) {
      i++
      continue
    }
    if (line.trim().startsWith('```')) {
      const lang = line.trim().slice(3).trim()
      const body: string[] = []
      i++
      while (i < lines.length && !lines[i]!.trim().startsWith('```')) body.push(lines[i++]!)
      i++
      blocks.push({ kind: 'code', lang, text: body.join('\n') })
      continue
    }
    if (line.startsWith('### ')) {
      blocks.push({ kind: 'h3', text: line.slice(4).trim() })
      i++
      continue
    }
    if (line.trim().startsWith('|')) {
      const rows: string[][] = []
      while (i < lines.length && lines[i]!.trim().startsWith('|')) {
        const cells = splitRow(lines[i]!)
        if (!cells.every((c) => /^:?-{2,}:?$/.test(c))) rows.push(cells)
        i++
      }
      blocks.push({ kind: 'table', head: rows[0] ?? [], rows: rows.slice(1) })
      continue
    }
    if (line.startsWith('> ')) {
      const body: string[] = []
      while (i < lines.length && lines[i]!.startsWith('>')) body.push(lines[i++]!.replace(/^>\s?/, ''))
      blocks.push({ kind: 'quote', text: body.join(' ') })
      continue
    }
    const listRe = UL.test(line) ? UL : OL.test(line) ? OL : null
    if (listRe) {
      const items: string[] = []
      while (i < lines.length) {
        const cur = lines[i]!
        const m = cur.match(listRe)
        if (m) {
          items.push(m[1]!)
        } else if (cur.trim() && /^\s{2,}/.test(cur) && items.length) {
          items[items.length - 1] += ' ' + cur.trim()
        } else {
          break
        }
        i++
      }
      blocks.push({ kind: listRe === UL ? 'ul' : 'ol', items })
      continue
    }
    const para: string[] = []
    while (
      i < lines.length &&
      lines[i]!.trim() &&
      !lines[i]!.startsWith('#') &&
      !lines[i]!.trim().startsWith('```') &&
      !lines[i]!.trim().startsWith('|') &&
      !UL.test(lines[i]!) &&
      !OL.test(lines[i]!)
    ) {
      para.push(lines[i++]!.trim())
    }
    if (para.length) blocks.push({ kind: 'p', text: para.join(' ') })
    else i++
  }
  return blocks
}

function parseSections(markdown: string): Section[] {
  const sections: Section[] = []
  let current: { title: string | null; lines: string[] } = { title: null, lines: [] }
  let inFence = false
  for (const raw of markdown.replace(/\r\n/g, '\n').split('\n')) {
    if (raw.trim().startsWith('```')) inFence = !inFence
    if (!inFence && /^#{1,2}\s/.test(raw)) {
      sections.push({ title: current.title, blocks: parseBlocks(current.lines) })
      current = { title: raw.replace(/^#{1,2}\s+/, '').trim(), lines: [] }
    } else {
      current.lines.push(raw)
    }
  }
  sections.push({ title: current.title, blocks: parseBlocks(current.lines) })
  return sections.filter((s) => s.title || s.blocks.length)
}

// --- inline ---------------------------------------------------------------

// Underscore italics only at word edges, so snake_case names in the Python
// lessons (learning_rate, max_depth) are left alone.
const INLINE =
  /(`[^`]+`|\*\*[^*]+\*\*|\*[^*\s][^*]*\*|(?<![A-Za-z0-9])_[^_\s][^_]*_(?![A-Za-z0-9])|\[[^\]]+\]\([^)\s]+\))/g

function inline(text: string): ReactNode[] {
  return text.split(INLINE).map((part, i) => {
    if (!part) return null
    if (part.startsWith('`')) {
      return (
        <code key={i} className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[0.85em] text-brand-700">
          {part.slice(1, -1)}
        </code>
      )
    }
    if (part.startsWith('**')) {
      return (
        <strong key={i} className="font-semibold text-slate-900">
          {inline(part.slice(2, -2))}
        </strong>
      )
    }
    if ((part.startsWith('*') || part.startsWith('_')) && part.length > 2) {
      return <em key={i}>{part.slice(1, -1)}</em>
    }
    const link = part.match(/^\[([^\]]+)\]\(([^)\s]+)\)$/)
    if (link) {
      const href = /^(https?:|mailto:|\/)/.test(link[2]!) ? link[2] : undefined
      return (
        <a key={i} href={href} target="_blank" rel="noreferrer" className="font-medium text-brand-600 underline underline-offset-2">
          {link[1]}
        </a>
      )
    }
    return <Fragment key={i}>{part}</Fragment>
  })
}

// --- rendering ------------------------------------------------------------

const TERM_ITEM = /^\*\*([^*]+)\*\*\s*(?:\(([^)]*)\))?\s*[—–:-]\s*(.*)$/

function BlockView({ block }: { block: Block }) {
  switch (block.kind) {
    case 'h3':
      return <h4 className="text-base font-semibold text-slate-900">{inline(block.text)}</h4>
    case 'p':
      return <p className="leading-relaxed text-slate-600">{inline(block.text)}</p>
    case 'quote':
      return (
        <blockquote className="border-l-4 border-accent-400 bg-accent-50/60 px-4 py-3 italic text-slate-700">
          {inline(block.text)}
        </blockquote>
      )
    case 'code':
      return (
        <pre className="overflow-x-auto rounded-xl bg-slate-950 p-4 text-[13px] leading-relaxed text-cyan-100">
          <code>{block.text}</code>
        </pre>
      )
    case 'table':
      return (
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-900">
              <tr>
                {block.head.map((h, i) => (
                  <th key={i} className="px-3 py-2 font-semibold">
                    {inline(h)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((r, ri) => (
                <tr key={ri} className="border-t border-slate-100">
                  {r.map((c, ci) => (
                    <td key={ci} className="px-3 py-2 text-slate-600">
                      {inline(c)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    case 'ol':
      return (
        <ol className="space-y-2">
          {block.items.map((item, i) => (
            <li key={i} className="flex gap-3 text-slate-600">
              <span className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-bold text-brand-700">
                {i + 1}
              </span>
              <span className="leading-relaxed">{inline(item)}</span>
            </li>
          ))}
        </ol>
      )
    case 'ul': {
      const terms = block.items.map((it) => it.match(TERM_ITEM))
      if (block.items.length >= 2 && terms.every(Boolean)) {
        return (
          <div className="grid gap-3 sm:grid-cols-2">
            {terms.map((m, i) => (
              <div
                key={i}
                className="lesson-term rounded-xl border border-slate-200 bg-gradient-to-br from-brand-50/70 to-transparent p-4"
                style={{ animationDelay: `${i * 90}ms` }}
              >
                <p className="font-semibold text-slate-900">
                  {m![1]}
                  {m![2] && <span className="ml-1 text-xs font-medium text-slate-400">{m![2]}</span>}
                </p>
                <p className="mt-1 text-sm leading-relaxed text-slate-600">{inline(m![3]!)}</p>
              </div>
            ))}
          </div>
        )
      }
      return (
        <ul className="space-y-2">
          {block.items.map((item, i) => (
            <li key={i} className="flex gap-3 text-slate-600">
              <span className="mt-2 size-1.5 shrink-0 rounded-full bg-gradient-to-r from-brand-400 to-accent-400" />
              <span className="leading-relaxed">{inline(item)}</span>
            </li>
          ))}
        </ul>
      )
    }
  }
}

function Blocks({ blocks }: { blocks: Block[] }) {
  return (
    <div className="space-y-4 text-[15px]">
      {blocks.map((b, i) => (
        <BlockView key={i} block={b} />
      ))}
    </div>
  )
}

const ACTIVITY = /try it|practice|exercise|project|assessment|your turn|activity/i

/** Pulls a `**Label:** text` paragraph out of the blocks. */
function extract(blocks: Block[], label: RegExp): { text: string | null; rest: Block[] } {
  let text: string | null = null
  const rest: Block[] = []
  for (const b of blocks) {
    if (text === null && b.kind === 'p') {
      const m = b.text.match(new RegExp(`^\\*\\*(?:${label.source}):?\\*\\*:?\\s*(.*)$`, 'i'))
      if (m) {
        text = m[1]!
        continue
      }
    }
    rest.push(b)
  }
  return { text, rest }
}

export interface LessonContentProps {
  content: string
  /** Changes whenever the lesson changes, so ticked activities reset. */
  lessonKey: number | string
}

export function sectionTitles(content: string): string[] {
  return parseSections(content)
    .map((s) => s.title?.replace(/[*_`]/g, ''))
    .filter((t): t is string => Boolean(t))
}

export function LessonContent({ content, lessonKey }: LessonContentProps) {
  const [done, setDone] = useState<Record<string, boolean>>({})

  const { objective, takeaway, sections } = useMemo(() => {
    let objective: string | null = null
    let takeaway: string | null = null
    const sections = parseSections(content).map((s) => {
      const o = extract(s.blocks, /learning objectives?|objective/)
      if (o.text && !objective) objective = o.text
      const t = extract(o.rest, /takeaway|key takeaway|remember/)
      if (t.text && !takeaway) takeaway = t.text
      return { ...s, blocks: t.rest }
    })
    return { objective, takeaway, sections: sections.filter((s) => s.title || s.blocks.length) }
  }, [content])

  let step = 0
  // Ids follow the titled sections only, matching `sectionTitles()` order, so
  // the player's section chips can jump straight to them.
  let titled = -1

  return (
    <div className="space-y-6" key={lessonKey}>
      {objective && (
        <Reveal>
          <div className="flex gap-4 rounded-2xl border border-brand-200 bg-brand-50/70 p-5">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[var(--color-brand-solid)] text-white">
              <Target className="size-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-brand-700">Your goal in this lesson</p>
              <p className="mt-1 leading-relaxed text-slate-700">{inline(objective)}</p>
            </div>
          </div>
        </Reveal>
      )}

      <ol className="lesson-timeline relative space-y-6">
        {sections.map((s, idx) => {
          const isActivity = Boolean(s.title && ACTIVITY.test(s.title))
          if (s.title) titled++
          const id = s.title ? `lesson-step-${titled}` : undefined
          if (isActivity) {
            const key = `${lessonKey}-${idx}`
            const ticked = Boolean(done[key])
            return (
              <li key={idx} id={id} className="relative scroll-mt-24 pl-12">
                <span className="absolute left-0 top-1 flex size-9 items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white shadow-[var(--shadow-glow-brand)]">
                  <PenLine className="size-4" aria-hidden="true" />
                </span>
                <Reveal>
                  <div className="lesson-activity relative overflow-hidden rounded-2xl border border-accent-200 bg-panel p-6 shadow-[var(--shadow-card)]">
                    <p className="text-xs font-bold uppercase tracking-wider text-accent-600">Activity</p>
                    <h3 className="mt-1 text-lg font-semibold text-slate-900">{inline(s.title!)}</h3>
                    <div className="mt-3">
                      <Blocks blocks={s.blocks} />
                    </div>
                    <button
                      type="button"
                      onClick={() => setDone((d) => ({ ...d, [key]: !ticked }))}
                      className={cn(
                        'mt-5 inline-flex items-center gap-2 rounded-lg border px-3.5 py-2 text-sm font-semibold transition-colors',
                        ticked
                          ? 'border-emerald-300 bg-emerald-50 text-emerald-700'
                          : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-700',
                      )}
                    >
                      {ticked ? (
                        <CheckCircle2 className="lesson-pop size-4" aria-hidden="true" />
                      ) : (
                        <Circle className="size-4" aria-hidden="true" />
                      )}
                      {ticked ? 'Done — nice work!' : 'I did this activity'}
                    </button>
                  </div>
                </Reveal>
              </li>
            )
          }
          if (!s.title) {
            return (
              <li key={idx} id={id} className="relative pl-12">
                <span className="absolute left-0 top-1 flex size-9 items-center justify-center rounded-full bg-brand-50 text-brand-600 ring-4 ring-[var(--color-bg)]">
                  <Sparkles className="size-4" aria-hidden="true" />
                </span>
                <Reveal>
                  <Blocks blocks={s.blocks} />
                </Reveal>
              </li>
            )
          }
          step++
          return (
            <li key={idx} id={id} className="relative scroll-mt-24 pl-12">
              <span className="absolute left-0 top-1 flex size-9 items-center justify-center rounded-full border-2 border-brand-400 bg-panel text-sm font-bold text-brand-700 ring-4 ring-[var(--color-bg)]">
                {step}
              </span>
              <Reveal>
                <div className="rounded-2xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] transition-shadow hover:shadow-[var(--shadow-glow-brand)]">
                  <h3 className="text-lg font-semibold text-slate-900">{inline(s.title)}</h3>
                  {s.blocks.length > 0 && (
                    <div className="mt-3">
                      <Blocks blocks={s.blocks} />
                    </div>
                  )}
                </div>
              </Reveal>
            </li>
          )
        })}
      </ol>

      {takeaway && (
        <Reveal>
          <div className="lesson-takeaway relative overflow-hidden rounded-2xl bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] p-6 text-white">
            <div className="flex gap-4">
              <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-white/15">
                <Lightbulb className="size-5" aria-hidden="true" />
              </span>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-white/75">Remember this</p>
                <p className="mt-1 text-base font-medium leading-relaxed [&_strong]:text-white">{inline(takeaway)}</p>
              </div>
            </div>
          </div>
        </Reveal>
      )}
    </div>
  )
}
