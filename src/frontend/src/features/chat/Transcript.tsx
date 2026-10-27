import type { ChatAnswer } from '@/api/chat'

export interface TranscriptTurn {
  question: string
  answer: ChatAnswer
}

/** Questions and answers. Text only, including the quoted citation. */
export function Transcript({ turns }: { turns: TranscriptTurn[] }) {
  if (turns.length === 0) {
    return (
      <output className="block text-muted-foreground">No messages yet.</output>
    )
  }

  return (
    <ol aria-label="Messages" className="space-y-3">
      {turns.map((turn, index) => (
        <li key={`${turn.question}-${index}`} className="space-y-2">
          <p className="text-foreground">{turn.question}</p>
          <p>{turn.answer.outputText}</p>
          {turn.answer.citations.length > 0 ? (
            <ul aria-label="Citations" className="space-y-2">
              {turn.answer.citations.map((citation) => (
                <li key={citation.id}>
                  <span className="text-foreground">{citation.sourceFile}</span>{' '}
                  page {citation.sourcePage}
                  <span className="mt-1 block">{citation.content}</span>
                </li>
              ))}
            </ul>
          ) : null}
        </li>
      ))}
    </ol>
  )
}
