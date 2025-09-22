// Custom render function for testing with providers
import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ClerkProvider } from '@clerk/nextjs'

// Test wrapper with all providers
interface AllTheProvidersProps {
  children: React.ReactNode
}

const AllTheProviders = ({ children }: AllTheProvidersProps) => {
  // Create a new QueryClient for each test to ensure isolation
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return (
    <ClerkProvider publishableKey="pk_test_mock">
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </ClerkProvider>
  )
}

// Custom render function that includes providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Re-export everything from testing-library
export * from '@testing-library/react'

// Override render method
export { customRender as render }

// Additional test utilities
export const renderWithQueryClient = (
  ui: ReactElement,
  queryClient?: QueryClient
) => {
  const client = queryClient || new QueryClient({
    defaultOptions: {
      queries: { retry: false, cacheTime: 0 },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={client}>
      {ui}
    </QueryClientProvider>
  )
}

// Clerk-specific test wrapper
export const renderWithClerk = (
  ui: ReactElement,
  mockUser?: any
) => {
  return render(
    <ClerkProvider publishableKey="pk_test_mock">
      {ui}
    </ClerkProvider>
  )
}

// Test helper for form testing
export const fillForm = async (
  user: any,
  fields: Record<string, string>
) => {
  for (const [name, value] of Object.entries(fields)) {
    const field = document.querySelector(`[name="${name}"]`) as HTMLInputElement
    if (field) {
      await user.clear(field)
      await user.type(field, value)
    }
  }
}

// Wait for async operations
export const waitForLoadingToFinish = () =>
  new Promise((resolve) => setTimeout(resolve, 0))

// Custom matchers
export const toBeInTheDocument = (element: HTMLElement | null) => {
  return element !== null && document.body.contains(element)
}

// Test ID helpers
export const getByTestId = (testId: string) =>
  document.querySelector(`[data-testid="${testId}"]`)

export const getAllByTestId = (testId: string) =>
  document.querySelectorAll(`[data-testid="${testId}"]`)

// Mock data helpers
export const createMockPrompt = (overrides = {}) => ({
  id: '1',
  title: 'Test Prompt',
  content: 'This is a test prompt',
  tags: ['test'],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  userId: 'user_123',
  ...overrides,
})

export const createMockUser = (overrides = {}) => ({
  id: 'user_123',
  emailAddress: 'test@example.com',
  firstName: 'Test',
  lastName: 'User',
  ...overrides,
})

// Performance testing utilities
export const measureRenderTime = (component: ReactElement) => {
  const start = performance.now()
  const result = render(component)
  const end = performance.now()

  return {
    ...result,
    renderTime: end - start,
  }
}

// Accessibility testing helpers
export const checkA11y = async (container: HTMLElement) => {
  const { axe, toHaveNoViolations } = await import('jest-axe')
  expect.extend(toHaveNoViolations)

  const results = await axe(container)
  expect(results).toHaveNoViolations()
}