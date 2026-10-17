import { SendHorizontal } from 'lucide-react'
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

/** Placeholder chat shell. Wire up to POST /chat once the backend exists. */
export function ChatPage() {
  return (
    <main className="mx-auto flex min-h-svh max-w-3xl flex-col justify-center p-4">
      <Card>
        <CardHeader>
          <CardTitle>
            <h1>MyHealth AI</h1>
          </CardTitle>
          <CardDescription>Ask questions about your documents.</CardDescription>
        </CardHeader>
        <CardContent className="min-h-48 text-sm text-muted-foreground">
          No messages yet.
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
