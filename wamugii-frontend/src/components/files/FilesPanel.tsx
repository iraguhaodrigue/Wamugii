import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, FileText, Paperclip, Pencil, Trash2, Upload } from 'lucide-react'
import {
  deleteProjectFile,
  downloadProjectFile,
  listProjectFiles,
  updateProjectFile,
  uploadProjectFile,
  type FileCategory,
  type ProjectFileListItem,
} from '@/api/projectFiles'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import type { ApiError } from '@/lib/apiClient'
import {
  Badge,
  Button,
  ConfirmDialog,
  EmptyState,
  ErrorState,
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
import { formatDate, formatEnumLabel, formatFileSize } from '@/utils/format'

const FILE_CATEGORIES: FileCategory[] = ['REQUIREMENT', 'PROPOSAL', 'DESIGN', 'DOCUMENT', 'REPORT', 'IMAGE', 'OTHER']
const categoryOptions = FILE_CATEGORIES.map((c) => ({ value: c, label: formatEnumLabel(c) }))

export function FilesPanel({ projectId }: { projectId: number }) {
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const canDelete = isAdmin // STAFF cannot delete files (backend-enforced); CLIENT-only-own-uploads doesn't apply here.
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { usersMap } = useUsersMap()

  const [categoryFilter, setCategoryFilter] = useState<FileCategory | ''>('')
  const [uploadCategory, setUploadCategory] = useState<FileCategory>('DOCUMENT')
  const [uploadDescription, setUploadDescription] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [editingFile, setEditingFile] = useState<ProjectFileListItem | null>(null)
  const [pendingDelete, setPendingDelete] = useState<ProjectFileListItem | null>(null)
  const [downloadingId, setDownloadingId] = useState<number | null>(null)

  const filesQuery = useQuery({
    queryKey: ['projects', projectId, 'files', { category: categoryFilter }],
    queryFn: () => listProjectFiles(projectId, { category: categoryFilter || undefined }),
  })

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'files'] })
  }

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!selectedFile) throw new Error('No file selected')
      return uploadProjectFile(projectId, {
        file: selectedFile,
        category: uploadCategory,
        description: uploadDescription || undefined,
      })
    },
    onSuccess: () => {
      setSelectedFile(null)
      setUploadDescription('')
      setUploadCategory('DOCUMENT')
      setUploadError(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      invalidate()
    },
    onError: (err: ApiError) => setUploadError(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, category, description }: { id: number; category: FileCategory; description: string }) =>
      updateProjectFile(projectId, id, { category, description: description || null }),
    onSuccess: () => {
      setEditingFile(null)
      invalidate()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteProjectFile(projectId, id),
    onSuccess: () => {
      setPendingDelete(null)
      invalidate()
    },
  })

  async function handleDownload(file: ProjectFileListItem) {
    setDownloadingId(file.id)
    try {
      await downloadProjectFile(projectId, file.id, file.original_filename)
    } finally {
      setDownloadingId(null)
    }
  }

  const files = filesQuery.data ?? []

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-200 bg-panel p-5 shadow-sm">
        <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
          <Upload className="size-4" aria-hidden="true" />
          Upload a file
        </h3>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            uploadMutation.mutate()
          }}
          className="mt-4 space-y-3"
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-slate-700 file:mr-3 file:rounded-lg file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-brand-700 hover:file:bg-brand-100"
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <Select
              label="Category"
              options={categoryOptions}
              value={uploadCategory}
              onChange={(e) => setUploadCategory(e.target.value as FileCategory)}
            />
            <Textarea
              label="Description"
              rows={1}
              hint="Optional"
              value={uploadDescription}
              onChange={(e) => setUploadDescription(e.target.value)}
            />
          </div>
          {uploadError && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {uploadError}
            </p>
          )}
          <Button type="submit" size="sm" isLoading={uploadMutation.isPending} disabled={!selectedFile}>
            Upload
          </Button>
        </form>
      </div>

      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Files</h3>
        <Select
          aria-label="Filter by category"
          options={[{ value: '', label: 'All categories' }, ...categoryOptions]}
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value as FileCategory | '')}
          className="w-48"
        />
      </div>

      {filesQuery.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-12 rounded-lg" />
          ))}
        </div>
      ) : filesQuery.isError ? (
        <ErrorState title="Couldn't load files" message="Please try again." onRetry={() => filesQuery.refetch()} />
      ) : files.length === 0 ? (
        <EmptyState icon={Paperclip} title="No files yet" description="Uploaded documents and assets will show up here." />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>File</TableHeaderCell>
            <TableHeaderCell>Category</TableHeaderCell>
            <TableHeaderCell>Size</TableHeaderCell>
            <TableHeaderCell>Uploaded by</TableHeaderCell>
            <TableHeaderCell>Date</TableHeaderCell>
            <TableHeaderCell>
              <span className="sr-only">Actions</span>
            </TableHeaderCell>
          </TableHead>
          <TableBody>
            {files.map((file) => (
              <TableRow key={file.id}>
                <TableCell className="max-w-xs">
                  <div className="flex items-center gap-2">
                    <FileText className="size-4 shrink-0 text-slate-400" aria-hidden="true" />
                    <span className="truncate font-medium text-slate-900">{file.original_filename}</span>
                  </div>
                  {file.description && <p className="mt-0.5 truncate text-xs text-slate-500">{file.description}</p>}
                </TableCell>
                <TableCell>
                  <Badge variant="neutral">{formatEnumLabel(file.category)}</Badge>
                </TableCell>
                <TableCell className="whitespace-nowrap">{formatFileSize(file.file_size)}</TableCell>
                <TableCell>{usersMap.get(file.uploaded_by)?.full_name ?? `#${file.uploaded_by}`}</TableCell>
                <TableCell className="whitespace-nowrap">{formatDate(file.created_at)}</TableCell>
                <TableCell>
                  <div className="flex items-center justify-end gap-1">
                    <button
                      type="button"
                      onClick={() => handleDownload(file)}
                      disabled={downloadingId === file.id}
                      aria-label="Download"
                      className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 disabled:opacity-50"
                    >
                      <Download className="size-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingFile(file)}
                      aria-label="Edit metadata"
                      className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
                    >
                      <Pencil className="size-4" />
                    </button>
                    {canDelete && (
                      <button
                        type="button"
                        onClick={() => setPendingDelete(file)}
                        aria-label="Delete file"
                        className="rounded-lg p-2 text-slate-500 hover:bg-red-50 hover:text-red-600"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Modal isOpen={editingFile !== null} onClose={() => setEditingFile(null)} title="Edit file metadata" size="sm">
        {editingFile && (
          <EditFileForm
            file={editingFile}
            isSaving={updateMutation.isPending}
            onCancel={() => setEditingFile(null)}
            onSave={(category, description) => updateMutation.mutate({ id: editingFile.id, category, description })}
          />
        )}
      </Modal>

      <ConfirmDialog
        isOpen={pendingDelete !== null}
        onClose={() => setPendingDelete(null)}
        onConfirm={() => pendingDelete && deleteMutation.mutate(pendingDelete.id)}
        title="Delete this file?"
        description={pendingDelete ? `"${pendingDelete.original_filename}" will be removed from the project.` : undefined}
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}

function EditFileForm({
  file,
  onSave,
  onCancel,
  isSaving,
}: {
  file: ProjectFileListItem
  onSave: (category: FileCategory, description: string) => void
  onCancel: () => void
  isSaving: boolean
}) {
  const [category, setCategory] = useState<FileCategory>(file.category)
  const [description, setDescription] = useState(file.description ?? '')

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        onSave(category, description)
      }}
      className="space-y-4"
    >
      <Select
        label="Category"
        options={categoryOptions}
        value={category}
        onChange={(e) => setCategory(e.target.value as FileCategory)}
      />
      <Textarea label="Description" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isSaving}>
          Save
        </Button>
      </div>
    </form>
  )
}
