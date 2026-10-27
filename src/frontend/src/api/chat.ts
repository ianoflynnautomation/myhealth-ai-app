import { z } from 'zod'
import { readErrorMessage, UNREACHABLE } from '@/api/errors'

export const citationSchema = z.object({
  id: z.string(),
  sourceFile: z.string(),
  sourcePage: z.number().int().positive(),
  content: z.string(),
})

export const chatResponseSchema = z.object({
  outputText: z.string(),
  citations: z.array(citationSchema),
})

export type ChatAnswer = z.infer<typeof chatResponseSchema>

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return null
  }
}

/** Ask the current question. Earlier questions stay on screen and are not sent again. */
export async function askQuestion(question: string): Promise<ChatAnswer> {
  let response: Response
  try {
    response = await fetch('/chat', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        messages: [{ role: 'user', content: question }],
      }),
    })
  } catch {
    throw new Error(UNREACHABLE)
  }
  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }
  const parsed = chatResponseSchema.safeParse(await readJson(response))
  if (!parsed.success) {
    throw new Error(UNREACHABLE)
  }
  return parsed.data
}
