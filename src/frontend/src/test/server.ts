import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

/** MSW server for tests. Add default handlers here; override per test with server.use(). */
export const server = setupServer(
  http.get('/documents', () => HttpResponse.json({ documents: [] })),
)
