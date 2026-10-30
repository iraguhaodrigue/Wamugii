import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, Award, BookOpen, GraduationCap, Layers, Sparkles } from 'lucide-react'
import { listPublicCourses } from '@/api/courses'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { cn } from '@/utils/cn'
import { SectionHeading } from './SectionHeading'
import { ProgramArt, type ProgramArtKind } from './ProgramArt'

/**
 * Homepage section: the whole WAMUGII AI Program as an ordered learning
 * track — a stepper with a travelling pulse, then one card per course, each
 * with its own animated illustration.
 *
 * Course order, copy and art live here; the lesson count is taken from the
 * live catalogue when it has loaded (the same cached query the Courses page
 * uses), so adding a lesson in the admin panel updates the homepage too.
 */
interface ProgramCourse {
  slug: string
  title: string
  summary: string
  level: 'Beginner' | 'Intermediate' | 'Advanced' | 'Capstone'
  lessons: number
  art: ProgramArtKind
  /** Card accent: label text, top glow and hover ring. */
  accent: { text: string; glow: string; ring: string; dot: string }
}

const ACCENTS = {
  cyan: { text: 'text-cyan-500', glow: 'from-cyan-500/30', ring: 'hover:ring-cyan-400/50', dot: 'bg-cyan-400' },
  violet: { text: 'text-violet-500', glow: 'from-violet-500/30', ring: 'hover:ring-violet-400/50', dot: 'bg-violet-400' },
  emerald: { text: 'text-emerald-500', glow: 'from-emerald-500/30', ring: 'hover:ring-emerald-400/50', dot: 'bg-emerald-400' },
  fuchsia: { text: 'text-fuchsia-500', glow: 'from-fuchsia-500/30', ring: 'hover:ring-fuchsia-400/50', dot: 'bg-fuchsia-400' },
  pink: { text: 'text-pink-500', glow: 'from-pink-500/30', ring: 'hover:ring-pink-400/50', dot: 'bg-pink-400' },
  amber: { text: 'text-amber-500', glow: 'from-amber-500/30', ring: 'hover:ring-amber-400/50', dot: 'bg-amber-400' },
  green: { text: 'text-green-500', glow: 'from-green-500/30', ring: 'hover:ring-green-400/50', dot: 'bg-green-400' },
}

const PROGRAM: ProgramCourse[] = [
  {
    slug: 'ai-career-essentials',
    title: 'AI Career Essentials',
    summary: 'Use AI tools well, write strong prompts and grow your career. No coding needed.',
    level: 'Beginner',
    lessons: 7,
    art: 'career',
    accent: ACCENTS.cyan,
  },
  {
    slug: 'ai-foundations',
    title: 'AI Foundations',
    summary: 'What AI really is: agents, problem types, how machines learn, data and ethics.',
    level: 'Beginner',
    lessons: 9,
    art: 'foundations',
    accent: ACCENTS.violet,
  },
  {
    slug: 'math-python-for-ai',
    title: 'Math & Python for AI',
    summary: 'The Python, NumPy, linear algebra, calculus and statistics that AI is built on.',
    level: 'Beginner',
    lessons: 9,
    art: 'mathpython',
    accent: ACCENTS.emerald,
  },
  {
    slug: 'machine-learning-fundamentals',
    title: 'Machine Learning Fundamentals',
    summary: 'Regression, classification, trees and clustering, trained and tested the right way.',
    level: 'Intermediate',
    lessons: 9,
    art: 'ml',
    accent: ACCENTS.fuchsia,
  },
  {
    slug: 'deep-learning-neural-networks',
    title: 'Deep Learning & Neural Networks',
    summary: 'How neural networks learn, plus CNNs for images and sequence models.',
    level: 'Intermediate',
    lessons: 9,
    art: 'deep',
    accent: ACCENTS.pink,
  },
  {
    slug: 'modern-ai-llms-generative',
    title: 'Modern AI: LLMs & Generative AI',
    summary: 'Transformers, large language models, prompting, RAG and AI agents.',
    level: 'Advanced',
    lessons: 9,
    art: 'llm',
    accent: ACCENTS.amber,
  },
  {
    slug: 'responsible-ai-deployment',
    title: 'Responsible AI & Deployment',
    summary: 'Fairness, safety and privacy, then ship a real AI app in your capstone project.',
    level: 'Capstone',
    lessons: 8,
    art: 'deploy',
    accent: ACCENTS.green,
  },
]

const LEVEL_STYLE: Record<ProgramCourse['level'], string> = {
  Beginner: 'bg-emerald-500/10 text-emerald-600',
  Intermediate: 'bg-sky-500/10 text-sky-600',
  Advanced: 'bg-violet-500/10 text-violet-600',
  Capstone: 'bg-amber-500/15 text-amber-600',
}

