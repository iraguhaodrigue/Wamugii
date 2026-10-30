import {
  Brain,
  Briefcase,
  Compass,
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
 * Extra, presentation-only content for a course's public page, keyed by slug.
 *
 * The API only gives lesson titles to visitors who are not enrolled, so the
 * one-line summaries, outcomes and audience cards live here. A course without
 * an entry still gets the animated page; it just shows titles without the
 * extra lines. Lessons are matched by position (lesson 1 → lessons[0]).
 */
export interface ShowcaseLesson {
  /** Used where the API isn't asked (the homepage spotlight). */
  title: string
  summary: string
  minutes: number
  icon: LucideIcon
}

export interface CourseShowcase {
  tagline: string
  level: string
  lessons: ShowcaseLesson[]
  outcomes: { icon: LucideIcon; title: string; text: string }[]
  audience: { icon: LucideIcon; title: string; text: string }[]
}

export const AI_ESSENTIALS_SLUG = 'ai-career-essentials'

const SHOWCASES: Record<string, CourseShowcase> = {
  [AI_ESSENTIALS_SLUG]: {
    tagline: 'Learn to use AI well, check its work, and grow your career. No coding needed.',
    level: 'Beginner',
    lessons: [
      { title: "What AI Really Is (and Isn't)", icon: Brain, minutes: 8, summary: 'The one idea behind all AI: it learns patterns from examples.' },
      { title: 'The AI-Ready Mindset', icon: Compass, minutes: 7, summary: 'Use AI as a fast assistant and keep your own judgement in charge.' },
      { title: 'Core AI Tools for Everyday Work', icon: Wrench, minutes: 8, summary: 'The main kinds of AI tools, and how to pick the right one.' },
      { title: 'Prompting Like a Pro', icon: MessageSquareText, minutes: 10, summary: 'Write prompts with a role, a task, details and a format.' },
      { title: 'Using AI in Your Field', icon: Briefcase, minutes: 9, summary: 'Point AI at the repetitive parts of your own real work.' },
      { title: 'Working Responsibly with AI', icon: ShieldCheck, minutes: 9, summary: 'Check facts, protect private data and stay honest.' },
      { title: 'Building Your AI-Augmented Career', icon: Rocket, minutes: 9, summary: 'Show real results and plan your next step with AI.' },
    ],
    outcomes: [
      { icon: Lightbulb, title: 'Explain AI simply', text: 'Say what AI is, what it is not, and why it makes mistakes.' },
      { icon: MessageSquareText, title: 'Write strong prompts', text: 'Get useful answers the first time, then improve them.' },
      { icon: Briefcase, title: 'Save time at work', text: 'Use AI on real tasks in your own field, every week.' },
      { icon: ShieldCheck, title: 'Use AI safely', text: 'Verify facts, protect data and avoid over-reliance.' },
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
