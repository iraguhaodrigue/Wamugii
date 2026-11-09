import {
  BarChart3,
  Briefcase,
  Brain,
  Eye,
  GitBranch,
  Layers,
  Scale,
  Code,
  Sigma,
  Table2,
  TrendingDown,
  GraduationCap,
  Lightbulb,
  MessageSquareText,
  Network,
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
  'machine-learning-fundamentals': {
    tagline:
      'A hands-on 4-week course in classic machine learning with scikit-learn — build, evaluate, tune and deploy models you can trust. Runs free in your browser.',
    level: 'Intermediate',
    lessonCount: 24,
    hours: 22,
    weeks: [
      {
        title: 'Week 1 · Your First Models with scikit-learn',
        summary: 'The workflow, encoding and scaling, linear and logistic regression and k-NN.',
        icon: TrendingDown,
      },
      {
        title: 'Week 2 · Trees, Ensembles and More',
        summary: 'Decision trees, random forests, boosting, SVMs and Naive Bayes on real medical data.',
        icon: GitBranch,
      },
      {
        title: 'Week 3 · Evaluating and Improving Models',
        summary: 'Cross-validation, precision and recall, ROC and thresholds, regularisation and tuning.',
        icon: BarChart3,
      },
      {
        title: 'Week 4 · Unsupervised Learning and Real Projects',
        summary: 'k-means, PCA, pipelines, imbalanced data, fairness and saving models.',
        icon: Layers,
      },
    ],
    highlights: [
      'Linear & Logistic Regression',
      'k-Nearest Neighbours',
      'Decision Trees',
      'Random Forests',
      'Gradient Boosting',
      'Support Vector Machines',
      'Cross-Validation',
      'Precision, Recall & ROC',
      'k-Means & PCA',
      'Pipelines & Fairness',
    ],
    outcomes: [
      { icon: Brain, title: 'Build real models', text: 'Seven families of algorithms, all with the same scikit-learn workflow.' },
      { icon: BarChart3, title: 'Evaluate honestly', text: 'Cross-validation, the right metrics and thresholds chosen from real costs.' },
      { icon: Wrench, title: 'Ship it properly', text: 'Pipelines, tuning, saved models, model cards and drift checks.' },
      { icon: Scale, title: 'Use it responsibly', text: 'Imbalanced data, proxies and fairness audits by group.' },
    ],
    audience: [
      { icon: GraduationCap, title: 'Students', text: 'The core of every data science and AI degree.' },
      { icon: Briefcase, title: 'Analysts and developers', text: 'Add prediction to your reports and apps.' },
      { icon: Users, title: 'Future AI builders', text: 'Step 3 of the WAMUGII AI Program, before deep learning.' },
    ],
  },
  'deep-learning-neural-networks': {
    tagline:
      'A hands-on 4-week course in deep learning with PyTorch — build networks from scratch, train them well, and use CNNs, transformers and generative models. Free GPU in your browser.',
    level: 'Intermediate',
    lessonCount: 24,
    hours: 23,
    weeks: [
      {
        title: 'Week 1 · Neural Networks from Scratch',
        summary: 'Neurons, activations, loss, gradient descent and backpropagation — then PyTorch autograd.',
        icon: Network,
      },
      {
        title: 'Week 2 · Training Deep Networks Well',
        summary: 'nn.Module, Adam, dropout, early stopping, batch norm and DataLoaders.',
        icon: TrendingDown,
      },
      {
        title: 'Week 3 · Computer Vision with CNNs',
        summary: 'Convolutions, data augmentation, transfer learning with ResNet and trustworthy image models.',
        icon: Eye,
      },
      {
        title: 'Week 4 · Sequences, Attention and Generative Models',
        summary: 'Embeddings, LSTMs, transformers, autoencoders and deploying models behind an API.',
        icon: Brain,
      },
    ],
    highlights: [
      'A Network from Scratch',
      'Backpropagation',
      'PyTorch & Autograd',
      'Adam & Early Stopping',
      'Batch Norm & ResNets',
      'CNNs for Images',
      'Transfer Learning',
      'LSTM Forecasting',
      'Attention & Transformers',
      'Deploying with FastAPI',
    ],
    outcomes: [
      { icon: Network, title: 'Understand networks', text: 'Build and train a neural network from scratch, then with PyTorch.' },
      { icon: TrendingDown, title: 'Train them well', text: 'Optimisers, regularisation, normalisation and honest validation.' },
      { icon: Eye, title: 'See with CNNs', text: 'Image models with augmentation and pretrained ResNets.' },
      { icon: Brain, title: 'Read and generate', text: 'Embeddings, LSTMs, attention, autoencoders — and responsible deployment.' },
    ],
    audience: [
      { icon: GraduationCap, title: 'Students', text: 'The deep-learning core of AI and data-science degrees.' },
      { icon: Briefcase, title: 'Developers', text: 'Add vision, language and forecasting to your apps.' },
      { icon: Users, title: 'Future AI builders', text: 'Step 4 of the WAMUGII AI Program, before LLMs.' },
    ],
  },
  'modern-ai-llms-generative': {
    tagline:
      'A hands-on 4-week course in large language models and generative AI — build a tiny GPT, use LLM APIs, build RAG with citations, agents and safe AI apps. Every line of code tested.',
    level: 'Advanced',
    lessonCount: 24,
    hours: 26,
    weeks: [
      {
        title: 'Week 1 · How Large Language Models Work',
        summary: 'Tokens and BPE, next-token prediction and sampling, your own tiny GPT, and how assistants are trained.',
        icon: Brain,
      },
      {
        title: 'Week 2 · Building with LLM APIs',
        summary: 'API calls, prompt engineering, structured output, tool use, streaming, cost and reliability.',
        icon: Code,
      },
      {
        title: 'Week 3 · Embeddings, Search and RAG',
        summary: 'Embeddings, vector search, retrieval-augmented generation with citations, and honest evaluation.',
        icon: Layers,
      },
      {
        title: 'Week 4 · Agents, Generative AI and Responsible Deployment',
        summary: 'Agents, LoRA fine-tuning, diffusion, open models, prompt-injection defence and a deployed AI API.',
        icon: ShieldCheck,
      },
    ],
    highlights: [
      'Tokenizers & BPE',
      'A Tiny GPT from Scratch',
      'LLM APIs & Prompting',
      'Tool Use & JSON',
      'Embeddings & Vector Search',
      'RAG with Citations',
      'Evaluating LLM Apps',
      'AI Agents',
      'LoRA & Diffusion',
      'Prompt-Injection Defence',
    ],
    outcomes: [
      { icon: Brain, title: 'Understand LLMs', text: 'Tokens, attention, sampling and training — you build a GPT yourself.' },
      { icon: Code, title: 'Build with APIs', text: 'Prompts, structured output, tools, streaming and cost control.' },
      { icon: Layers, title: 'Answer from documents', text: 'Embeddings, hybrid search and RAG with citations, measured properly.' },
      { icon: ShieldCheck, title: 'Ship it safely', text: 'Agents, guardrails, privacy and a tested, deployable AI web API.' },
    ],
    audience: [
      { icon: GraduationCap, title: 'Students', text: 'The modern-AI part of computer-science and data-science degrees.' },
      { icon: Briefcase, title: 'Developers', text: 'Add assistants, document search and automation to your products.' },
      { icon: Users, title: 'Future AI builders', text: 'Step 5 of the WAMUGII AI Program, after deep learning.' },
    ],
  },
  'responsible-ai-deployment': {
    tagline:
      'The capstone of the AI Program: take a model from notebook to a tested, monitored, fair and documented product — then build your own end-to-end project.',
    level: 'Capstone',
    lessonCount: 24,
    hours: 27,
    weeks: [
      {
        title: 'Week 1 · From Notebook to Product',
        summary: 'Model artifacts, reproducible training, a FastAPI service, ML tests and Docker packaging.',
        icon: Rocket,
      },
      {
        title: 'Week 2 · MLOps: Running Models in Production',
        summary: 'CI/CD and quality gates, a model registry, monitoring, drift, and safe releases.',
        icon: Wrench,
      },
      {
        title: 'Week 3 · Fairness, Explainability, Privacy and Security',
        summary: 'Fairness metrics and bias fixes, explanations, Rwanda data protection, and AI security — then a full audit.',
        icon: Scale,
      },
      {
        title: 'Week 4 · Governance, Documentation and the Capstone',
        summary: 'AI law and accountability, model cards, human oversight, and your own end-to-end project.',
        icon: ShieldCheck,
      },
    ],
    highlights: [
      'FastAPI Model Serving',
      'Testing ML Systems',
      'Docker Packaging',
      'CI/CD Quality Gates',
      'Monitoring & Drift',
      'Fairness Audits',
      'Explainable Decisions',
      'Privacy by Design',
      'AI Security',
      'Model Cards & Governance',
    ],
    outcomes: [
      { icon: Rocket, title: 'Ship models', text: 'A validated, versioned, tested API packaged with Docker.' },
      { icon: Wrench, title: 'Run them well', text: 'CI/CD, registries, monitoring, drift detection and safe releases.' },
      { icon: Scale, title: 'Make them fair', text: 'Measure and reduce bias, explain decisions, protect personal data.' },
      { icon: ShieldCheck, title: 'Govern them', text: 'Risk registers, model cards, human oversight — and your capstone.' },
    ],
    audience: [
      { icon: GraduationCap, title: 'Students', text: 'A final-year or master\'s capstone that employers can see working.' },
      { icon: Briefcase, title: 'Developers & data teams', text: 'Put models into production safely and keep them healthy.' },
      { icon: Users, title: 'Managers & policy makers', text: 'Understand fairness, privacy, risk and accountability in AI.' },
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
