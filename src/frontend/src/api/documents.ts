import { z } from 'zod'
import { readErrorMessage, UNREACHABLE } from '@/api/errors'

export const documentSchema = z.object({
  id: z.string(),
  sourceFile: z.string(),
  pageCount: z.number().int().nonnegative(),
  chunkCount: z.number().int().nonnegative(),
})

export type StoredDocument = z.infer<typeof documentSchema>

const documentListSchema = z.object({
  documents: z.array(documentSchema),
})

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return null
  }
}

async function fetchApi(path: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(path, init)
  } catch {
    throw new Error(UNREACHABLE)
  }
}

export async function listDocuments(): Promise<StoredDocument[]> {
  const response = await fetchApi('/documents')
  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }
  const parsed = documentListSchema.safeParse(await readJson(response))
  if (!parsed.success) {
    throw new Error(UNREACHABLE)
  }
  return parsed.data.documents
}

export async function uploadDocument(file: File): Promise<StoredDocument> {
  const body = new FormData()
  body.append('file', file)
  const response = await fetchApi('/documents', { method: 'POST', body })
  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }
  const parsed = documentSchema.safeParse(await readJson(response))
  if (!parsed.success) {
    throw new Error(UNREACHABLE)
  }
  return parsed.data
}
