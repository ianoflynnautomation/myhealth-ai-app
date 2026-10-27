import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { SendHorizontal } from 'lucide-react'
import { askQuestion } from '@/api/chat'
import {
  listDocuments,
  uploadDocument,
  type StoredDocument,
} from '@/api/documents'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { DocumentList } from '@/features/chat/DocumentList'
import { Transcript, type TranscriptTurn } from '@/features/chat/Transcript'

/** Chat page. Lists stored PDFs and will send a question to POST /chat. */
export function ChatPage() {
  const queryClient = useQueryClient()
  const documents = useQuery({
    queryKey: ['documents'],
    queryFn: listDocuments,
  })
  const [message, setMessage] = useState('')
  const [turns, setTurns] = useState<TranscriptTurn[]>([])
  const upload = useMutation({
    mutationFn: uploadDocument,
    onSuccess: (document) => {
      queryClient.setQueryData<StoredDocument[]>(['documents'], (current) => {
        const list = current ?? []
        if (list.some((item) => item.id === document.id)) {
          return list
        }
        return [...list, document]
      })
    },
  })
  const chat = useMutation({
    mutationFn: askQuestion,
    onSuccess: (answer, question) => {
      setTurns((current) => [...current, { question, answer }])
      setMessage('')
    },
  })

  function sendQuestion() {
    const question = message.trim()
    if (question === '' || chat.isPending) {
      return
    }
    chat.mutate(question)
  }

  return (
    <main className="mx-auto flex min-h-svh max-w-3xl flex-col justify-center p-4">
      <Card>
        <CardHeader>
          <CardTitle>
            <h1 className="text-xl leading-snug">MyHealth AI</h1>
          </CardTitle>
          <CardDescription>Ask questions about your documents.</CardDescription>
        </CardHeader>
        <CardContent className="min-h-48 space-y-3 text-sm">
          <div className="space-y-2">
            <Label htmlFor="upload-pdf" className="text-foreground">
              Upload PDF
            </Label>
            <Input
              id="upload-pdf"
              type="file"
              accept="application/pdf,.pdf"
              disabled={upload.isPending}
              onChange={(event) => {
                const file = event.currentTarget.files?.[0]
                event.currentTarget.value = ''
                if (file) {
                  upload.mutate(file)
                }
              }}
            />
          </div>
          {upload.isError ? (
            <p role="alert" className="text-destructive">
              {upload.error.message}
            </p>
          ) : null}
          <DocumentList
            documents={documents.data}
            isPending={documents.isPending}
            errorMessage={
              documents.isError ? documents.error.message : undefined
            }
          />
          <Transcript turns={turns} />
          {chat.isError ? (
            <p role="alert" className="text-destructive">
              {chat.error.message}
            </p>
          ) : null}
        </CardContent>
        <CardFooter className="gap-2">
          <Textarea
            aria-label="Message"
            placeholder="Ask a question…"
            value={message}
            onChange={(event) => {
              setMessage(event.target.value)
            }}
            className="min-w-0 flex-1 resize-none"
          />
          <Button
            type="submit"
            size="icon"
            aria-label="Send"
            disabled={message.trim() === '' || chat.isPending}
            onClick={sendQuestion}
            className="shrink-0"
          >
            <SendHorizontal />
          </Button>
        </CardFooter>
      </Card>
    </main>
  )
}