function ProgramTrack() {
  return (
    <Reveal className="relative mx-auto mt-12 hidden max-w-4xl sm:block">
      <div className="absolute left-[7%] right-[7%] top-5 h-0.5 overflow-hidden rounded bg-slate-200">
        <span className="pa-track-pulse absolute inset-y-0 w-24 bg-gradient-to-r from-transparent via-cyan-400 to-transparent" />
      </div>
      <ol className="relative grid grid-cols-7">
        {PROGRAM.map((c, i) => (
          <li key={c.slug} className="flex flex-col items-center text-center">
            <a
              href={`#program-${c.slug}`}
              onClick={(e) => {
                e.preventDefault()
                document.getElementById(`program-${c.slug}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
              }}
              className="group flex size-10 items-center justify-center rounded-full border-2 border-slate-200 bg-panel text-sm font-bold text-slate-700 transition-transform duration-300 hover:scale-110"
              aria-label={`Course ${i + 1}: ${c.title}`}
            >
              <span className={cn('pa-track-node flex size-6 items-center justify-center rounded-full text-[11px] text-white', c.accent.dot)} style={{ animationDelay: `${i * 0.6}s` }}>
                {i + 1}
              </span>
            </a>
            <span className="mt-2 hidden text-[11px] font-medium leading-tight text-slate-500 md:block">{c.title.replace(/ \(.*\)$/, '').split(':')[0]}</span>
          </li>
        ))}
      </ol>
    </Reveal>
  )
}

export function AIProgram() {
  const { data } = useQuery({ queryKey: ['courses', 'public'], queryFn: () => listPublicCourses() })
  const live = new Map((data ?? []).map((c) => [c.slug, c]))
  const courses = PROGRAM.map((c) => ({ ...c, lessons: live.get(c.slug)?.lesson_count || c.lessons }))
  const totalLessons = courses.reduce((sum, c) => sum + c.lessons, 0)

  const stats = [
    { icon: GraduationCap, label: `${courses.length} courses` },
    { icon: BookOpen, label: `${totalLessons} lessons` },
    { icon: Layers, label: 'Beginner to advanced' },
    { icon: Award, label: 'Certificate for each' },
  ]

  return (
    <section id="ai-program" className="relative overflow-hidden py-20 sm:py-24">
      <div className="dot-texture pointer-events-none absolute inset-0 opacity-60" aria-hidden="true" />
      <Container className="relative">
        <SectionHeading
          label="WAMUGII AI Program"
          title="Learn AI step by step, from your first prompt to a live AI app"
          description="Seven connected courses in simple English. Start free today and earn a certificate for every course you finish."
        />
        <Reveal className="mt-8 flex flex-wrap justify-center gap-2.5">
          {stats.map(({ icon: Icon, label }) => (
            <span key={label} className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-panel px-3.5 py-1.5 text-sm font-medium text-slate-700 shadow-[var(--shadow-card)]">
              <Icon className="size-4 text-brand-500" aria-hidden="true" />
              {label}
            </span>
          ))}
        </Reveal>

        <ProgramTrack />

        <div className="mt-12 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {courses.map((c, i) => (
            <Reveal key={c.slug} delay={(i % 4) * 90} className={cn(i === 0 && 'md:col-span-2')}>
              <Link
                id={`program-${c.slug}`}
                to={paths.courseDetail(c.slug)}
                className={cn(
                  'group flex h-full scroll-mt-28 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-panel shadow-[var(--shadow-card)] ring-1 ring-transparent transition-[transform,box-shadow] duration-300 hover:-translate-y-1.5 hover:shadow-[var(--shadow-glow-brand)]',
                  c.accent.ring,
                )}
              >
                <div className={cn('relative overflow-hidden bg-[#06131c]', i === 0 ? 'h-44 sm:h-52' : 'h-44')}>
                  <div className={cn('pointer-events-none absolute inset-0 bg-gradient-to-b to-transparent', c.accent.glow)} aria-hidden="true" />
                  <div className="tech-grid pointer-events-none absolute inset-0 opacity-[0.05]" aria-hidden="true" />
                  <div className="relative h-full p-2 transition-transform duration-500 group-hover:scale-[1.04]">
                    <ProgramArt kind={c.art} />
                  </div>
                  <span className="absolute left-3 top-3 rounded-full bg-black/40 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider text-white backdrop-blur-sm">
                    Course {i + 1}
                  </span>
                  {i === 0 && (
                    <span className="absolute right-3 top-3 inline-flex items-center gap-1 rounded-full bg-cyan-400 px-2.5 py-1 text-[11px] font-bold text-cyan-950">
                      <Sparkles className="size-3" aria-hidden="true" />
                      Start here
                    </span>
                  )}
                </div>
                <div className="flex flex-1 flex-col p-5">
                  <div className="flex items-center gap-2">
                    <span className={cn('rounded-full px-2 py-0.5 text-[11px] font-semibold', LEVEL_STYLE[c.level])}>{c.level}</span>
                    <span className="text-xs text-slate-400">· {c.lessons} lessons · Free</span>
                  </div>
                  <h3 className="mt-3 text-lg font-bold leading-snug text-slate-900">{c.title}</h3>
                  <p className="mt-1.5 flex-1 text-sm leading-relaxed text-slate-500">{c.summary}</p>
                  <span className={cn('mt-4 inline-flex items-center gap-1.5 text-sm font-semibold', c.accent.text)}>
                    {i === 0 ? 'Start learning free' : 'View course'}
                    <ArrowRight className="size-4 transition-transform duration-300 group-hover:translate-x-1" aria-hidden="true" />
                  </span>
                </div>
              </Link>
            </Reveal>
          ))}
        </div>

        <Reveal className="mt-12">
          <div className="shine relative flex flex-col items-center justify-between gap-5 overflow-hidden rounded-2xl bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] p-6 text-center sm:flex-row sm:p-8 sm:text-left">
            <div>
              <p className="text-xl font-bold text-white">Ready to start your AI journey?</p>
              <p className="mt-1 text-sm text-white/80">Create a free account, enroll in Course 1 and finish your first lesson today.</p>
            </div>
            <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
              <Link
                to={paths.register}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-white px-5 text-sm font-semibold text-[#0b1120] transition-transform hover:-translate-y-0.5"
              >
                Create free account
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
              <Link
                to={paths.courses}
                className="inline-flex h-11 items-center justify-center rounded-lg border border-white/40 px-5 text-sm font-semibold text-white transition-colors hover:bg-white/10"
              >
                Browse all courses
              </Link>
            </div>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
