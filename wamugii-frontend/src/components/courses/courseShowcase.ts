import {
  Briefcase,
  Brain,
  Code,
  Sigma,
  Table2,
  TrendingDown,
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
  'ai-foundations': {
    tagline:
      'A complete 4-week, university-level foundation in AI: how it works, how machines learn, how models are measured, and how to use AI responsibly. No coding needed.',
    level: 'Beginner to intermediate',
    lessonCount: 24,
    hours: 20,
    weeks: [
      {
        title: 'Week 1 · What AI Is',
        summary: 'A precise definition, the history of AI, intelligent agents, problem types and search.',
        icon: Brain,
      },
      {
        title: 'Week 2 · How Machines Learn',
        summary: 'Data, the machine-learning workflow, and supervised, unsupervised and reinforcement learning.',
        icon: Lightbulb,
      },
      {
        title: 'Week 3 · Measuring and Building Models',
        summary: 'Overfitting, accuracy, precision and recall, neural networks and how LLMs work.',
        icon: Wrench,
      },
      {
        title: 'Week 4 · AI in Society',
        summary: 'Bias, explainability, privacy, Rwanda’s AI policy, the EU AI Act — and careers in AI.',
        icon: ShieldCheck,
      },
    ],
    highlights: [
      'Defining AI, ML and Deep Learning',
      'Intelligent Agents',
      'Supervised Learning',
      'Reinforcement Learning',
      'Precision and Recall',
      'Neural Networks Explained',
      'Transformers and LLMs',
      'Bias and Fairness',
      'AI Governance and Policy',
      'Careers in AI',
    ],
    outcomes: [
      { icon: Brain, title: 'Explain AI precisely', text: 'Describe any AI system as an agent and name its problem type.' },
      { icon: Lightbulb, title: 'Understand how models learn', text: 'Data, training, testing, neural networks and LLMs — clearly.' },
      { icon: Wrench, title: 'Judge results honestly', text: 'Read a confusion matrix and pick the right measure.' },
      { icon: ShieldCheck, title: 'Use AI responsibly', text: 'Fairness, privacy, Rwanda’s data law and AI governance.' },
    ],
    audience: [
      { icon: GraduationCap, title: 'Students', text: 'A strong base before machine learning and deep learning.' },
      { icon: Briefcase, title: 'Professionals', text: 'Understand the AI your organisation buys and builds.' },
      { icon: Users, title: 'Future AI builders', text: 'The first step of the WAMUGII AI Program.' },
    ],
  },
  'math-python-for-ai': {
    tagline:
      'A hands-on 4-week course in Python and the maths behind AI — from your first line of code to training a model from scratch. Runs free in your browser.',
    level: 'Beginner to intermediate',
    lessonCount: 24,
    hours: 20,
    weeks: [
      {
        title: 'Week 1 · Python Basics for AI',
        summary: 'Variables, lists, loops, decisions, functions and files — in free Google Colab.',
        icon: Code,
      },
      {
        title: 'Week 2 · Working with Data',
        summary: 'NumPy, Pandas, cleaning messy data, grouping and clear charts.',
        icon: Table2,
      },
      {
        title: 'Week 3 · Linear Algebra, Statistics and Probability',
        summary: 'Vectors, matrices, averages and spread, probability and the normal curve.',
        icon: Sigma,
      },
      {
        title: 'Week 4 · Calculus and Your First Model',
        summary: 'Bayes, correlation, derivatives and gradient descent — then linear regression from scratch.',
        icon: TrendingDown,
      },
    ],
    highlights: [
      'Your First Python Program',
      'Lists, Dictionaries and Loops',
      'NumPy Arrays',
      'Pandas DataFrames',
      'Cleaning Messy Data',
      'Vectors and Matrices',
      'Probability and Bayes',
      'Derivatives',
      'Gradient Descent',
      'Linear Regression from Scratch',
    ],
    outcomes: [
      { icon: Code, title: 'Write real Python', text: 'Variables, loops, functions and files — the code behind AI.' },
      { icon: Table2, title: 'Handle real data', text: 'Clean, summarise and chart data with NumPy, Pandas and Matplotlib.' },
      { icon: Sigma, title: 'Understand the maths', text: 'Vectors, matrices, statistics and probability, explained simply.' },
      { icon: TrendingDown, title: 'Train a model', text: 'Build linear regression with your own gradient descent.' },
    ],
    audience: [
      { icon: GraduationCap, title: 'Students', text: 'The base for machine learning and data science.' },
      { icon: Briefcase, title: 'Professionals', text: 'Automate reports and analyse data with Python.' },
      { icon: Users, title: 'Future AI builders', text: 'Step 2 of the WAMUGII AI Program.' },
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
