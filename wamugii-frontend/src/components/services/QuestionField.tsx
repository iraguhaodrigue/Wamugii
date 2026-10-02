import type { ServiceQuestion } from '@/api/services'
import { Input, Select, Textarea } from '@/components/ui'
import { cn } from '@/utils/cn'

/**
 * How a question's value is held in form state.
 *
 * One string per question, including MULTISELECT — the backend stores an answer
 * as free text, so the joined form ("Blog, Booking") is what gets submitted and
 * what staff read. Keeping the state a plain string means there is no separate
 * encode step between the field and the payload.
 */
export type AnswerMap = Record<number, string>

/** The separator a multiselect answer is joined with, in one place. */
export const MULTISELECT_SEPARATOR = ', '

export interface QuestionFieldProps {
  question: ServiceQuestion
  value: string
  error?: string
  onChange: (value: string) => void
  disabled?: boolean
}

/** Renders one service question as the input its type calls for. */
export function QuestionField({
  question,
  value,
  error,
  onChange,
  disabled,
}: QuestionFieldProps) {
  const label = question.question_text
  const options = question.options ?? []

  switch (question.question_type) {
    case 'TEXTAREA':
      return (
        <Textarea
          label={label}
          rows={4}
          required={question.is_required}
          error={error}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
        />
      )

    case 'NUMBER':
      return (
        <Input
          label={label}
          type="number"
          min="0"
          required={question.is_required}
          error={error}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
        />
      )

    case 'SELECT':
      return (
        <Select
          label={label}
          required={question.is_required}
          error={error}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          options={[
            { value: '', label: question.is_required ? 'Select an option' : 'No preference' },
            ...options.map((option) => ({ value: option, label: option })),
          ]}
        />
      )

    case 'YES_NO':
      return (
        <Select
          label={label}
          required={question.is_required}
          error={error}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          options={[
            { value: '', label: question.is_required ? 'Select one' : 'Not sure yet' },
            { value: 'Yes', label: 'Yes' },
            { value: 'No', label: 'No' },
          ]}
        />
      )

    case 'MULTISELECT': {
      // A checkbox group rather than a <select multiple>: multi-select boxes are
      // hard to discover and worse on touch. The joined string stays the single
      // source of truth so nothing has to be reconciled on submit.
      const selected = value ? value.split(MULTISELECT_SEPARATOR).filter(Boolean) : []

      function toggle(option: string) {
        const next = selected.includes(option)
          ? selected.filter((item) => item !== option)
          : // Re-derived from `options` so the answer keeps the order the admin
            // set, not the order the visitor happened to click in.
            options.filter((item) => item === option || selected.includes(item))
        onChange(next.join(MULTISELECT_SEPARATOR))
      }

      return (
        <fieldset className="flex flex-col gap-2" disabled={disabled}>
          <legend className="text-sm font-medium text-slate-700">
            {label}
            {question.is_required && <span className="ml-0.5 text-red-600">*</span>}
          </legend>
          <div className="grid gap-2 sm:grid-cols-2">
            {options.map((option) => (
              <label
                key={option}
                className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 bg-panel px-3 py-2 text-sm text-slate-700 transition-colors hover:border-brand-400/60"
              >
                <input
                  type="checkbox"
                  className="size-4 rounded border-slate-300 accent-[var(--color-brand-solid)]"
                  checked={selected.includes(option)}
                  onChange={() => toggle(option)}
                />
                {option}
              </label>
            ))}
          </div>
          {error && (
            <p role="alert" className="text-sm text-red-600">
              {error}
            </p>
          )}
        </fieldset>
      )
    }

    case 'TEXT':
    default:
      return (
        <Input
          label={label}
          required={question.is_required}
          error={error}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          className={cn(error && 'border-red-500')}
        />
      )
  }
}
