/** Dev server proxy. Vite forwards these paths to the API. */
export const devProxy = {
  '/documents': 'http://127.0.0.1:8000',
  '/chat': 'http://127.0.0.1:8000',
} as const
