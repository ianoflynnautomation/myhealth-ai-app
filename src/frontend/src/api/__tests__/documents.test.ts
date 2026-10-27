import { http, HttpResponse } from 'msw'
import { listDocuments, uploadDocument } from '@/api/documents'
import { server } from '@/test/server'

const stored = {
  id: 'abc',
  sourceFile: 'example.pdf',
  pageCount: 1,
  chunkCount: 1,
}

describe('documents client', () => {
  it('the client should post the file and read the api result', async () => {
    // Given
    const uploads: { contentType: string | null; fileName: string | null }[] =
      []
    const original = globalThis.fetch.bind(globalThis)
    const fetchSpy = vi
      .spyOn(globalThis, 'fetch')
      .mockImplementation(async (input, init) => {
        if (init?.body instanceof FormData) {
          const file = init.body.get('file')
          uploads.push({
            contentType: new Headers(init.headers).get('content-type'),
            fileName: file instanceof File ? file.name : null,
          })
        }
        return original(input, init)
      })
    server.use(
      http.get('/documents', () => HttpResponse.json({ documents: [stored] })),
      http.post('/documents', () => HttpResponse.json(stored, { status: 201 })),
    )
    const file = new File(['%PDF'], 'example.pdf', { type: 'application/pdf' })

    try {
      // When
      const listed = await listDocuments()
      const uploaded = await uploadDocument(file)

      // Then
      expect(listed).toEqual([stored])
      expect(uploaded).toEqual(stored)
      expect(uploads[0]).toEqual({
        contentType: null,
        fileName: 'example.pdf',
      })

      server.use(
        http.post('/documents', () =>
          HttpResponse.json(
            {
              error: {
                code: 'UNSUPPORTED_MEDIA_TYPE',
                message: 'Upload must be a PDF.',
                details: {},
              },
            },
            { status: 415 },
          ),
        ),
      )
      await expect(uploadDocument(file)).rejects.toThrow(
        'Upload must be a PDF.',
      )

      server.use(
        http.post(
          '/documents',
          () => new HttpResponse('nope', { status: 500 }),
        ),
      )
      await expect(uploadDocument(file)).rejects.toThrow(
        'The API could not be reached.',
      )
    } finally {
      fetchSpy.mockRestore()
    }
  })
})
