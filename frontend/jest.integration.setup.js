// Jest setup for integration tests
import { beforeAll, afterAll, afterEach } from '@jest/globals'

// Extended timeout for integration tests
jest.setTimeout(30000)

// Mock console.warn for cleaner test output
const originalWarn = console.warn
beforeAll(() => {
  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return
    }
    originalWarn.call(console, ...args)
  }
})

afterAll(() => {
  console.warn = originalWarn
})

// Clean up after each test
afterEach(() => {
  // Clear all timers
  jest.clearAllTimers()
  // Clear all mocks
  jest.clearAllMocks()
})

// Mock window location
delete window.location
window.location = {
  href: 'http://localhost:3000',
  origin: 'http://localhost:3000',
  protocol: 'http:',
  host: 'localhost:3000',
  hostname: 'localhost',
  port: '3000',
  pathname: '/',
  search: '',
  hash: '',
  assign: jest.fn(),
  replace: jest.fn(),
  reload: jest.fn(),
}

// Mock fetch for integration tests
global.fetch = jest.fn()

// Setup DOM environment
beforeAll(() => {
  // Add viewport meta tag
  const meta = document.createElement('meta')
  meta.name = 'viewport'
  meta.content = 'width=device-width, initial-scale=1'
  document.head.appendChild(meta)
})

// Integration test specific mocks
jest.mock('../src/config/env', () => ({
  env: {
    NODE_ENV: 'test',
    NEXT_PUBLIC_API_URL: 'http://localhost:8000',
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: 'pk_test_mock',
  },
}))

// Mock API client for integration tests
jest.mock('../src/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    patch: jest.fn(),
  },
}))