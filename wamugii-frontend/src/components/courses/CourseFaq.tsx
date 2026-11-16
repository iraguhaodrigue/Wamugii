import { ChevronDown } from 'lucide-react'
import { Reveal } from '@/components/common/Reveal'

interface Props {
  isFree: boolean
  coding: boolean
  hasHandbook: boolean
}

/** Frequently asked questions on a course page, in simple English. */
export function CourseFaq({ isFree, coding, hasHandbook }: Props) {
  const items: { q: string; a: string }[] = [
    {
      q: 'How long do I have access?',
      a: 'For as long as the course is online. Study at your own pace: plan about one lesson a day, five days a week, and you finish in about a month.',
    },
    {
      q: 'What do I need?',
      a: coding
        ? 'A laptop or desktop computer with a modern browser (Chrome, Edge or Firefox) and an internet connection. The Python examples run inside the browser, so you do not need to install anything. A phone works for reading, but coding is easier on a computer.'
        : 'A phone, tablet or computer with an internet connection. No coding or special software is needed.',
    },
    ...(hasHandbook
      ? [
          {
            q: 'Can I learn without watching the videos?',
            a: 'Yes. The Student Handbook explains every lesson in full, with worked examples, diagrams and a self-check with answers, so you can learn by reading alone. Enrolled students download it from the first lesson; anyone can download a free sample chapter on this page.',
          },
        ]
      : []),
    ...(coding
      ? [
          {
            q: 'Do the code examples really run in my browser?',
            a: 'Yes. Press Run on a Python example and it runs on your own device; nothing is sent to our server. The first run takes 10 to 30 seconds while Python loads, then it is fast. Every lesson also has an Open in Colab button that opens the whole lesson as a Google Colab notebook, free and with a GPU, for the few examples that need a GPU, an API key or a web server.',
          },
        ]
      : []),
    {
      q: 'How do I get the certificate?',
      a: 'Complete every lesson (and pass the final exam when the course has one). Your WAMUGII certificate of completion then unlocks in the course, and you receive an email. You can add it to your CV and LinkedIn profile.',
    },
    {
      q: isFree ? 'Is it really free?' : 'How do I pay?',
      a: isFree
        ? 'Yes. Enroll with a free account and every lesson, quiz and the certificate are open to you.'
        : 'When you enroll, we create an invoice in your account. The lessons unlock as soon as we record your payment.',
    },
    {
      q: 'What if I get stuck?',
      a: 'Every lesson has a questions section. Ask about that lesson there: your instructor gets an email and answers you.',
    },
  ]

  return (
    <section>
      <Reveal>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">Questions students ask</h2>
      </Reveal>
      <div className="mt-6 divide-y divide-slate-200 overflow-hidden rounded-2xl border border-slate-200 bg-panel">
        {items.map(({ q, a }) => (
          <details key={q} className="group">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 text-sm font-semibold text-slate-900 hover:bg-brand-50/50">
              {q}
              <ChevronDown className="size-4 shrink-0 text-brand-600 transition-transform group-open:rotate-180" aria-hidden="true" />
            </summary>
            <p className="px-5 pb-4 text-sm leading-relaxed text-slate-600">{a}</p>
          </details>
        ))}
      </div>
    </section>
  )
}
