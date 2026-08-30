export interface PageStubProps {
  title: string
  description?: string
}

export function PageStub({ title, description }: PageStubProps) {
  return (
    <div className="mx-auto flex min-h-[50vh] w-full max-w-3xl flex-col items-center justify-center gap-2 px-4 py-16 text-center">
      <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
      <p className="text-sm text-slate-500">
        {description ?? 'This page will be built in an upcoming stage.'}
      </p>
    </div>
  )
}
