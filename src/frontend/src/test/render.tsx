import { QueryClient } from '@tanstack/react-query'
import { render, type RenderOptions } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router'
import { Providers } from '@/app/providers'

interface Options extends Omit<RenderOptions, 'wrapper'> {
  route?: string
}

/** Render with app providers, a MemoryRouter and a fresh, non-retrying QueryClient. */
export function renderWithProviders(
  ui: ReactElement,
  { route = '/', ...options }: Options = {},
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(ui, {
    wrapper: ({ children }) => (
      <Providers queryClient={queryClient}>
        <MemoryRouter initialEntries={[route]}>{children}</MemoryRouter>
      </Providers>
    ),
    ...options,
  })
}
