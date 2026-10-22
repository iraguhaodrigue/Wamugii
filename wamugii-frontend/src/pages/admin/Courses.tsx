import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, Plus } from 'lucide-react'
import {
  createCourse,
  listAllCourses,
  type Course,
  type CourseCreate,
} from '@/api/courses'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
  EmptyState,
  ErrorState,
  Input,
  Modal,
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
import { formatMoney } from '@/utils/format'
import { courseStatusVariant } from '@/utils/statusBadge'

const EMPTY_DRAFT: CourseCreate = {
  title: '',
  description: '',
  is_free: true,
  price: null,
  status: 'DRAFT',
  display_order: 0,
}

export function AdminCourses() {
  usePageTitle('Courses')
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [draft, setDraft] = useState<CourseCreate>(EMPTY_DRAFT)
  const [formError, setFormError] = useState<string | null>(null)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['courses', 'admin'],
    queryFn: () => listAllCourses(),
  })

  const createMutation = useMutation<Course, ApiError, CourseCreate>({
    mutationFn: (payload) => createCourse(payload),
    onSuccess: (course) => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setIsCreateOpen(false)
      setDraft(EMPTY_DRAFT)
      setFormError(null)
      navigate(paths.admin.courseDetail(course.id))
    },
    onError: (err) => setFormError(err.message),
  })

  function handleCreate() {
    const payload: CourseCreate = {
      ...draft,
      title: draft.title.trim(),
      description: (draft.description ?? '').trim(),
      // Backend normalises `price` to null on free, but send cleanly either way.
      price: draft.is_free ? null : (draft.price ?? null),
    }
    createMutation.mutate(payload)
  }

  const canSubmit =
    draft.title.trim().length > 0 &&
    (draft.is_free || Boolean(draft.price && Number(draft.price) > 0))

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Create and manage training courses. Only PUBLISHED active courses appear in the public
          catalogue.
        </p>
        <Button
          size="sm"
          leftIcon={<Plus className="size-4" />}
          onClick={() => {
            setDraft(EMPTY_DRAFT)
            setFormError(null)
            setIsCreateOpen(true)
          }}
        >
          New course
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load courses"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !data || data.length === 0 ? (
        <EmptyState
          icon={GraduationCap}
          title="No courses yet"
          description="Create the first course to open your training catalogue."
        />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>Course</TableHeaderCell>
            <TableHeaderCell>Price</TableHeaderCell>
            <TableHeaderCell>Lessons</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
          </TableHead>
          <TableBody>
            {data.map((course) => (
              <TableRow
                key={course.id}
                clickable
                onClick={() => navigate(paths.admin.courseDetail(course.id))}
              >
                <TableCell className="font-medium text-slate-900">
                  {course.title}
                  {!course.is_active && (
                    <span className="ml-2 text-xs text-slate-400">(deleted)</span>
                  )}
                </TableCell>
                <TableCell>
                  {course.is_free ? (
                    <Badge variant="success">Free</Badge>
                  ) : (
                    (formatMoney(course.price) ?? '—')
                  )}
                </TableCell>
                <TableCell>{course.lesson_count}</TableCell>
                <TableCell>
                  <Badge variant={courseStatusVariant[course.status]}>{course.status}</Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Create a course"
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="Title"
            required
            value={draft.title}
            onChange={(e) => setDraft((d) => ({ ...d, title: e.target.value }))}
          />
          <Textarea
            label="Description"
            rows={4}
            value={draft.description ?? ''}
            onChange={(e) => setDraft((d) => ({ ...d, description: e.target.value }))}
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <Select
              label="Pricing"
              options={[
                { value: 'free', label: 'Free' },
                { value: 'paid', label: 'Paid' },
              ]}
              value={draft.is_free ? 'free' : 'paid'}
              onChange={(e) =>
                setDraft((d) => ({
                  ...d,
                  is_free: e.target.value === 'free',
                  price: e.target.value === 'free' ? null : d.price,
                }))
              }
            />
            {!draft.is_free && (
              <Input
                label="Price (RWF)"
                type="number"
                min="0"
                step="0.01"
                required
                value={draft.price ?? ''}
                onChange={(e) => setDraft((d) => ({ ...d, price: e.target.value || null }))}
              />
            )}
          </div>
          <Select
            label="Status"
            options={[
              { value: 'DRAFT', label: 'Draft (hidden from catalogue)' },
              { value: 'PUBLISHED', label: 'Published (publicly listed)' },
            ]}
            value={draft.status}
            onChange={(e) =>
              setDraft((d) => ({ ...d, status: e.target.value as CourseCreate['status'] }))
            }
          />

          {formError && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {formError}
            </p>
          )}

          <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
            <Button
              variant="outline"
              onClick={() => setIsCreateOpen(false)}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              disabled={!canSubmit}
              isLoading={createMutation.isPending}
              onClick={handleCreate}
            >
              Create course
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
