import type { StoredDocument } from '@/api/documents'
import { Skeleton } from '@/components/ui/skeleton'

interface DocumentListProps {
  documents: StoredDocument[] | undefined
  isPending: boolean
  errorMessage?: string
}

/** Stored PDFs. Shows loading, the API error, an empty store, or one row per file. */
export function DocumentList({
  documents,
  isPending,
  errorMessage,
}: DocumentListProps) {
  if (errorMessage) {
    return (
      <p role="alert" className="text-destructive">
        {errorMessage}
      </p>
    )
  }

  if (isPending) {
    return (
      <output
        aria-busy="true"
        aria-label="Loading documents"
        className="block space-y-2"
      >
        <Skeleton className="h-4 w-2/3" />
        <Skeleton className="h-4 w-1/2" />
      </output>
    )
  }

  if (!documents || documents.length === 0) {
    return (
      <output className="block text-muted-foreground">No documents yet.</output>
    )
  }

  return (
    <ul aria-label="Stored documents" className="space-y-2">
      {documents.map((document) => (
        <li
          key={document.id}
          className="flex items-baseline justify-between gap-3 text-foreground"
        >
          <span className="min-w-0 truncate">{document.sourceFile}</span>
          <span className="shrink-0 text-muted-foreground">
            {document.pageCount} {document.pageCount === 1 ? 'page' : 'pages'}
          </span>
        </li>
      ))}
    </ul>
  )
}
