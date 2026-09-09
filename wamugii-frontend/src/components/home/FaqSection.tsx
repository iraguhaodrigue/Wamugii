import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { Faq } from '@/components/common/Faq'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'

/** Answers describe how the application and process actually work today. */
const faqs = [
  {
    question: 'How do I request a quote?',
    answer:
      'Use the Request a Quote form — it takes a couple of minutes and needs no account. Tell us about the project, add a budget range and deadline if you have one, and we take it from there.',
  },
  {
    question: 'How much does a project cost?',
    answer:
      "It depends on scope — we don't work from a fixed price list. You'll get a clear estimate during scoping, and nothing starts until you have approved the budget in writing.",
  },
  {
    question: 'How long does development take?',
    answer:
      'It varies with complexity. We agree a timeline together during scoping, then track progress against milestones you can follow in your client portal.',
  },
  {
    question: 'Can you maintain my system after launch?',
    answer:
      'Yes. Ongoing technical support is part of what we offer — launch is a stage in the project, not the end of the relationship.',
  },
  {
    question: 'Do you provide hosting?',
    answer:
      'Yes. Hosting and domains are one of our services, covering registration, setup and the configuration around them.',
  },
  {
    question: 'Can you build custom software for my business?',
    answer:
      'Yes. Custom software development is a core service — typically internal systems, dashboards and automation built around how your business already works.',
  },
  {
    question: 'I already have a website or system. Can you just improve it?',
    answer:
      'Yes. IT consultancy, installation and technical support all cover reviewing, fixing and improving what you already have — we do not require a rebuild from scratch.',
  },
  {
    question: 'Do I need a technical background to work with you?',
    answer:
      "No. We keep updates in plain language — you shouldn't need to read code to understand how your project is progressing.",
  },
]

export function FaqSection() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <Container>
        <SectionHeading
          label="FAQ"
          title="Questions you might have"
          description="Still unsure about something? Ask it directly in your quote request — we'll answer before anything is agreed."
        />

        <div className="mx-auto mt-12 max-w-3xl">
          <Reveal>
            <Faq items={faqs} />
          </Reveal>

          <Reveal delay={80}>
            <div className="mt-8 text-center">
              <Link
                to={paths.requestQuote}
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
              >
                Ask us your question
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </div>
          </Reveal>
        </div>
      </Container>
    </section>
  )
}
