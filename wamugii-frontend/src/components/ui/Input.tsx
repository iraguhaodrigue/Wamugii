import { type InputHTMLAttributes, forwardRef, useId, useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { cn } from '@/utils/cn'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  /**
   * Opt out of the show/hide button on a password field. The toggle is on by
   * default for `type="password"`, so every password input in the app gets it
   * without each caller remembering to ask.
   */
  hideToggle?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, id, required, type, hideToggle = false, ...props }, ref) => {
    const generatedId = useId()
    const inputId = id ?? generatedId
    const errorId = `${inputId}-error`
    const hintId = `${inputId}-hint`

    const [isRevealed, setIsRevealed] = useState(false)
    const isPassword = type === 'password'
    const showToggle = isPassword && !hideToggle

    // Purely a display concern: revealing swaps the rendered input type so the
    // browser stops masking it. The value itself is untouched and is never
    // copied, logged, or sent anywhere it wasn't already going.
    const resolvedType = isPassword && isRevealed ? 'text' : type

    const field = (
      <input
        ref={ref}
        id={inputId}
        type={resolvedType}
        required={required}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : hint ? hintId : undefined}
        className={cn(
          'h-10 w-full rounded-lg border border-slate-300 bg-panel px-3 text-sm text-slate-900',
          'placeholder:text-slate-400',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:border-brand-500',
          'disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500',
          // Room for the button so long values don't run underneath it.
          showToggle && 'pr-10',
          error && 'border-red-500 focus-visible:ring-red-500 focus-visible:border-red-500',
          className,
        )}
        {...props}
      />
    )

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-slate-700">
            {label}
            {required && <span className="ml-0.5 text-red-600">*</span>}
          </label>
        )}

        {showToggle ? (
          <div className="relative">
            {field}
            <button
              type="button"
              onClick={() => setIsRevealed((shown) => !shown)}
              // A real button, so it's reachable and operable by keyboard.
              aria-label={isRevealed ? 'Hide password' : 'Show password'}
              aria-pressed={isRevealed}
              // The field itself already announces its own state; keep the
              // button out of the input's description.
              tabIndex={props.disabled ? -1 : 0}
              disabled={props.disabled}
              className="absolute right-1 top-1/2 inline-flex size-8 -translate-y-1/2 items-center justify-center rounded-md text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isRevealed ? (
                <EyeOff className="size-4" aria-hidden="true" />
              ) : (
                <Eye className="size-4" aria-hidden="true" />
              )}
            </button>
          </div>
        ) : (
          field
        )}

        {error ? (
          <p id={errorId} className="text-sm text-red-600">
            {error}
          </p>
        ) : hint ? (
          <p id={hintId} className="text-sm text-slate-500">
            {hint}
          </p>
        ) : null}
      </div>
    )
  },
)
Input.displayName = 'Input'
