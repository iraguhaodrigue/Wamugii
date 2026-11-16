/**
 * Runs lesson Python code inside the student's browser with Pyodide
 * (CPython compiled to WebAssembly). Nothing is sent to our server.
 *
 *  * Python runs in a Web Worker, so the page never freezes; "Stop" simply
 *    ends the worker and starts a fresh one.
 *  * Each lesson gets its own namespace ("session"), like one notebook per
 *    lesson: a later code block can use variables from an earlier one.
 *  * Packages (numpy, pandas, scikit-learn, matplotlib, scipy…) are loaded
 *    the first time a block imports them. Matplotlib charts come back as images.
 *
 * Pyodide is loaded from jsDelivr by default. Set VITE_PYODIDE_URL to serve it
 * from your own server instead (must end with a slash).
 */

export const PYODIDE_URL: string = (
  (import.meta.env.VITE_PYODIDE_URL as string | undefined) || 'https://cdn.jsdelivr.net/pyodide/v0.29.4/full/'
).replace(/\/?$/, '/')

export type RuntimeStatus = 'off' | 'starting' | 'ready' | 'running' | 'failed'

export interface RunResult {
  ok: boolean
  /** Text printed by the code (stdout and stderr, in order). */
  output: string
  /** repr() of the last expression, when it is not None (like a notebook). */
  value: string | null
  /** Error message, already trimmed to the parts a student needs. */
  error: string | null
  /** PNG data URLs for matplotlib figures the code created. */
  images: string[]
  /** True when the error is a NameError, usually because an earlier block was not run. */
  nameError: boolean
  /** Seconds the code took (without loading time). */
  seconds: number
}

type Listener = (status: RuntimeStatus, message: string) => void

// Libraries that cannot run inside a browser tab. Lessons that use them are
// meant for Google Colab or the student's own computer.
const UNSUPPORTED: Record<string, string> = {
  torch: 'PyTorch',
  torchvision: 'PyTorch',
  transformers: 'Hugging Face Transformers',
  anthropic: 'the Anthropic SDK (it needs an API key and the internet)',
  openai: 'the OpenAI SDK (it needs an API key and the internet)',
  google: 'the Google AI SDK (it needs an API key and the internet)',
  fastapi: 'FastAPI (it runs a web server)',
  uvicorn: 'a web server',
  subprocess: 'running other programs',
  requests: 'internet requests',
  ollama: 'Ollama (it runs on your computer)',
}

