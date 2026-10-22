import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  ExternalLink,
  Plus,
  SearchX,
  Trash2,
  Upload,
  Users,
} from 'lucide-react'
import {
  createLesson,
  deactivateCourse,
  deactivateLesson,
  deactivateLessonMaterial,
  getCourseById,
  listCourseEnrollments,
  listCourseLessons,
  updateCourse,
  updateLesson,
  uploadLessonMaterial,
  type Course,
  type Lesson,
  type LessonCreate,
  type LessonMaterial,
} from '@/api/courses'
import { useAuth } from '@/context/AuthContext'
import { useUsersMap } from '@/hooks/useUsersMap'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
  ConfirmDialog,
  EmptyState,
  ErrorState,
  Input,
  Modal,
  ProgressBar,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
  Textarea,
} from '@/components/ui'
import { formatDate, formatFileSize, formatMoney } from '@/utils/format'
import { courseStatusVariant, enrollmentStatusVariant } from '@/utils/statusBadge'
import { VideoEmbed } from '@/components/courses/VideoEmbed'
import { isSupportedVideoUrl } from '@/utils/videoEmbed'
import { cn } from '@/utils/cn'

type Tab = 'content' | 'lessons' | 'enrollments'

export function AdminCourseDetail() {
  const { courseId } = useParams<{ courseId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'

  const [tab, setTab] = useState<Tab>('content')
  const [draftCourse, setDraftCourse] = useState<Partial<Course> | null>(null)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const courseQuery = useQuery<Course, ApiError>({
    queryKey: ['courses', 'admin', courseId],
    queryFn: () => getCourseById(courseId!),
    enabled: Boolean(courseId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })
  const course = courseQuery.data
  usePageTitle(course?.title ?? 'Course')

  const updateCourseMutation = useMutation<Course, ApiError, Partial<Course>>({
    mutationFn: (payload) =>
      updateCourse(courseId!, {
        title: payload.title,
        description: payload.description,
        is_free: payload.is_free,
        price: payload.is_free ? null : (payload.price ?? null),
        status: payload.status,
        category: payload.category ?? null,
        cover_image_url: payload.cover_image_url ?? null,
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(['courses', 'admin', courseId], updated)
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setDraftCourse(null)
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deactivateCourse(courseId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      navigate(paths.admin.courses)
    },
  })

  if (courseQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  if (courseQuery.isError && courseQuery.error.status === 404) {
    return (
      <EmptyState
        icon={SearchX}
        title="Course not found"
        description="This course doesn't exist."
        action={
          <Link
            to={paths.admin.courses}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Courses
          </Link>
        }
      />
    )
  }
  if (courseQuery.isError || !course) {
    return (
      <ErrorState
        title="Couldn't load this course"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => courseQuery.refetch()}
      />
    )
  }

  const working = { ...course, ...(draftCourse ?? {}) }
  const isDirty = draftCourse !== null

  const tabs: { key: Tab; label: string }[] = [
    { key: 'content', label: 'Course content' },
    { key: 'lessons', label: 'Lessons' },
    { key: 'enrollments', label: 'Enrollments' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={paths.admin.courses}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Courses
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">{course.title}</h1>
            <Badge variant={courseStatusVariant[course.status]}>{course.status}</Badge>
            {course.is_free ? (
              <Badge variant="success">Free</Badge>
            ) : (
              <Badge variant="info">{formatMoney(course.price) ?? 'Paid'}</Badge>
            )}
            {!course.is_active && <Badge variant="neutral">Deleted</Badge>}
          </div>
          <div className="flex items-center gap-2">
            <Link
              to={paths.courseDetail(course.slug)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:text-brand-700"
            >
              View public page
              <ExternalLink className="size-4" aria-hidden="true" />
            </Link>
            {isAdmin && course.is_active && (
              <Button
                size="sm"
                variant="danger"
                leftIcon={<Trash2 className="size-4" />}
                onClick={() => setIsDeleteOpen(true)}
              >
                Delete
              </Button>
            )}
          </div>
        </div>
      </div>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      <div className="border-b border-slate-200">
        <nav className="-mb-px flex gap-6" aria-label="Course tabs">
          {tabs.map((t) => (
            <button
              key={t.key}
              type="button"
              onClick={() => setTab(t.key)}
              className={cn(
                'border-b-2 px-1 pb-3 text-sm font-medium transition-colors',
                tab === t.key
                  ? 'border-brand-600 text-brand-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700',
              )}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {tab === 'content' && (
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Course details
            </h2>
            <div className="mt-5 space-y-5">
              <Input
                label="Title"
                required
                value={working.title}
                onChange={(e) => setDraftCourse((d) => ({ ...(d ?? {}), title: e.target.value }))}
              />
              <Textarea
                label="Description"
                rows={5}
                value={working.description ?? ''}
                onChange={(e) =>
                  setDraftCourse((d) => ({ ...(d ?? {}), description: e.target.value }))
                }
              />
              <div className="grid gap-5 sm:grid-cols-2">
                <Input
                  label="Category"
                  hint="Optional"
                  value={working.category ?? ''}
                  onChange={(e) =>
                    setDraftCourse((d) => ({ ...(d ?? {}), category: e.target.value || null }))
                  }
                />
                <Input
                  label="Cover image URL"
                  hint="Optional"
                  value={working.cover_image_url ?? ''}
                  onChange={(e) =>
                    setDraftCourse((d) => ({
                      ...(d ?? {}),
                      cover_image_url: e.target.value || null,
                    }))
                  }
                />
                <Select
                  label="Pricing"
                  options={[
                    { value: 'free', label: 'Free' },
                    { value: 'paid', label: 'Paid' },
                  ]}
                  value={working.is_free ? 'free' : 'paid'}
                  onChange={(e) =>
                    setDraftCourse((d) => ({
                      ...(d ?? {}),
                      is_free: e.target.value === 'free',
                      price: e.target.value === 'free' ? null : working.price,
                    }))
                  }
                />
                {!working.is_free && (
                  <Input
                    label="Price (RWF)"
                    type="number"
                    min="0"
                    step="0.01"
                    required
                    value={working.price ?? ''}
                    onChange={(e) =>
                      setDraftCourse((d) => ({ ...(d ?? {}), price: e.target.value || null }))
                    }
                  />
                )}
                <Select
                  label="Status"
                  options={[
                    { value: 'DRAFT', label: 'Draft (hidden)' },
                    { value: 'PUBLISHED', label: 'Published (public)' },
                  ]}
                  value={working.status}
                  onChange={(e) =>
                    setDraftCourse((d) => ({
                      ...(d ?? {}),
                      status: e.target.value as Course['status'],
                    }))
                  }
                />
              </div>
            </div>
            {isDirty && (
              <div className="mt-5 flex justify-end gap-2 border-t border-slate-100 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setDraftCourse(null)}
                  disabled={updateCourseMutation.isPending}
                >
                  Cancel
                </Button>
                <Button
                  isLoading={updateCourseMutation.isPending}
                  onClick={() => updateCourseMutation.mutate(working)}
                >
                  Save changes
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === 'lessons' && <LessonsPanel courseId={course.id} />}
      {tab === 'enrollments' && <EnrollmentsPanel courseId={course.id} />}

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete this course?"
        description="This deactivates the course. Existing enrollments stay but the course disappears from the public catalogue."
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}

// --- lessons panel --------------------------------------------------------

const EMPTY_LESSON: LessonCreate = {
  title: '',
  content: '',
  video_url: null,
  display_order: 0,
}

function LessonsPanel({ courseId }: { courseId: number }) {
  const queryClient = useQueryClient()
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [draft, setDraft] = useState<LessonCreate>(EMPTY_LESSON)
  const [editing, setEditing] = useState<Lesson | null>(null)
  const [removing, setRemoving] = useState<Lesson | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const lessonsQuery = useQuery({
    queryKey: ['courses', 'admin', courseId, 'lessons'],
    queryFn: () => listCourseLessons(courseId),
  })

  function refresh() {
    queryClient.invalidateQueries({ queryKey: ['courses', 'admin', courseId, 'lessons'] })
    queryClient.invalidateQueries({ queryKey: ['courses', 'admin', String(courseId)] })
    queryClient.invalidateQueries({ queryKey: ['courses'] })
  }

  const saveMutation = useMutation<Lesson, ApiError, void>({
    mutationFn: () => {
      if (editing) {
        return updateLesson(courseId, editing.id, {
          title: draft.title,
          content: draft.content,
          video_url: draft.video_url || null,
          display_order: draft.display_order,
        })
      }
      return createLesson(courseId, {
        ...draft,
        display_order:
          draft.display_order || (lessonsQuery.data?.length ?? 0) + 1,
      })
    },
    onSuccess: () => {
      refresh()
      setIsCreateOpen(false)
      setEditing(null)
      setDraft(EMPTY_LESSON)
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const removeMutation = useMutation<Lesson, ApiError, number>({
    mutationFn: (lessonId) => deactivateLesson(courseId, lessonId),
    onSuccess: () => {
      refresh()
      setRemoving(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const videoLooksOk =
    !draft.video_url || isSupportedVideoUrl(draft.video_url)
  const canSave = draft.title.trim().length > 0 && videoLooksOk

  const lessons = lessonsQuery.data ?? []
  const activeLessons = lessons.filter((l) => l.is_active)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          Lessons appear to students in display-order. Attach a YouTube or Vimeo URL for the
          video; PDFs and docs upload as materials.
        </p>
        <Button
          size="sm"
          leftIcon={<Plus className="size-4" />}
          onClick={() => {
            setEditing(null)
            setDraft(EMPTY_LESSON)
            setFormError(null)
            setIsCreateOpen(true)
          }}
        >
          Add lesson
        </Button>
      </div>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      {lessonsQuery.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
      ) : lessonsQuery.isError ? (
        <ErrorState
          title="Couldn't load lessons"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => lessonsQuery.refetch()}
        />
      ) : activeLessons.length === 0 ? (
        <EmptyState title="No lessons yet" description="Add the first lesson to this course." />
      ) : (
        <ul className="space-y-3">
          {activeLessons.map((lesson) => (
            <li
              key={lesson.id}
              className="rounded-xl border border-slate-200 bg-panel p-5 shadow-sm"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-base font-semibold text-slate-900">{lesson.title}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Order: {lesson.display_order} · {lesson.materials.length} material(s)
                    {lesson.video_url && isSupportedVideoUrl(lesson.video_url) && ' · video attached'}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setEditing(lesson)
                      setDraft({
                        title: lesson.title,
                        content: lesson.content,
                        video_url: lesson.video_url,
                        display_order: lesson.display_order,
                      })
                      setFormError(null)
                      setIsCreateOpen(true)
                    }}
                  >
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    leftIcon={<Trash2 className="size-4" />}
                    onClick={() => setRemoving(lesson)}
                  >
                    Remove
                  </Button>
                </div>
              </div>
              <LessonMaterialsRow courseId={courseId} lesson={lesson} onRefresh={refresh} />
            </li>
          ))}
        </ul>
      )}

      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title={editing ? 'Edit lesson' : 'Add lesson'}
        size="lg"
      >
        <div className="space-y-4">
          <Input
            label="Title"
            required
            value={draft.title}
            onChange={(e) => setDraft((d) => ({ ...d, title: e.target.value }))}
          />
          <Textarea
            label="Content"
            rows={6}
            hint="The lesson body — what students read inside the player."
            value={draft.content ?? ''}
            onChange={(e) => setDraft((d) => ({ ...d, content: e.target.value }))}
          />
          <Input
            label="Video URL"
            placeholder="https://www.youtube.com/watch?v=…  or  https://vimeo.com/…"
            hint="Optional. Only YouTube or Vimeo links are embedded."
            value={draft.video_url ?? ''}
            onChange={(e) => setDraft((d) => ({ ...d, video_url: e.target.value || null }))}
          />
          {!videoLooksOk && draft.video_url && (
            <p role="alert" className="text-xs text-amber-700">
              That URL doesn't look like a supported YouTube or Vimeo video. Students will see
              "video unavailable" until this is fixed.
            </p>
          )}
          {draft.video_url && videoLooksOk && (
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
              <p className="mb-2 text-xs font-medium text-slate-500">Preview</p>
              <VideoEmbed url={draft.video_url} title="Lesson preview" />
            </div>
          )}
          <Input
            label="Display order"
            type="number"
            min="0"
            value={String(draft.display_order ?? 0)}
            onChange={(e) =>
              setDraft((d) => ({ ...d, display_order: Number(e.target.value || 0) }))
            }
          />

          <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
            <Button
              variant="outline"
              onClick={() => setIsCreateOpen(false)}
              disabled={saveMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              disabled={!canSave}
              isLoading={saveMutation.isPending}
              onClick={() => saveMutation.mutate()}
            >
              {editing ? 'Save lesson' : 'Add lesson'}
            </Button>
          </div>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={removing !== null}
        onClose={() => setRemoving(null)}
        onConfirm={() => removing && removeMutation.mutate(removing.id)}
        title="Remove this lesson?"
        description="It disappears from the player straight away. Existing progress on it is kept but no longer counts toward completion."
        confirmLabel="Remove"
        isDanger
        isLoading={removeMutation.isPending}
      />
    </div>
  )
}

function LessonMaterialsRow({
  courseId,
  lesson,
  onRefresh,
}: {
  courseId: number
  lesson: Lesson
  onRefresh: () => void
}) {
  const fileInput = useRef<HTMLInputElement>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [removing, setRemoving] = useState<LessonMaterial | null>(null)

  const uploadMutation = useMutation<LessonMaterial, ApiError, File>({
    mutationFn: (file) => uploadLessonMaterial(courseId, lesson.id, file),
    onSuccess: () => {
      onRefresh()
      if (fileInput.current) fileInput.current.value = ''
      setUploadError(null)
    },
    onError: (err) => setUploadError(err.message),
  })

  const removeMutation = useMutation<LessonMaterial, ApiError, number>({
    mutationFn: (materialId) => deactivateLessonMaterial(courseId, lesson.id, materialId),
    onSuccess: () => {
      onRefresh()
      setRemoving(null)
    },
    onError: (err) => setUploadError(err.message),
  })

  // The admin lessons endpoint already filters materials by is_active,
  // so what we receive here is the live set.
  const activeMaterials = lesson.materials

  return (
    <div className="mt-4 rounded-lg border border-slate-100 bg-slate-50 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Materials</p>
        <label className="inline-flex cursor-pointer items-center gap-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700">
          <Upload className="size-3.5" aria-hidden="true" />
          {uploadMutation.isPending ? 'Uploading…' : 'Upload file'}
          <input
            ref={fileInput}
            type="file"
            className="hidden"
            accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.txt"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) uploadMutation.mutate(file)
            }}
          />
        </label>
      </div>

      {uploadError && (
        <p role="alert" className="mt-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
          {uploadError}
        </p>
      )}

      {activeMaterials.length === 0 ? (
        <p className="mt-2 text-xs text-slate-400">No materials attached.</p>
      ) : (
        <ul className="mt-2 divide-y divide-slate-200">
          {activeMaterials.map((m) => (
            <li
              key={m.id}
              className="flex items-center justify-between gap-3 py-2 text-sm"
            >
              <span className="min-w-0 truncate text-slate-700">
                {m.original_filename}{' '}
                <span className="text-xs text-slate-400">({formatFileSize(m.file_size)})</span>
              </span>
              <Button
                size="sm"
                variant="outline"
                leftIcon={<Trash2 className="size-3.5" />}
                onClick={() => setRemoving(m)}
              >
                Remove
              </Button>
            </li>
          ))}
        </ul>
      )}

      <ConfirmDialog
        isOpen={removing !== null}
        onClose={() => setRemoving(null)}
        onConfirm={() => removing && removeMutation.mutate(removing.id)}
        title="Remove this material?"
        description="It disappears from the player; the file is kept on disk but not referenced."
        confirmLabel="Remove"
        isDanger
        isLoading={removeMutation.isPending}
      />
    </div>
  )
}

// --- enrollments panel ---------------------------------------------------

function EnrollmentsPanel({ courseId }: { courseId: number }) {
  const { usersMap } = useUsersMap()
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['courses', 'admin', courseId, 'enrollments'],
    queryFn: () => listCourseEnrollments(courseId),
  })

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-14 rounded-xl" />
        ))}
      </div>
    )
  }
  if (isError) {
    return (
      <ErrorState
        title="Couldn't load enrollments"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => refetch()}
      />
    )
  }
  if (!data || data.length === 0) {
    return (
      <EmptyState
        icon={Users}
        title="No one enrolled yet"
        description="Students who enroll show up here with their progress."
      />
    )
  }
  return (
    <Table>
      <TableHead>
        <TableHeaderCell>Student</TableHeaderCell>
        <TableHeaderCell>Status</TableHeaderCell>
        <TableHeaderCell>Progress</TableHeaderCell>
        <TableHeaderCell>Enrolled</TableHeaderCell>
      </TableHead>
      <TableBody>
        {data.map((row) => (
          <TableRow key={row.id}>
            <TableCell className="font-medium text-slate-900">
              {usersMap.get(row.client_id)?.full_name ?? `#${row.client_id}`}
            </TableCell>
            <TableCell>
              <Badge variant={enrollmentStatusVariant[row.status]}>{row.status}</Badge>
            </TableCell>
            <TableCell className="w-48">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <ProgressBar value={row.progress_percent} />
                <span className="shrink-0">{row.progress_percent}%</span>
              </div>
              <p className="mt-0.5 text-xs text-slate-400">
                {row.completed_lessons}/{row.total_lessons} lessons
              </p>
            </TableCell>
            <TableCell>{formatDate(row.enrolled_at)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

