import { createContext, useContext, useEffect, useMemo, useRef, useState, useSyncExternalStore, type ReactNode } from 'react'
import { AlertTriangle, Check, Copy, ExternalLink, Loader2, Pencil, Play, RotateCcw, Square, TerminalSquare } from 'lucide-react'
import { pythonRuntime, unsupportedImports, type RunResult } from '@/lib/python/runtime'
import { cn } from '@/utils/cn'

/**
 * "Run" support for the Python examples in a lesson.
 *
 * LessonContent wraps a lesson in <PythonLesson>. Every Python block in that
 * lesson shares one namespace, like cells in a notebook, so block 3 can use a
 * variable made in block 1. If a block fails because an earlier one was not
 * run yet, the student gets a one-tap "Run the earlier blocks first" fix.
 */

interface LessonCtx {
  sessionId: string
  /** Remember the current (maybe edited) code of the block at a position. */
  setCode: (index: number, code: string) => void
  /** The current code of the block at a position, if it has been shown. */
  getCode: (index: number) => string | undefined
  /** Libraries that stop the block at a position from running in the browser. */
  needsAt: (index: number) => string[] | null
  /** This lesson's notebook in Google Colab, when it has one. */
  colabUrl: string | null
}

const Ctx = createContext<LessonCtx | null>(null)

