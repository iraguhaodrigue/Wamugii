import {
  Briefcase,
  Brain,
  GraduationCap,
  Lightbulb,
  MessageSquareText,
  Rocket,
  ShieldCheck,
  Store,
  Users,
  Wrench,
  type LucideIcon,
} from 'lucide-react'

/**
 * Extra, presentation-only content for a course's public page and the
 * homepage spotlight, keyed by slug. The lessons themselves (titles, weeks,
 * minutes) come from the API; this adds the tagline, a one-line summary per
 * week, outcomes and audience. A course without an entry still gets the full
 * animated page.
 */
export interface ShowcaseWeek {
  /** Must match the lessons' `module_title` to attach the summary. */
  title: string
  summary: string
  icon: LucideIcon
}

export interface CourseShowcase {
  tagline: string
  level: string
  /** Shown where the API isn't asked (homepage spotlight). */
  lessonCount: number
  hours: number
  weeks: ShowcaseWeek[]
  /** A handful of lesson titles for the homepage marquee. */
  highlights: string[]
  outcomes: { icon: LucideIcon; title: string; text: string }[]
  audience: { icon: LucideIcon; title: string; text: string }[]
}

export const AI_ESSENTIALS_SLUG = 'ai-career-essentials'

const SHOWCASES: Record<string, CourseShowcase> = {
  [AI_ESSENTIALS_SLUG]: {
    tagline:
      'A complete 4-week course: understand AI, use it well, apply it at work and grow your career. No coding needed.',
    level: 'Beginner',
    lessonCount: 24,
    hours: 19,
    weeks: [
      {
        title: 'Week 1 · Understanding AI',
        summary: 'What AI is, how machines learn, how ChatGPT-style tools work, and where AI fails.',
        icon: Brain,
      },
      {
        title: 'Week 2 · Using AI Tools Well',
        summary: 'The right mindset, the main tools, and prompting skills that get real results.',
        icon: MessageSquareText,
      },
      {
        title: 'Week 3 · AI at Work',
        summary: 'Writing, research, spreadsheets, presentations and business tasks — done faster.',
        icon: Briefcase,
      },
      {
        title: 'Week 4 · Responsible AI and Your Career',
        summary: 'Privacy, ethics and the future of work — then your portfolio and 90-day plan.',
        icon: Rocket,
      },
    ],
    highlights: [
      'What AI Really Is (and Isn’t)',
      'How Machines Learn',
      'Generative AI and LLMs',
      'Prompting Like a Pro',
      'Checking AI’s Work',
      'AI for Spreadsheets and Data',
      'Automate a Real Task',
      'Privacy and Data Protection',
      'Your 90-Day AI Career Plan',
      'Final Project and Certificate',
    ],
    outcomes: [
      { icon: Lightbulb, title: 'Explain AI simply', text: 'Say what AI is, how it learns, and why it makes mistakes.' },
      { icon: MessageSquareText, title: 'Write strong prompts', text: 'Get useful answers the first time, then improve them.' },
      { icon: Wrench, title: 'Save hours every week', text: 'Use AI for writing, research, data and presentations.' },
      { icon: ShieldCheck, title: 'Use AI safely', text: 'Verify facts, protect data and stay honest.' },
    ],
    audience: [
      { icon: GraduationCap, title: 'Students', text: 'Study faster and prepare for the job market.' },
      { icon: Store, title: 'Business owners', text: 'Write, plan and serve customers with less effort.' },
      { icon: Users, title: 'Professionals', text: 'Stay ahead in your role as AI changes work.' },
    ],
  },
}

export function getShowcase(slug: string | undefined): CourseShowcase | undefined {
  return slug ? SHOWCASES[slug] : undefined
}

/** Group an ordered lesson list into its modules (null module => one untitled group). */
export function groupByModule<T extends { module_title?: string | null }>(
  lessons: T[],
): { title: string | null; lessons: { lesson: T; index: number }[] }[] {
  const groups: { title: string | null; lessons: { lesson: T; index: number }[] }[] = []
  lessons.forEach((lesson, index) => {
    const title = lesson.module_title ?? null
    const last = groups[groups.length - 1]
    if (last && last.title === title) last.lessons.push({ lesson, index })
    else groups.push({ title, lessons: [{ lesson, index }] })
  })
  return groups
}

export function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${minutes} min`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m ? `${h} h ${m} min` : `${h} h`
}
