import { Link } from 'react-router-dom'
import { ArrowRight, Award, BookOpen, Clock, Sparkles } from 'lucide-react'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { NeuralArt } from '@/components/courses/NeuralArt'
import { AI_ESSENTIALS_SLUG, getShowcase } from '@/components/courses/courseShowcase'

/**
 * Homepage band that promotes the free AI Career Essentials course: copy and
 * calls to action beside the animated neural network, then a slow marquee of
 * the seven lessons. Static content, so the homepage makes no extra request.
 */
export function CourseSpotlight() {
  const showcase = getShowcase(AI_ESSENTIALS_SLUG)
  if (!showcase) return null
  const minutes = showcase.lessons.reduce((sum, l) => sum + l.minutes, 0)
  // Rendered twice so the marquee can loop seamlessly at -50%.
  const loop = [...showcase.lessons, ...showcase.lessons]

  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <div className="glow-pool-teal pointer-events-none absolute inset-0" aria-hidden="true" />
      <div className="glow-pool-purple pointer-events-none absolute inset-0" aria-hidden="true" />
      <Container className="relative">
        <div className="relative overflow-hidden rounded-3xl bg-[var(--color-brand-950)] px-6 py-12 sm:px-10 lg:px-14">
          <div
            className="pointer-events-none absolute inset-0 bg-cover bg-center opacity-60"
            style={{ backgroundImage: "url('/graphics/gradient-blobs.svg')" }}
            aria-hidden="true"
          />
          <div className="relative grid items-center gap-10 lg:grid-cols-2">
            <Reveal>
              <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-cyan-300">
                <Sparkles className="size-3.5" aria-hidden="true" />
                New · Free course
              </span>
              <h2 className="mt-5 text-3xl font-extrabold tracking-tight text-white sm:text-5xl">
                AI Career <span className="text-gradient-hero">Essentials</span>
              </h2>
              <p className="mt-4 max-w-lg text-base text-white/75 sm:text-lg">{showcase.tagline}</p>
              <ul className="mt-6 flex flex-wrap gap-2.5 text-sm text-white/85">
                <li className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5">
                  <BookOpen className="size-4 text-cyan-300" aria-hidden="true" />
                  {showcase.lessons.length} lessons
                </li>
                <li className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5">
                  <Clock className="size-4 text-cyan-300" aria-hidden="true" />
                  {minutes < 75 ? 'About 1 hour' : `About ${Math.round(minutes / 30) / 2} hours`}
                </li>
                <li className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5">
                  <Award className="size-4 text-cyan-300" aria-hidden="true" />
                  Certificate
                </li>
              </ul>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  to={paths.courseDetail(AI_ESSENTIALS_SLUG)}
                  className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-6 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter,transform] duration-200 hover:-translate-y-0.5 hover:brightness-110"
                >
                  Start learning free
                  <ArrowRight className="size-4" aria-hidden="true" />
                </Link>
                <Link
                  to={paths.courses}
                  className="inline-flex h-12 items-center justify-center rounded-lg border border-white/20 bg-white/5 px-6 text-sm font-semibold text-white transition-colors hover:bg-white/10"
                >
                  See the full AI Program
                </Link>
              </div>
            </Reveal>
            <Reveal delay={120} className="mx-auto w-full max-w-md">
              <NeuralArt />
            </Reveal>
          </div>

          <div className="course-marquee relative mt-12 overflow-hidden">
            <ul className="course-marquee-track flex w-max gap-3">
              {loop.map(({ title, icon: Icon }, i) => (
                <li
                  key={i}
                  aria-hidden={i >= showcase.lessons.length ? true : undefined}
                  className="flex items-center gap-2.5 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white/85"
                >
                  <span className="flex size-7 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white">
                    <Icon className="size-3.5" aria-hidden="true" />
                  </span>
                  <span className="text-xs font-semibold text-cyan-300">{(i % showcase.lessons.length) + 1}</span>
                  <span className="whitespace-nowrap font-medium">{title}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Container>
    </section>
  )
}
