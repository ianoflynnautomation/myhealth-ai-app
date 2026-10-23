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
})
