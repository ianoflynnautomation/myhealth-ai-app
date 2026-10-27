import { screen } from '@testing-library/react'
import { renderWithProviders } from '@/test/render'
import { App } from '../App'

describe('App', () => {
  it('renders the chat page at /', () => {
    renderWithProviders(<App />)

    expect(
      screen.getByRole('heading', { name: 'MyHealth AI' }),
    ).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'Message' })).toBeInTheDocument()
  })
})