/** Top-level module names a block imports ("import a, b.c as d" gives a and b). */
function importedModules(code: string): string[] {
  const out: string[] = []
  for (const m of code.matchAll(/^\s*import\s+([^\n#]+)/gm)) {
    for (const part of m[1]!.split(',')) {
      const name = part.trim().split(/\s+/)[0]?.split('.')[0]
      if (name) out.push(name)
    }
  }
  for (const m of code.matchAll(/^\s*from\s+([A-Za-z_]\w*)/gm)) out.push(m[1]!)
  return out
}

/** Names of libraries in `code` that the browser cannot run, for a friendly message. */
export function unsupportedImports(code: string): string[] {
  const found = new Set<string>()
  for (const mod of importedModules(code)) {
    const lib = UNSUPPORTED[mod]
    if (lib) found.add(lib)
  }
  return [...found]
}

/** Names a block creates at the top level: variables, functions, classes, imports. */
function definedNames(code: string): Set<string> {
  const names = new Set<string>()
  const add = (s: string) => {
    const n = s.trim().replace(/^\*/, '')
    if (/^[A-Za-z_]\w*$/.test(n)) names.add(n)
  }
  for (const m of code.matchAll(/^(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)/gm)) add(m[1]!)
  for (const m of code.matchAll(/^import\s+([^\n#]+)/gm)) {
    for (const part of m[1]!.split(',')) {
      const bits = part.trim().split(/\s+as\s+/)
      add(bits[1] ?? bits[0]!.split('.')[0]!)
    }
  }
  for (const m of code.matchAll(/^from\s+\S+\s+import\s+\(?([^\n#)]+)/gm)) {
    for (const part of m[1]!.split(',')) {
      const bits = part.trim().split(/\s+as\s+/)
      add(bits[1] ?? bits[0]!)
    }
  }
  for (const m of code.matchAll(/^\(?([A-Za-z_][\w\s,()*]*?)\)?\s*(?:[+\-*/]?=)(?!=)/gm)) {
    for (const part of m[1]!.replace(/[()]/g, '').split(',')) add(part)
  }
  for (const m of code.matchAll(/^for\s+([\w\s,()]+?)\s+in\s/gm)) {
    for (const part of m[1]!.replace(/[()]/g, '').split(',')) add(part)
  }
  for (const m of code.matchAll(/^with\s.+\sas\s+([A-Za-z_]\w*)/gm)) add(m[1]!)
  return names
}

/**
 * For every Python block in a lesson, the reason it cannot run in the browser,
 * or null when it can. A block is "Colab only" when it imports an unsupported
 * library itself, or when it uses something (a model, a client, a helper
 * function) that an earlier Colab-only block created.
 */
export function colabOnlyReasons(codes: string[]): (string[] | null)[] {
  const tainted = new Map<string, string[]>()
  return codes.map((code) => {
    const own = unsupportedImports(code)
    const defined = definedNames(code)
    let reasons = own
    if (!reasons.length) {
      const borrowed = new Set<string>()
      for (const [name, libs] of tainted) {
        if (defined.has(name)) continue
        if (new RegExp(`(^|[^\\w.])${name}\\b`).test(code)) libs.forEach((l) => borrowed.add(l))
      }
      reasons = [...borrowed]
    }
    if (reasons.length) {
      defined.forEach((n) => tainted.set(n, reasons))
      return reasons
    }
    // A supported block that redefines a name makes it usable again.
    defined.forEach((n) => tainted.delete(n))
    return null
  })
}

const WORKER_SOURCE = (baseUrl: string) => `
importScripts(${JSON.stringify(baseUrl + 'pyodide.js')});
let py = null;
let current = null;
const spaces = new Map();
const MAX_OUT = 200000;
let outSize = 0;
const decoder = new TextDecoder();
function send(msg) { postMessage(msg); }
function emit(kind, text) {
  if (current === null) return;
  if (outSize > MAX_OUT) return;
  outSize += text.length;
  if (outSize > MAX_OUT) text = text + "\\n… output cut off (too long)\\n";
  send({ type: 'out', id: current, kind, text });
}
const SETUP = \`
import os, sys, builtins, warnings, io, base64
os.environ["MPLBACKEND"] = "AGG"
warnings.filterwarnings("ignore", message=".*non-interactive.*")
warnings.filterwarnings("ignore", message=".*FigureCanvasAgg.*")
def _no_input(*args, **kwargs):
    raise RuntimeError("input() cannot be used in the browser. Put the value straight into the code instead, for example name = 'Aline'.")
builtins.input = _no_input
def _wamugii_figures():
    plt = sys.modules.get("matplotlib.pyplot")
    if plt is None:
        return []
    out = []
    for num in plt.get_fignums():
        buf = io.BytesIO()
        plt.figure(num).savefig(buf, format="png", dpi=110, bbox_inches="tight")
        out.append("data:image/png;base64," + base64.b64encode(buf.getvalue()).decode())
    plt.close("all")
    return out
\`;
async function start() {
  send({ type: 'status', status: 'starting', message: 'Starting Python in your browser…' });
  py = await loadPyodide({ indexURL: ${JSON.stringify(baseUrl)} });
  const sink = (kind) => ({ write: (buf) => { emit(kind, decoder.decode(buf)); return buf.length; } });
  py.setStdout(sink('stdout'));
  py.setStderr(sink('stderr'));
  await py.runPythonAsync(SETUP);
  send({ type: 'status', status: 'ready', message: 'Python is ready' });
}
const ready = start().catch((e) => {
  send({ type: 'status', status: 'failed', message: String(e && e.message || e) });
  throw e;
});
function space(sid) {
  if (!spaces.has(sid)) {
    const d = py.globals.get('dict')();
    d.set('__name__', '__main__');
    spaces.set(sid, d);
  }
  return spaces.get(sid);
}
onmessage = async (ev) => {
  const { id, sid, code } = ev.data;
  try { await ready; } catch (e) {
    send({ type: 'done', id, ok: false, error: 'Python could not start: ' + String(e && e.message || e), images: [], value: null, seconds: 0 });
    return;
  }
  current = id; outSize = 0;
  let ok = true, error = null, value = null, images = [];
  try {
    await py.loadPackagesFromImports(code, {
      messageCallback: (m) => { if (/^Loading /.test(m)) send({ type: 'status', status: 'running', message: m.replace(/^Loading /, 'Installing ') }); },
      errorCallback: () => {},
    });
    const t0 = performance.now();
    send({ type: 'status', status: 'running', message: 'Running…' });
    let result;
    try {
      result = await py.runPythonAsync(code, { globals: space(sid) });
    } finally {
      ev.data.t = (performance.now() - t0) / 1000;
    }
    if (result !== undefined && result !== null) {
      try { value = py.globals.get('repr')(result); } catch (e) { value = String(result); }
      if (result && typeof result.destroy === 'function') result.destroy();
    }
  } catch (e) {
    ok = false;
    error = String(e && e.message || e);
  }
  try {
    const figs = py.globals.get('_wamugii_figures')();
    images = figs.toJs();
    figs.destroy();
  } catch (e) {}
  current = null;
  send({ type: 'done', id, ok, error, value, images, seconds: ev.data.t || 0 });
  send({ type: 'status', status: 'ready', message: 'Python is ready' });
};
`

/** Keep only the lines of a Python traceback that help a student. */
export function tidyError(raw: string): string {
  if (/does not support processes/.test(raw)) {
    return 'This example starts another program (for example pytest or a server). A browser cannot do that, so run this block on your own computer or in Google Colab.'
  }
  const lines = raw.replace(/\r/g, '').split('\n')
  const start = lines.findIndex((l) => l.startsWith('Traceback'))
  const body = start >= 0 ? lines.slice(start + 1) : lines
  const kept: string[] = []
  let skip = false
  for (const line of body) {
    if (/^\s*File "\/lib\/python|^\s*File "<exec>"|_pyodide|pyodide\/|\^{3,}/.test(line)) {
      skip = /File "\/lib\/python|_pyodide|pyodide\//.test(line)
      if (/File "<exec>"/.test(line)) {
        kept.push(line.replace('"<exec>"', 'your code'))
        skip = false
      }
      continue
    }
    if (skip && /^\s{4}/.test(line)) continue
    skip = false
    if (line.trim()) kept.push(line)
  }
  return (kept.length ? kept : lines).join('\n').trim()
}

interface Pending {
  resolve: (r: RunResult) => void
  out: string[]
  onOutput?: (text: string) => void
}

class PythonRuntime {
  private worker: Worker | null = null
  private url: string | null = null
  private status: RuntimeStatus = 'off'
  private message = ''
  private listeners = new Set<Listener>()
  private pending = new Map<number, Pending>()
  private nextId = 1
  private queue: Promise<unknown> = Promise.resolve()

  getStatus(): { status: RuntimeStatus; message: string } {
    return { status: this.status, message: this.message }
  }

  subscribe(fn: Listener): () => void {
    this.listeners.add(fn)
    return () => this.listeners.delete(fn)
  }

  private setStatus(status: RuntimeStatus, message: string) {
    this.status = status
    this.message = message
    this.listeners.forEach((fn) => fn(status, message))
  }

  private ensureWorker(): Worker {
    if (this.worker) return this.worker
    this.url = URL.createObjectURL(new Blob([WORKER_SOURCE(PYODIDE_URL)], { type: 'text/javascript' }))
    const worker = new Worker(this.url)
    worker.onmessage = (ev: MessageEvent) => {
      const msg = ev.data as Record<string, unknown>
      if (msg.type === 'status') {
        this.setStatus(msg.status as RuntimeStatus, String(msg.message ?? ''))
      } else if (msg.type === 'out') {
        const p = this.pending.get(msg.id as number)
        if (p) {
          p.out.push(String(msg.text))
          p.onOutput?.(p.out.join(''))
        }
      } else if (msg.type === 'done') {
        const p = this.pending.get(msg.id as number)
        if (!p) return
        this.pending.delete(msg.id as number)
        const error = msg.error ? tidyError(String(msg.error)) : null
        p.resolve({
          ok: Boolean(msg.ok),
          output: p.out.join(''),
          value: (msg.value as string | null) ?? null,
          error,
          images: (msg.images as string[]) ?? [],
          nameError: Boolean(error && /NameError/.test(error)),
          seconds: Number(msg.seconds ?? 0),
        })
      }
    }
    worker.onerror = (ev) => {
      this.setStatus('failed', ev.message || 'Python could not start')
      this.failAll('Python stopped unexpectedly. Check your internet connection, then press Run again.')
      this.reset()
    }
    this.worker = worker
    this.setStatus('starting', 'Starting Python in your browser…')
    return worker
  }

  private failAll(error: string) {
    this.pending.forEach((p) =>
      p.resolve({ ok: false, output: p.out.join(''), value: null, error, images: [], nameError: false, seconds: 0 }),
    )
    this.pending.clear()
  }

  private reset() {
    this.worker?.terminate()
    this.worker = null
    if (this.url) URL.revokeObjectURL(this.url)
    this.url = null
  }

  /** Start loading Python early (for example when a lesson with code opens). */
  warmUp(): void {
    this.ensureWorker()
  }

  /** Run code in a lesson's namespace. Calls are queued, one at a time. */
  run(sessionId: string, code: string, onOutput?: (text: string) => void): Promise<RunResult> {
    const task = () =>
      new Promise<RunResult>((resolve) => {
        const worker = this.ensureWorker()
        const id = this.nextId++
        this.pending.set(id, { resolve, out: [], onOutput })
        worker.postMessage({ id, sid: sessionId, code })
      })
    const next = this.queue.then(task, task)
    this.queue = next.catch(() => undefined)
    return next
  }

  /** Stop whatever is running. Every lesson namespace is cleared. */
  stop(): void {
    this.failAll('Stopped. Python was restarted, so run the earlier blocks again if this one needs them.')
    this.reset()
    this.queue = Promise.resolve()
    this.setStatus('off', 'Stopped')
  }
}

export const pythonRuntime = new PythonRuntime()
