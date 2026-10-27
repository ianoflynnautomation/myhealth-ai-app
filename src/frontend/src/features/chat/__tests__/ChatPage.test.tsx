import { screen, cleanup, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { ChatPage } from '@/features/chat/ChatPage'
import { renderWithProviders } from '@/test/render'
import { server } from '@/test/server'

const stored = {
  id: 'abc',
  sourceFile: 'example.pdf',
  pageCount: 1,
  chunkCount: 1,
}

describe('ChatPage', () => {
  it('the page should show that documents are loading', async () => {
    // Given
    let release: () => void = () => {
      throw new Error('The document list was not held.')
    }
    const pending = new Promise<void>((resolve) => {
      release = resolve
    })
    server.use(
      http.get('/documents', async () => {
        await pending
        return HttpResponse.json({ documents: [] })
      }),
    )

    // When
    renderWithProviders(<ChatPage />)

    // Then
    expect(
      screen.getByRole('status', { name: 'Loading documents' }),
    ).toHaveAttribute('aria-busy', 'true')
    expect(screen.queryByText('No documents yet.')).not.toBeInTheDocument()
    release()
    expect(await screen.findByText('No documents yet.')).toBeInTheDocument()
  })

  it('the page should list a stored pdf', async () => {
    // Given
    server.use(
      http.get('/documents', () => HttpResponse.json({ documents: [] })),
    )

    // When
    renderWithProviders(<ChatPage />)

    // Then
    expect(await screen.findByText('No documents yet.')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'MyHealth AI' }),
    ).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'Message' })).toBeInTheDocument()

    cleanup()
    server.use(
      http.get('/documents', () => HttpResponse.json({ documents: [stored] })),
    )
    renderWithProviders(<ChatPage />)

    const item = await screen.findByRole('listitem')
    expect(item).toHaveTextContent('example.pdf')
    expect(item).toHaveTextContent('1')
  })

  it('the page should not call an empty store when the list fails', async () => {
    // Given
    server.use(http.get('/documents', () => HttpResponse.error()))

    // When
    renderWithProviders(<ChatPage />)

    // Then
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'The API could not be reached.',
    )
    expect(screen.queryByText('No documents yet.')).not.toBeInTheDocument()
  })

  it('the page should show an uploaded pdf once', async () => {
    // Given
    const user = userEvent.setup()
    let posts = 0
    server.use(
      http.get('/documents', () => HttpResponse.json({ documents: [] })),
      http.post('/documents', () => {
        posts += 1
        return HttpResponse.json(stored, { status: posts === 1 ? 201 : 200 })
      }),
    )
    renderWithProviders(<ChatPage />)
    expect(await screen.findByText('No documents yet.')).toBeInTheDocument()
    const input = screen.getByLabelText('Upload PDF')

    // When
    await user.upload(
      input,
      new File(['%PDF'], 'example.pdf', { type: 'application/pdf' }),
    )
    await screen.findByRole('listitem')
    await user.upload(
      input,
      new File(['%PDF'], 'example.pdf', { type: 'application/pdf' }),
    )
    await waitFor(() => {
      expect(posts).toBe(2)
    })

    // Then
    expect(screen.getAllByRole('listitem')).toHaveLength(1)
    const item = screen.getByRole('listitem')
    expect(item).toHaveTextContent('example.pdf')
    expect(item).toHaveTextContent('1')
  })

  it('the page should show the upload error', async () => {
    // Given
    const user = userEvent.setup()
    const listed = {
      id: 'listed',
      sourceFile: 'notes.pdf',
      pageCount: 2,
      chunkCount: 2,
    }
    server.use(
      http.get('/documents', () => HttpResponse.json({ documents: [listed] })),
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
    renderWithProviders(<ChatPage />)
    expect(await screen.findByRole('listitem')).toHaveTextContent('notes.pdf')

    // When
    await user.upload(
      screen.getByLabelText('Upload PDF'),
      new File(['nope'], 'scan.pdf', { type: 'application/pdf' }),
    )

    // Then
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Upload must be a PDF.',
    )
    expect(screen.getAllByRole('listitem')).toHaveLength(1)
    expect(screen.getByRole('listitem')).toHaveTextContent('notes.pdf')
    expect(screen.getByRole('listitem')).toHaveTextContent('2')
  })

  it('the page should not send a blank question', async () => {
    // Given
    const user = userEvent.setup()
    let posts = 0
    server.use(
      http.post('/chat', () => {
        posts += 1
        return HttpResponse.json({ outputText: 'nope', citations: [] })
      }),
    )
    renderWithProviders(<ChatPage />)
    const send = screen.getByRole('button', { name: 'Send' })
    const message = screen.getByRole('textbox', { name: 'Message' })
    expect(send).toBeDisabled()

    // When
    await user.type(message, '   ')

    // Then
    expect(send).toBeDisabled()
    await user.clear(message)
    expect(send).toBeDisabled()
    expect(posts).toBe(0)
  })

  it('the page should show the cited page', async () => {
    // Given
    const user = userEvent.setup()
    const question = 'What is the DemoMarker value?'
    const sentence = 'DemoMarker value is 10 units.'
    let body: unknown
    server.use(
      http.post('/chat', async ({ request }) => {
        body = await request.json()
        return HttpResponse.json({
          outputText: sentence,
          citations: [
            {
              id: 'abc:1',
              sourceFile: 'example.pdf',
              sourcePage: 1,
              content: sentence,
            },
          ],
        })
      }),
    )
    renderWithProviders(<ChatPage />)

    // When
    await user.type(screen.getByRole('textbox', { name: 'Message' }), question)
    await user.click(screen.getByRole('button', { name: 'Send' }))

    // Then
    expect(await screen.findByText(question)).toBeInTheDocument()
    expect(body).toEqual({
      messages: [{ role: 'user', content: question }],
    })
    expect(screen.getAllByText(sentence)).toHaveLength(2)
    const citation = screen.getByRole('list', { name: 'Citations' })
    expect(citation).toHaveTextContent('example.pdf')
    expect(citation).toHaveTextContent('page 1')
    expect(citation).toHaveTextContent(sentence)
    expect(screen.queryByText('No messages yet.')).not.toBeInTheDocument()
  })

  it('the page should show the fixed sentence', async () => {
    // Given
    const user = userEvent.setup()
    server.use(
      http.post('/chat', () =>
        HttpResponse.json({
          outputText: 'No stored document answers that.',
          citations: [],
        }),
      ),
    )
    renderWithProviders(<ChatPage />)

    // When
    await user.type(
      screen.getByRole('textbox', { name: 'Message' }),
      'Where was the zebra?',
    )
    await user.click(screen.getByRole('button', { name: 'Send' }))

    // Then
    expect(
      await screen.findByText('No stored document answers that.'),
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('list', { name: 'Citations' }),
    ).not.toBeInTheDocument()
  })
})
