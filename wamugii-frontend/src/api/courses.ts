import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type Course = components['schemas']['CourseRead']
export type CoursePublicDetail = components['schemas']['CoursePublicDetail']
export type CourseCreate = components['schemas']['CourseCreate']
export type CourseUpdate = components['schemas']['CourseUpdate']
export type CourseStatus = components['schemas']['CourseStatus']

export type Lesson = components['schemas']['LessonRead']
export type LessonCreate = components['schemas']['LessonCreate']
export type LessonUpdate = components['schemas']['LessonUpdate']
export type LessonMaterial = components['schemas']['LessonMaterialRead']

export type ClientEnrollment = components['schemas']['ClientEnrollmentRead']
export type Enrollment = components['schemas']['EnrollmentRead']
export type EnrollmentStatus = components['schemas']['EnrollmentStatus']
export type EnrollResponse = components['schemas']['EnrollResponse']
export type LessonCompleteResponse = components['schemas']['LessonCompleteResponse']
export type Certificate = components['schemas']['CertificateRead']

export const COURSE_STATUSES: CourseStatus[] = ['DRAFT', 'PUBLISHED']

// --- public catalogue -----------------------------------------------------

export async function listPublicCourses(
  params: { category?: string; search?: string } = {},
): Promise<Course[]> {
  const { data } = await apiClient.get<Course[]>('/courses', { params: { limit: 100, ...params } })
  return data
}

export async function getPublicCourse(slug: string): Promise<CoursePublicDetail> {
  const { data } = await apiClient.get<CoursePublicDetail>(`/courses/${slug}`)
  return data
}

// --- admin / staff --------------------------------------------------------

export async function listAllCourses(
  params: { include_drafts?: boolean; category?: string; search?: string } = {},
): Promise<Course[]> {
  const { data } = await apiClient.get<Course[]>('/courses', {
    params: { limit: 100, include_drafts: true, ...params },
  })
  return data
}

export async function getCourseById(courseId: number | string): Promise<Course> {
  const { data } = await apiClient.get<Course>(`/courses/by-id/${courseId}`)
  return data
}

export async function createCourse(payload: CourseCreate): Promise<Course> {
  const { data } = await apiClient.post<Course>('/courses', payload)
  return data
}

export async function updateCourse(
  courseId: number | string,
  payload: CourseUpdate,
): Promise<Course> {
  const { data } = await apiClient.patch<Course>(`/courses/${courseId}`, payload)
  return data
}

export async function deactivateCourse(courseId: number | string): Promise<Course> {
  const { data } = await apiClient.delete<Course>(`/courses/${courseId}`)
  return data
}

// --- lessons --------------------------------------------------------------

export async function listCourseLessons(courseId: number | string): Promise<Lesson[]> {
  const { data } = await apiClient.get<Lesson[]>(`/courses/${courseId}/lessons`)
  return data
}

export async function createLesson(
  courseId: number | string,
  payload: LessonCreate,
): Promise<Lesson> {
  const { data } = await apiClient.post<Lesson>(`/courses/${courseId}/lessons`, payload)
  return data
}

export async function updateLesson(
  courseId: number | string,
  lessonId: number | string,
  payload: LessonUpdate,
): Promise<Lesson> {
  const { data } = await apiClient.patch<Lesson>(
    `/courses/${courseId}/lessons/${lessonId}`,
    payload,
  )
  return data
}

export async function deactivateLesson(
  courseId: number | string,
  lessonId: number | string,
): Promise<Lesson> {
  const { data } = await apiClient.delete<Lesson>(`/courses/${courseId}/lessons/${lessonId}`)
  return data
}

export async function uploadLessonMaterial(
  courseId: number | string,
  lessonId: number | string,
  file: File,
): Promise<LessonMaterial> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<LessonMaterial>(
    `/courses/${courseId}/lessons/${lessonId}/materials`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function deactivateLessonMaterial(
  courseId: number | string,
  lessonId: number | string,
  materialId: number | string,
): Promise<LessonMaterial> {
  const { data } = await apiClient.delete<LessonMaterial>(
    `/courses/${courseId}/lessons/${lessonId}/materials/${materialId}`,
  )
  return data
}

export async function listCourseEnrollments(
  courseId: number | string,
): Promise<Enrollment[]> {
  const { data } = await apiClient.get<Enrollment[]>(`/courses/${courseId}/enrollments`)
  return data
}

// --- client ---------------------------------------------------------------

export async function listMyEnrollments(): Promise<ClientEnrollment[]> {
  const { data } = await apiClient.get<ClientEnrollment[]>('/client/courses')
  return data
}

export async function enrollInCourse(courseId: number | string): Promise<EnrollResponse> {
  const { data } = await apiClient.post<EnrollResponse>(`/client/courses/${courseId}/enroll`)
  return data
}

export async function listMyLessons(courseId: number | string): Promise<Lesson[]> {
  const { data } = await apiClient.get<Lesson[]>(`/client/courses/${courseId}/lessons`)
  return data
}

export async function getMyLesson(
  courseId: number | string,
  lessonId: number | string,
): Promise<Lesson> {
  const { data } = await apiClient.get<Lesson>(
    `/client/courses/${courseId}/lessons/${lessonId}`,
  )
  return data
}

/**
 * The certificate for a completed course.
 *
 * 403 until every lesson is complete, and the same 404/403 enrollment gate as
 * the lesson endpoints otherwise -- nothing is stored server-side, so this is
 * recomputed each time it is asked for.
 */
export async function getCertificate(courseId: number | string): Promise<Certificate> {
  const { data } = await apiClient.get<Certificate>(
    `/client/courses/${courseId}/certificate`,
  )
  return data
}

export async function markLessonComplete(
  courseId: number | string,
  lessonId: number | string,
): Promise<LessonCompleteResponse> {
  const { data } = await apiClient.post<LessonCompleteResponse>(
    `/client/courses/${courseId}/lessons/${lessonId}/complete`,
  )
  return data
}

/**
 * Download a lesson material.
 *
 * Same blob-through-the-authenticated-client approach as the other downloads:
 * a plain <a href> would arrive without the Bearer token.
 */
export async function downloadLessonMaterial(
  courseId: number | string,
  lessonId: number | string,
  materialId: number | string,
  filename: string,
): Promise<void> {
  const response = await apiClient.get(
    `/client/courses/${courseId}/lessons/${lessonId}/materials/${materialId}/download`,
    { responseType: 'blob' },
  )
  const url = URL.createObjectURL(response.data as Blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
