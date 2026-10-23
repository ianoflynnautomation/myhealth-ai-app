import { z } from 'zod'

export const UNREACHABLE = 'The API could not be reached.'

const errorEnvelope = z.object({
  error: z.object({
    message: z.string(),
  }),
})

export async function readErrorMessage(response: Response): Promise<string> {
  try {
    const parsed = errorEnvelope.safeParse(await response.json())
    if (parsed.success) {
      return parsed.data.error.message
    }
  } catch {
    // The body is not JSON.
  }
  return UNREACHABLE
}
