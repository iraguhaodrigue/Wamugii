import { useEffect, useRef } from 'react'
import { cn } from '@/utils/cn'

export type TechBackgroundIntensity = 'hero' | 'cta' | 'medium' | 'subtle'

export interface AnimatedTechBackgroundProps {
  intensity?: TechBackgroundIntensity
  className?: string
}

interface Preset {
  particlesDesktop: number
  particlesMobile: number
  linkDistance: number
  streaks: 0 | 1 | 2
  gridOpacity: number
  speed: number
}

const PRESETS: Record<TechBackgroundIntensity, Preset> = {
  hero: { particlesDesktop: 68, particlesMobile: 24, linkDistance: 150, streaks: 2, gridOpacity: 0.05, speed: 1 },
  cta: { particlesDesktop: 48, particlesMobile: 18, linkDistance: 130, streaks: 2, gridOpacity: 0.045, speed: 0.9 },
  medium: { particlesDesktop: 34, particlesMobile: 14, linkDistance: 115, streaks: 1, gridOpacity: 0.035, speed: 0.75 },
  subtle: { particlesDesktop: 20, particlesMobile: 8, linkDistance: 95, streaks: 0, gridOpacity: 0.025, speed: 0.6 },
}

// Mirrors --color-brand-400 / --color-accent-400 in index.css — those two
// tokens are intentionally constant across light/dark, so hardcoding them
// here avoids a getComputedStyle readback for a value that never changes.
const BRAND_RGB: [number, number, number] = [34, 211, 238]
const ACCENT_RGB: [number, number, number] = [167, 139, 250]

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  r: number
  phase: number
  color: [number, number, number]
}

/**
 * Decorative particle-network canvas + CSS grid/light-streak layers, used
 * behind Hero/Services/Technology/CTA sections on the public site. Always
 * `aria-hidden` and `pointer-events-none` — never intercepts clicks/scroll.
 * Pauses its own rAF loop when off-screen or the tab is hidden, and skips
 * animation entirely under `prefers-reduced-motion: reduce` (drawing one
 * static frame instead).
 */
export function AnimatedTechBackground({ intensity = 'medium', className }: AnimatedTechBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const parent = canvas?.parentElement
    if (!canvas || !parent) return

    const ctx = canvas.getContext('2d', { alpha: true })
    if (!ctx) return

    const preset = PRESETS[intensity]
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    let width = 0
    let height = 0
    let dpr = Math.min(window.devicePixelRatio || 1, 2)
    let particles: Particle[] = []
    let rafId = 0
    let running = true
    let inView = true

    function seed() {
      const isMobile = width < 640
      const count = isMobile ? preset.particlesMobile : preset.particlesDesktop
      particles = Array.from({ length: count }, () => {
        const isAccent = Math.random() < 0.3
        return {
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.12 * preset.speed,
          vy: (Math.random() - 0.5) * 0.12 * preset.speed,
          r: Math.random() * 1.3 + 0.6,
          phase: Math.random() * Math.PI * 2,
          color: isAccent ? ACCENT_RGB : BRAND_RGB,
        }
      })
    }

    function resize() {
      width = parent!.clientWidth
      height = parent!.clientHeight
      dpr = Math.min(window.devicePixelRatio || 1, 2)
      canvas!.width = Math.max(1, Math.round(width * dpr))
      canvas!.height = Math.max(1, Math.round(height * dpr))
      ctx!.setTransform(dpr, 0, 0, dpr, 0, 0)
      seed()
    }

    function drawFrame(t: number) {
      ctx!.clearRect(0, 0, width, height)

      if (!reduceMotion) {
        for (const p of particles) {
          p.x += p.vx
          p.y += p.vy
          if (p.x < -20) p.x = width + 20
          else if (p.x > width + 20) p.x = -20
          if (p.y < -20) p.y = height + 20
          else if (p.y > height + 20) p.y = -20
        }
      }

      for (let i = 0; i < particles.length; i++) {
        const a = particles[i]
        if (!a) continue
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j]
          if (!b) continue
          const dx = a.x - b.x
          const dy = a.y - b.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < preset.linkDistance) {
            const alpha = (1 - dist / preset.linkDistance) * 0.14
            ctx!.strokeStyle = `rgba(${a.color[0]}, ${a.color[1]}, ${a.color[2]}, ${alpha})`
            ctx!.lineWidth = 1
            ctx!.beginPath()
            ctx!.moveTo(a.x, a.y)
            ctx!.lineTo(b.x, b.y)
            ctx!.stroke()
          }
        }
      }

      for (const p of particles) {
        const pulse = reduceMotion ? 0.7 : 0.55 + Math.sin(t / 1400 + p.phase) * 0.25
        ctx!.beginPath()
        ctx!.fillStyle = `rgba(${p.color[0]}, ${p.color[1]}, ${p.color[2]}, ${0.55 * pulse})`
        ctx!.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx!.fill()
      }
    }

    function loop(t: number) {
      if (running && inView) drawFrame(t)
      rafId = requestAnimationFrame(loop)
    }

    resize()
    drawFrame(0)

    const resizeObserver = new ResizeObserver(() => resize())
    resizeObserver.observe(parent)

    const intersectionObserver = new IntersectionObserver(
      ([entry]) => {
        inView = entry?.isIntersecting ?? true
      },
      { threshold: 0 },
    )
    intersectionObserver.observe(canvas)

    function handleVisibility() {
      running = document.visibilityState === 'visible'
    }
    document.addEventListener('visibilitychange', handleVisibility)

    if (!reduceMotion) {
      rafId = requestAnimationFrame(loop)
    }

    return () => {
      running = false
      if (rafId) cancelAnimationFrame(rafId)
      resizeObserver.disconnect()
      intersectionObserver.disconnect()
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [intensity])

  const preset = PRESETS[intensity]

  return (
    <div className={cn('pointer-events-none absolute inset-0 overflow-hidden', className)} aria-hidden="true">
      <div className="tech-grid absolute inset-0" style={{ opacity: preset.gridOpacity }} />
      {preset.streaks >= 1 && <div className="tech-streak tech-streak-a" style={{ left: '18%' }} />}
      {preset.streaks >= 2 && <div className="tech-streak tech-streak-accent tech-streak-b" style={{ left: '62%' }} />}
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" />
    </div>
  )
}
