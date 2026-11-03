import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Exam-screen watcher.
 *
 * A web page cannot stop a student from switching tabs or apps, but it can
 * notice. While `active`, this hook watches for the three ways of leaving the
 * exam screen:
 *
 *  * the tab is hidden (another tab, another app, the phone's home screen),
 *  * the window loses focus (another window or a pop-up appears on top),
 *  * full screen is closed (Esc, F11, swipe).
 *
 * One "leave" is counted per episode: after the first signal, further signals
 * are ignored until the student comes back and presses "Return to the exam"
 * (`acknowledge`). Copy, paste, right-click and print-screen are blocked and
 * reported as `notice` (logged, not counted).
 *
 * Full screen is requested on the whole document, so dialogs rendered in a
 * portal stay visible. Where the browser has no full-screen support (iPhone
 * Safari), the other two signals still work.
 */
export interface ProctorOptions {
  active: boolean
  onLeave: (detail: string) => void
  onNotice: (detail: string) => void
}

export function fullscreenSupported(): boolean {
  return typeof document !== 'undefined' && Boolean(document.documentElement.requestFullscreen) && document.fullscreenEnabled !== false
}

export async function enterFullscreen(): Promise<boolean> {
  if (!fullscreenSupported()) return false
  if (document.fullscreenElement) return true
  try {
    await document.documentElement.requestFullscreen({ navigationUI: 'hide' })
    return true
  } catch {
    return false
  }
}

export async function exitFullscreen(): Promise<void> {
  if (document.fullscreenElement && document.exitFullscreen) {
    try {
      await document.exitFullscreen()
    } catch {
      // already out
    }
  }
}

export function useProctor({ active, onLeave, onNotice }: ProctorOptions) {
  const [away, setAway] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(() => Boolean(document.fullscreenElement))
  const awayRef = useRef(false)
  // Ignore signals for a moment after (re)starting: entering full screen can
  // itself fire focus/resize events on some browsers.
  const quietUntil = useRef(0)
  const lastNotice = useRef(0)
  const leaveRef = useRef(onLeave)
  const noticeRef = useRef(onNotice)
  leaveRef.current = onLeave
  noticeRef.current = onNotice

  // A hidden tab is never caused by our own full-screen switch, so it always
  // counts; the short quiet time only applies to focus and full-screen signals.
  const leave = useCallback((detail: string, always = false) => {
    if (awayRef.current || (!always && Date.now() < quietUntil.current)) return
    awayRef.current = true
    setAway(true)
    leaveRef.current(detail)
  }, [])

  const notice = useCallback((detail: string) => {
    const now = Date.now()
    if (now - lastNotice.current < 3000) return
    lastNotice.current = now
    noticeRef.current(detail)
  }, [])

  /** The student is back: clear the episode and try to restore full screen. */
  const acknowledge = useCallback(async () => {
    quietUntil.current = Date.now() + 1500
    await enterFullscreen()
    awayRef.current = false
    setAway(false)
  }, [])

  const pause = useCallback((ms = 1500) => {
    quietUntil.current = Date.now() + ms
  }, [])

  useEffect(() => {
    if (!active) return
    quietUntil.current = Date.now() + 1500

    const onVisibility = () => {
      if (document.visibilityState === 'hidden') leave('tab_hidden', true)
    }
    const onBlur = () => leave('window_blur')
    const onFullscreen = () => {
      const fs = Boolean(document.fullscreenElement)
      setIsFullscreen(fs)
      if (!fs && fullscreenSupported()) leave('fullscreen_exit')
    }
    const block = (detail: string) => (e: Event) => {
      e.preventDefault()
      notice(detail)
    }
    const onCopy = block('copy')
    const onCut = block('cut')
    const onPaste = (e: ClipboardEvent) => {
      // Pasting into a fill-in answer is blocked too: answers must be typed.
      e.preventDefault()
      notice('paste')
    }
    const onContext = block('right_click')
    const onKey = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase()
      if (key === 'printscreen') {
        notice('print_screen')
        return
      }
      if ((e.ctrlKey || e.metaKey) && ['c', 'x', 'v', 'p', 's', 'u', 'a'].includes(key)) {
        e.preventDefault()
        notice(`shortcut_${key}`)
      }
    }
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = ''
    }

    document.addEventListener('visibilitychange', onVisibility)
    window.addEventListener('blur', onBlur)
    document.addEventListener('fullscreenchange', onFullscreen)
    document.addEventListener('copy', onCopy)
    document.addEventListener('cut', onCut)
    document.addEventListener('paste', onPaste)
    document.addEventListener('contextmenu', onContext)
    document.addEventListener('keydown', onKey)
    window.addEventListener('beforeunload', onBeforeUnload)
    return () => {
      document.removeEventListener('visibilitychange', onVisibility)
      window.removeEventListener('blur', onBlur)
      document.removeEventListener('fullscreenchange', onFullscreen)
      document.removeEventListener('copy', onCopy)
      document.removeEventListener('cut', onCut)
      document.removeEventListener('paste', onPaste)
      document.removeEventListener('contextmenu', onContext)
      document.removeEventListener('keydown', onKey)
      window.removeEventListener('beforeunload', onBeforeUnload)
    }
  }, [active, leave, notice])

  return { away, isFullscreen, acknowledge, pause }
}

export const LEAVE_REASONS: Record<string, string> = {
  tab_hidden: 'You switched to another tab or app.',
  window_blur: 'Another window or a pop-up took focus from the exam.',
  fullscreen_exit: 'You left full-screen mode.',
  page_reload: 'The exam page was reloaded or closed.',
}

export const NOTICE_TEXT: Record<string, string> = {
  copy: 'Copying is turned off during the exam.',
  cut: 'Cutting text is turned off during the exam.',
  paste: 'Pasting is turned off during the exam. Type your answer.',
  right_click: 'Right-click is turned off during the exam.',
  print_screen: 'Screenshots are not allowed during the exam.',
}
