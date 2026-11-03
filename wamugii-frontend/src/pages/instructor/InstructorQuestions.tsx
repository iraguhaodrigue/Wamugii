import { useQuery } from '@tanstack/react-query'
import { listMyStudentQuestions, listMyTeachingCourses } from '@/api/exams'
import { usePageTitle } from '@/context/PageTitleContext'
import { QuestionsInbox } from '@/components/courses/admin/CourseStaffPanels'

/** Every student question across the instructor's courses, newest first. */
export function InstructorQuestions() {
  usePageTitle('Student questions')
  const courses = useQuery({ queryKey: ['instructor', 'courses'], queryFn: listMyTeachingCourses })
  const titles = Object.fromEntries((courses.data ?? []).map((c) => [c.id, c.title]))
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Student questions</h1>
        <p className="mt-1 text-sm text-slate-500">Questions students asked under your lessons. They get an email when you answer.</p>
      </div>
      <QuestionsInbox load={(u) => listMyStudentQuestions(u)} queryKey={['instructor', 'questions']} courseTitles={titles} />
    </div>
  )
}
