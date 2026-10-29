import { useEffect } from 'react'
import { Printer, X } from 'lucide-react'
import type { Certificate as CertificateData } from '@/api/courses'

export interface CertificateProps {
  certificate: CertificateData
  onClose: () => void
}

/**
 * A printable certificate of completion.
 *
 * Deliberately NOT themed. The client portal runs inside the `.dark` token
 * scope, which remaps `--color-slate-*` — `slate-900` resolves to near-white in
 * there — so this component uses literal colours instead of the usual utility
 * tokens. A certificate is printed on white paper and has to look the same
 * however the app around it is themed. `--color-brand-solid` and
 * `--color-accent-solid` are the two brand tokens that are intentionally never
 * remapped, so those are safe to use.
 *
 * Printing is handled by `window.print()` plus the `body.certificate-print-mode`
 * rules in index.css. The body class and the landscape `@page` rule are both
 * attached only while this component is mounted, because the invoice page also
 * calls `window.print()` and must keep printing portrait with its own content.
 */
export function Certificate({ certificate, onClose }: CertificateProps) {
  useEffect(() => {
    document.body.classList.add('certificate-print-mode')

    // `@page` is document-level and cannot be scoped by a class, so the
    // orientation is attached and removed with the component rather than
    // living in the stylesheet, where it would also rotate invoice printing.
    const pageRule = document.createElement('style')
    pageRule.textContent = '@page { size: A4 landscape; margin: 10mm; }'
    document.head.appendChild(pageRule)

    return () => {
      document.body.classList.remove('certificate-print-mode')
      pageRule.remove()
    }
  }, [])

  const issued = new Date(certificate.issued_on).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="space-y-4">
      <div className="print-hide flex flex-wrap items-center justify-between gap-3">
        <button
          type="button"
          onClick={onClose}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 transition-colors hover:text-brand-600"
        >
          <X className="size-4" aria-hidden="true" />
          Back to the course
        </button>
        <button
          type="button"
          onClick={() => window.print()}
          className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
        >
          <Printer className="size-4" aria-hidden="true" />
          Print / Save as PDF
        </button>
      </div>

      {/*
        A4 landscape is 297x210mm, and the aspect ratio holds those proportions
        at any width. Percentage padding and `cqw` type sizes make everything
        inside scale with the sheet, so one layout covers phone to desktop.

        `containerType: inline-size` is what makes the `cqw` units resolve
        against this sheet rather than the viewport -- without a container they
        fall back to viewport units and the type scale comes untied from the
        certificate it is sitting on.
      */}
      <div
        className="certificate-sheet mx-auto w-full overflow-hidden rounded-lg bg-white shadow-lg"
        style={{ aspectRatio: '297 / 210', maxWidth: '1000px', containerType: 'inline-size' }}
      >
        <div className="flex h-full flex-col items-center justify-center border-[6px] border-double border-[#0e7490] p-[4%] text-center">
          <p
            className="text-[1.6cqw] font-semibold uppercase tracking-[0.3em] text-[#0e7490]"
            style={{ fontSize: 'clamp(8px, 1.5cqw, 15px)' }}
          >
            Certificate of Completion
          </p>

          <div
            className="mt-[3%] h-px w-[18%]"
            style={{ backgroundImage: 'linear-gradient(90deg, #0e7490, #6d28d9)' }}
            aria-hidden="true"
          />

          <p
            className="mt-[4%] text-[#475569]"
            style={{ fontSize: 'clamp(9px, 1.5cqw, 16px)' }}
          >
            This certifies that
          </p>

          <h1
            className="mt-[1%] font-bold leading-tight text-[#0f172a]"
            style={{ fontSize: 'clamp(20px, 5cqw, 54px)' }}
          >
            {certificate.student_name}
          </h1>

          <p
            className="mt-[3%] text-[#475569]"
            style={{ fontSize: 'clamp(9px, 1.5cqw, 16px)' }}
          >
            has successfully completed
          </p>

          <h2
            className="mt-[1%] font-semibold leading-snug text-[#0e7490]"
            style={{ fontSize: 'clamp(13px, 2.8cqw, 30px)' }}
          >
            {certificate.course_title}
          </h2>

          <p
            className="mt-[1.5%] text-[#64748b]"
            style={{ fontSize: 'clamp(8px, 1.2cqw, 13px)' }}
          >
            {certificate.lesson_count} {certificate.lesson_count === 1 ? 'lesson' : 'lessons'}{' '}
            completed
          </p>

          <div className="mt-auto flex w-full items-end justify-between gap-[4%] pt-[4%]">
            <div className="text-left">
              <p
                className="font-medium text-[#0f172a]"
                style={{ fontSize: 'clamp(8px, 1.2cqw, 13px)' }}
              >
                {issued}
              </p>
              <div className="mt-[6%] h-px w-full bg-[#cbd5e1]" aria-hidden="true" />
              <p
                className="mt-[4%] uppercase tracking-wider text-[#64748b]"
                style={{ fontSize: 'clamp(6px, 0.95cqw, 11px)' }}
              >
                Date issued
              </p>
            </div>

            <div className="text-right">
              <p
                className="font-bold tracking-tight text-[#0f172a]"
                style={{ fontSize: 'clamp(9px, 1.5cqw, 17px)' }}
              >
                WAMUGII TECH SOLUTIONS
              </p>
              <p
                className="mt-[2%] italic text-[#0e7490]"
                style={{ fontSize: 'clamp(7px, 1.1cqw, 12px)' }}
              >
                We Build. We Innovate. We Empower.
              </p>
              <div className="mt-[6%] h-px w-full bg-[#cbd5e1]" aria-hidden="true" />
              <p
                className="mt-[4%] uppercase tracking-wider text-[#64748b]"
                style={{ fontSize: 'clamp(6px, 0.95cqw, 11px)' }}
              >
                Authorised signature
              </p>
            </div>
          </div>

          <p
            className="mt-[3%] font-mono uppercase tracking-widest text-[#94a3b8]"
            style={{ fontSize: 'clamp(6px, 0.9cqw, 11px)' }}
          >
            {certificate.certificate_id}
          </p>
        </div>
      </div>
    </div>
  )
}