export function PythonLesson({
  lessonKey,
  needs,
  colabUrl = null,
  children,
}: {
  lessonKey: string | number
  colabUrl?: string | null
  /** Per Python block: why it can only run in Colab, or null (see colabOnlyReasons). */
  needs: (string[] | null)[]
  children: ReactNode
}) {
  const codes = useRef<Record<number, string>>({})
  // A fresh namespace per lesson visit, so an old lesson's variables never leak in.
  const [sessionId] = useState(() => `lesson-${lessonKey}-${Math.random().toString(36).slice(2, 8)}`)
  const value = useMemo<LessonCtx>(
    () => ({
      sessionId,
      setCode: (index, code) => {
        codes.current[index] = code
      },
      getCode: (index) => codes.current[index],
      needsAt: (index) => needs[index] ?? null,
      colabUrl,
    }),
    [sessionId, needs, colabUrl],
  )
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

function useRuntimeStatus() {
  return useSyncExternalStore(
    (cb) => pythonRuntime.subscribe(cb),
    () => pythonRuntime.getStatus().message + '|' + pythonRuntime.getStatus().status,
    () => '|off',
  )
}

const COLAB = 'https://colab.research.google.com/#create=true'

type Phase = 'idle' | 'running' | 'done'

export function PythonCodeBlock({ code, index, label }: { code: string; index: number; label: string }) {
  const lesson = useContext(Ctx)
  const [text, setText] = useState(code)
  const [editing, setEditing] = useState(false)
  const [copied, setCopied] = useState(false)
  const [phase, setPhase] = useState<Phase>('idle')
  const [live, setLive] = useState('')
  const [result, setResult] = useState<RunResult | null>(null)
  const [prep, setPrep] = useState<string | null>(null)
  const status = useRuntimeStatus()
  const [statusMessage] = status.split('|')
  const own = unsupportedImports(text)
  const unsupported = own.length ? own : (lesson?.needsAt(index) ?? [])
  const inherited = !own.length && unsupported.length > 0
  const changed = text !== code

  useEffect(() => {
    lesson?.setCode(index, text)
  }, [lesson, index, text])

  async function copy() {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1800)
    } catch {
      // Clipboard blocked: the student can still select the text by hand.
    }
  }

  async function run(withEarlier = false) {
    if (!lesson || phase === 'running') return
    setPhase('running')
    setResult(null)
    setLive('')
    if (withEarlier) {
      for (let i = 0; i < index; i++) {
        const earlier = lesson.getCode(i)
        if (!earlier || lesson.needsAt(i) || unsupportedImports(earlier).length) continue
        setPrep(`Running block ${i + 1} of ${index}…`)
        const r = await pythonRuntime.run(lesson.sessionId, earlier)
        if (!r.ok) {
          setPrep(null)
          setResult({ ...r, error: `Block ${i + 1} above stopped with an error, so this block was not run.\n\n${r.error ?? ''}` })
          setPhase('done')
          return
        }
      }
      setPrep(null)
    }
    const r = await pythonRuntime.run(lesson.sessionId, text, setLive)
    setResult(r)
    setPhase('done')
  }

  const output = phase === 'running' ? live : result?.output ?? ''
  const showPanel = phase !== 'idle'

  return (
    <div className="overflow-hidden rounded-xl border border-[#1e293b] bg-[#0b1220]" data-python-block={index}>
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#1e293b] px-3 py-1.5">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-[#94a3b8]">
          {label}
          {changed && <span className="ml-2 normal-case tracking-normal text-[#fbbf24]">edited</span>}
        </span>
        <div className="flex items-center gap-1">
          {lesson && (
            <>
              {changed && (
                <button
                  type="button"
                  onClick={() => setText(code)}
                  className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-[#cbd5e1] transition-colors hover:bg-[#1e293b] hover:text-[#ffffff]"
                  aria-label="Undo my changes"
                >
                  <RotateCcw className="size-3.5" aria-hidden="true" />
                  Reset
                </button>
              )}
              <button
                type="button"
                onClick={() => setEditing((e) => !e)}
                className={cn(
                  'inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors hover:bg-[#1e293b] hover:text-[#ffffff]',
                  editing ? 'bg-[#1e293b] text-[#ffffff]' : 'text-[#cbd5e1]',
                )}
                aria-pressed={editing}
              >
                <Pencil className="size-3.5" aria-hidden="true" />
                {editing ? 'Done' : 'Edit'}
              </button>
            </>
          )}
          <button
            type="button"
            onClick={copy}
            className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-[#cbd5e1] transition-colors hover:bg-[#1e293b] hover:text-[#ffffff]"
            aria-label={copied ? 'Code copied' : 'Copy code'}
          >
            {copied ? <Check className="size-3.5 text-[#34d399]" aria-hidden="true" /> : <Copy className="size-3.5" aria-hidden="true" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
          {lesson &&
            (phase === 'running' ? (
              <button
                type="button"
                onClick={() => pythonRuntime.stop()}
                className="inline-flex items-center gap-1 rounded-md bg-[#7f1d1d] px-2.5 py-1 text-xs font-semibold text-[#ffffff] transition-colors hover:bg-[#991b1b]"
              >
                <Square className="size-3" aria-hidden="true" />
                Stop
              </button>
            ) : (
              <button
                type="button"
                onClick={() => run(false)}
                disabled={unsupported.length > 0}
                title={unsupported.length ? 'This example needs Google Colab or your own computer' : 'Run this code in your browser'}
                className="inline-flex items-center gap-1 rounded-md bg-[#0e7490] px-2.5 py-1 text-xs font-semibold text-[#ffffff] transition-colors hover:bg-[#0891b2] disabled:cursor-not-allowed disabled:bg-[#334155] disabled:text-[#94a3b8]"
              >
                <Play className="size-3" aria-hidden="true" />
                Run
              </button>
            ))}
        </div>
      </div>

      {editing ? (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          spellCheck={false}
          autoCapitalize="off"
          autoCorrect="off"
          rows={Math.min(30, Math.max(4, text.split('\n').length + 1))}
          aria-label="Edit the code"
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
              e.preventDefault()
              void run(false)
            }
            if (e.key === 'Tab') {
              e.preventDefault()
              const el = e.currentTarget
              const { selectionStart: s, selectionEnd: end } = el
              const next = text.slice(0, s) + '    ' + text.slice(end)
              setText(next)
              requestAnimationFrame(() => el.setSelectionRange(s + 4, s + 4))
            }
          }}
          className="block w-full resize-y bg-[#0b1220] p-3 font-mono text-[12.5px] leading-relaxed text-[#cffafe] outline-none focus:ring-1 focus:ring-inset focus:ring-[#0e7490] sm:p-4 sm:text-[13px]"
        />
      ) : (
        <pre className="overflow-x-auto p-3 text-[12.5px] leading-relaxed text-[#cffafe] sm:p-4 sm:text-[13px]">
          <code>{text}</code>
        </pre>
      )}

      {lesson && unsupported.length > 0 && (
        <div className="flex gap-2.5 border-t border-[#1e293b] bg-[#111a2e] px-3 py-2.5 text-xs leading-relaxed text-[#cbd5e1] sm:px-4">
          <ExternalLink className="mt-0.5 size-3.5 shrink-0 text-[#67e8f9]" aria-hidden="true" />
          <p>
            {inherited
              ? `This example builds on an earlier block that uses ${unsupported.join(' and ')}, which cannot run inside a browser.`
              : `This example uses ${unsupported.join(' and ')}, which cannot run inside a browser.`}{' '}
            {lesson.colabUrl ? (
              <>
                <a
                  href={lesson.colabUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold text-[#67e8f9] underline underline-offset-2"
                >
                  Open this lesson in Google Colab
                </a>{' '}
                (free, with a GPU): every example is there, ready to run.
              </>
            ) : (
              <>
                Copy the lesson's code into{' '}
                <a href={COLAB} target="_blank" rel="noreferrer" className="font-semibold text-[#67e8f9] underline underline-offset-2">
                  Google Colab
                </a>{' '}
                (free) or run it on your own computer.
              </>
            )}
          </p>
        </div>
      )}

      {showPanel && (
        <div className="border-t border-[#1e293b] bg-[#060b16]" aria-live="polite">
          <div className="flex items-center gap-2 px-3 pt-2 text-[11px] font-semibold uppercase tracking-wider text-[#64748b] sm:px-4">
            <TerminalSquare className="size-3.5" aria-hidden="true" />
            Output
            {phase === 'done' && result && result.seconds > 0 && (
              <span className="ml-auto normal-case tracking-normal text-[#475569]">{result.seconds.toFixed(2)} s</span>
            )}
          </div>
          {phase === 'running' && !output && (
            <p className="flex items-center gap-2 px-3 py-2.5 text-xs text-[#94a3b8] sm:px-4">
              <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
              {prep ?? statusMessage ?? 'Running…'}
              {/Starting/.test(statusMessage ?? '') && (
                <span className="text-[#64748b]">(the first time takes 10–30 seconds)</span>
              )}
            </p>
          )}
          {output && (
            <pre className="max-h-96 overflow-auto whitespace-pre px-3 py-2 font-mono text-[12.5px] leading-relaxed text-[#e2e8f0] sm:px-4">
              {output}
            </pre>
          )}
          {result?.value && (
            <pre className="max-h-96 overflow-auto whitespace-pre px-3 py-2 font-mono text-[12.5px] leading-relaxed text-[#a5f3fc] sm:px-4">
              {result.value}
            </pre>
          )}
          {result?.images.map((src, i) => (
            <div key={i} className="px-3 py-2 sm:px-4">
              <img src={src} alt={`Chart ${i + 1} made by the code`} className="max-w-full rounded-lg bg-white" />
            </div>
          ))}
          {result?.error && (
            <div className="mx-3 mb-3 mt-1 rounded-lg border border-[#7f1d1d] bg-[#1f0a0a] p-3 sm:mx-4">
              <p className="flex items-center gap-1.5 text-xs font-semibold text-[#fca5a5]">
                <AlertTriangle className="size-3.5" aria-hidden="true" />
                The code stopped with an error
              </p>
              <pre className="mt-1.5 overflow-x-auto whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-[#fecaca]">
                {result.error}
              </pre>
              {result.nameError && index > 0 && (
                <div className="mt-2.5 flex flex-wrap items-center gap-2 text-xs text-[#cbd5e1]">
                  <span>This block probably uses something made in an earlier block.</span>
                  <button
                    type="button"
                    onClick={() => run(true)}
                    className="inline-flex items-center gap-1 rounded-md bg-[#0e7490] px-2.5 py-1 font-semibold text-[#ffffff] hover:bg-[#0891b2]"
                  >
                    <Play className="size-3" aria-hidden="true" />
                    Run the earlier blocks first
                  </button>
                </div>
              )}
            </div>
          )}
          {phase === 'done' && result?.ok && !output && !result.value && result.images.length === 0 && (
            <p className="px-3 py-2.5 text-xs text-[#64748b] sm:px-4">Done. This block prints nothing; it prepares things for the next blocks.</p>
          )}
        </div>
      )}
    </div>
  )
}
