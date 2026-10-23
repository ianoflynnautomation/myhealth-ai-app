import { useQuery } from '@tanstack/react-query'
import { SendHorizontal } from 'lucide-react'
import { listDocuments } from '@/api/documents'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'

/** Chat page. Lists stored PDFs and will send a question to POST /chat. */
export function ChatPage() {
  const documents = useQuery({
    queryKey: ['documents'],
    queryFn: listDocuments,
  })

  return (
    <main className="mx-auto flex min-h-svh max-w-3xl flex-col justify-center p-4">
      <Card>
        <CardHeader>
          <CardTitle>
            <h1>MyHealth AI</h1>
          </CardTitle>
          <CardDescription>Ask questions about your documents.</CardDescription>
        </CardHeader>
        <CardContent className="min-h-48 space-y-3 text-sm text-muted-foreground">
          {documents.isSuccess && documents.data.length === 0 ? (
            <p>No documents yet.</p>
          ) : null}
          {documents.isSuccess && documents.data.length > 0 ? (
            <ul>
              {documents.data.map((document) => (
                <li key={document.id}>
                  {document.sourceFile} {document.pageCount}
                </li>
              ))}
            </ul>
          ) : null}
          <p>No messages yet.</p>
        </CardContent>
        <CardFooter className="gap-2">
          <Textarea
            aria-label="Message"
            placeholder="Ask a question…"
            className="resize-none"
          />
          <Button type="submit" size="icon" aria-label="Send" disabled>
            <SendHorizontal />
          </Button>
        </CardFooter>
      </Card>
    </main>
  )
}
