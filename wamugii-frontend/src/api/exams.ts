import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

type S = components['schemas']
export type ExamOverview = S['ExamOverview']
export type ExamSession = S['ExamSession']
export type ExamQuestionPublic = S['ExamQuestionPublic']
export type ExamResult = S['ExamResult']
export type ExamEventResult = S['ExamEventResult']
export type ExamQuestionKind = S['ExamQuestionKind']
export type ExamQuestionAdmin = S['ExamQuestionAdmin']
export type ExamQuestionWrite = S['ExamQuestionWrite']
export type ExamBankSummary = S['ExamBankSummary']
export type ExamSettings = S['ExamSettings']
export type ExamAttemptAdmin = S['ExamAttemptAdmin']
export type InstructorRead = S['InstructorRead']
export type InstructorCourse = S['InstructorCourseRead']
export type LessonQuestion = S['LessonQuestionRead']
export type AiDraftResponse = S['AiDraftResponse']
/** An answer as stored: option id(s) for choice questions, text for fill-in. */
export type ExamAnswer = number | number[] | string | null

// --- student: final exam ------------------------------------------------------

export async function getExamOverview(courseId: number | string): Promise<ExamOverview> {
  const { data } = await apiClient.get<ExamOverview>(`/client/courses/${courseId}/exam`)
  return data
}

export async function startExam(courseId: number | string): Promise<ExamSession> {
  const { data } = await apiClient.post<ExamSession>(`/client/courses/${courseId}/exam/start`)
  return data
}

export async function saveExamAnswers(attemptId: number, answers: Record<string, ExamAnswer>): Promise<void> {
  await apiClient.put(`/client/exam-attempts/${attemptId}/answers`, { answers })
}

export async function reportExamEvent(
  attemptId: number,
  type: 'leave' | 'notice',
  detail: string,
): Promise<ExamEventResult> {
  const { data } = await apiClient.post<ExamEventResult>(`/client/exam-attempts/${attemptId}/events`, { type, detail })
  return data
}

export async function submitExam(attemptId: number, answers: Record<string, ExamAnswer>): Promise<ExamResult> {
  const { data } = await apiClient.post<ExamResult>(`/client/exam-attempts/${attemptId}/submit`, { answers })
  return data
}

export async function getExamResult(attemptId: number): Promise<ExamResult> {
  const { data } = await apiClient.get<ExamResult>(`/client/exam-attempts/${attemptId}/result`)
  return data
}

// --- student: lesson Q&A ----------------------------------------------------------

export async function listLessonQuestions(courseId: number, lessonId: number): Promise<LessonQuestion[]> {
  const { data } = await apiClient.get<LessonQuestion[]>(`/client/courses/${courseId}/lessons/${lessonId}/questions`)
  return data
}

export async function askLessonQuestion(courseId: number, lessonId: number, body: string): Promise<LessonQuestion> {
  const { data } = await apiClient.post<LessonQuestion>(`/client/courses/${courseId}/lessons/${lessonId}/questions`, { body })
  return data
}

export async function replyAsStudent(courseId: number, questionId: number, body: string): Promise<LessonQuestion> {
  const { data } = await apiClient.post<LessonQuestion>(`/client/courses/${courseId}/questions/${questionId}/answers`, { body })
  return data
}

// --- course staff: exam bank, results ----------------------------------------------

export async function getExamBank(courseId: number | string): Promise<ExamBankSummary> {
  const { data } = await apiClient.get<ExamBankSummary>(`/courses/${courseId}/exam`)
  return data
}

export async function updateExamSettings(courseId: number | string, settings: Partial<ExamSettings>): Promise<ExamSettings> {
  const { data } = await apiClient.put<ExamSettings>(`/courses/${courseId}/exam/settings`, settings)
  return data
}

export async function addExamQuestions(courseId: number | string, items: ExamQuestionWrite[]): Promise<ExamQuestionAdmin[]> {
  const { data } = await apiClient.post<ExamQuestionAdmin[]>(`/courses/${courseId}/exam/questions`, items)
  return data
}

export async function editExamQuestion(courseId: number | string, id: number, item: ExamQuestionWrite): Promise<ExamQuestionAdmin> {
  const { data } = await apiClient.put<ExamQuestionAdmin>(`/courses/${courseId}/exam/questions/${id}`, item)
  return data
}

export async function deleteExamQuestion(courseId: number | string, id: number): Promise<void> {
  await apiClient.delete(`/courses/${courseId}/exam/questions/${id}`)
}

export async function aiDraftQuestions(
  courseId: number | string,
  body: { lesson_ids?: number[]; count: number; kinds?: ExamQuestionKind[] },
): Promise<AiDraftResponse> {
  const { data } = await apiClient.post<AiDraftResponse>(`/courses/${courseId}/exam/ai-draft`, body)
  return data
}

export async function listExamAttempts(courseId: number | string): Promise<ExamAttemptAdmin[]> {
  const { data } = await apiClient.get<ExamAttemptAdmin[]>(`/courses/${courseId}/exam/attempts`)
  return data
}

export async function grantExtraAttempt(courseId: number | string, enrollmentId: number): Promise<void> {
  await apiClient.post(`/courses/${courseId}/enrollments/${enrollmentId}/exam/extra-attempt`)
}

// --- instructors --------------------------------------------------------------------------

export async function listInstructors(courseId: number | string): Promise<InstructorRead[]> {
  const { data } = await apiClient.get<InstructorRead[]>(`/courses/${courseId}/instructors`)
  return data
}

export async function assignInstructor(courseId: number | string, email: string): Promise<InstructorRead> {
  const { data } = await apiClient.post<InstructorRead>(`/courses/${courseId}/instructors`, { email })
  return data
}

export async function removeInstructor(courseId: number | string, userId: number): Promise<void> {
  await apiClient.delete(`/courses/${courseId}/instructors/${userId}`)
}

export async function listMyTeachingCourses(): Promise<InstructorCourse[]> {
  const { data } = await apiClient.get<InstructorCourse[]>('/instructor/courses')
  return data
}

export async function listMyStudentQuestions(unanswered = false): Promise<LessonQuestion[]> {
  const { data } = await apiClient.get<LessonQuestion[]>('/instructor/questions', { params: { unanswered } })
  return data
}

export async function listCourseQuestions(courseId: number | string, unanswered = false): Promise<LessonQuestion[]> {
  const { data } = await apiClient.get<LessonQuestion[]>(`/courses/${courseId}/questions`, { params: { unanswered } })
  return data
}

export async function answerQuestion(courseId: number | string, questionId: number, body: string): Promise<LessonQuestion> {
  const { data } = await apiClient.post<LessonQuestion>(`/courses/${courseId}/questions/${questionId}/answers`, { body })
  return data
}

export async function hideQuestion(courseId: number | string, questionId: number): Promise<void> {
  await apiClient.delete(`/courses/${courseId}/questions/${questionId}`)
}
