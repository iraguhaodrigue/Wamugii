import { lazy, type ComponentType } from 'react'

const RELOAD_FLAG = 'wamugii_chunk_reload'

/**
 * Load a page's code the first time it is opened.
 *
 * After a new deploy, a visitor who still has the old page open asks for code
 * files that no longer exist. Instead of a blank screen, reload once to get
 * the new version (the flag stops an endless reload loop).
 */
async function loadWithRetry<M>(load: () => Promise<M>): Promise<M> {
  try {
    const module = await load()
    try {
      sessionStorage.removeItem(RELOAD_FLAG)
    } catch {
      // storage unavailable: nothing to clear
    }
    return module
  } catch (error) {
    let alreadyReloaded = false
    try {
      alreadyReloaded = sessionStorage.getItem(RELOAD_FLAG) === '1'
      if (!alreadyReloaded) sessionStorage.setItem(RELOAD_FLAG, '1')
    } catch {
      alreadyReloaded = true // cannot remember, so do not risk a loop
    }
    if (!alreadyReloaded) {
      window.location.reload()
      return new Promise<M>(() => {}) // the page is reloading
    }
    throw error
  }
}

/** A lazily loaded component from a module's named export. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function lazyNamed<M extends Record<K, ComponentType<any>>, K extends keyof M>(
  load: () => Promise<M>,
  name: K,
) {
  return lazy(async () => ({ default: (await loadWithRetry(load))[name] }))
}

/** A lazily loaded component from a module's default export. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function lazyDefault<T extends ComponentType<any>>(load: () => Promise<{ default: T }>) {
  return lazy(() => loadWithRetry(load))
}
