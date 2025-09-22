// MSW server setup for testing
import { setupServer } from 'msw/node'
import { rest } from 'msw'

// Mock API responses
const handlers = [
  // Auth endpoints
  rest.get('/api/auth/user', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 'user_123',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
      })
    )
  }),

  // Prompts API
  rest.get('/api/prompts', (req, res, ctx) => {
    const page = req.url.searchParams.get('page') || '1'
    const limit = req.url.searchParams.get('limit') || '10'

    return res(
      ctx.status(200),
      ctx.json({
        data: [
          {
            id: '1',
            title: 'Test Prompt 1',
            content: 'This is a test prompt',
            tags: ['test', 'example'],
            createdAt: '2024-01-01T00:00:00Z',
            updatedAt: '2024-01-01T00:00:00Z',
            userId: 'user_123',
          },
          {
            id: '2',
            title: 'Test Prompt 2',
            content: 'Another test prompt',
            tags: ['test'],
            createdAt: '2024-01-02T00:00:00Z',
            updatedAt: '2024-01-02T00:00:00Z',
            userId: 'user_123',
          },
        ],
        meta: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: 2,
          totalPages: 1,
        },
      })
    )
  }),

  rest.get('/api/prompts/:id', (req, res, ctx) => {
    const { id } = req.params

    return res(
      ctx.status(200),
      ctx.json({
        id,
        title: `Test Prompt ${id}`,
        content: 'This is a test prompt content',
        tags: ['test'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
        userId: 'user_123',
        versions: [
          {
            id: '1',
            content: 'Version 1 content',
            createdAt: '2024-01-01T00:00:00Z',
          },
        ],
      })
    )
  }),

  rest.post('/api/prompts', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 'new_prompt_id',
        title: 'New Prompt',
        content: 'New prompt content',
        tags: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        userId: 'user_123',
      })
    )
  }),

  rest.put('/api/prompts/:id', (req, res, ctx) => {
    const { id } = req.params

    return res(
      ctx.status(200),
      ctx.json({
        id,
        title: 'Updated Prompt',
        content: 'Updated content',
        tags: ['updated'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: new Date().toISOString(),
        userId: 'user_123',
      })
    )
  }),

  rest.delete('/api/prompts/:id', (req, res, ctx) => {
    return res(ctx.status(204))
  }),

  // LLM Provider endpoints
  rest.get('/api/llm/providers', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        providers: [
          {
            id: 'openai',
            name: 'OpenAI',
            models: ['gpt-4', 'gpt-3.5-turbo'],
            enabled: true,
          },
          {
            id: 'anthropic',
            name: 'Anthropic',
            models: ['claude-3-opus', 'claude-3-sonnet'],
            enabled: true,
          },
        ],
      })
    )
  }),

  rest.post('/api/llm/generate', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        response: 'This is a mock LLM response',
        metadata: {
          model: 'gpt-4',
          tokens: 150,
          cost: 0.002,
        },
      })
    )
  }),

  // Analytics endpoints
  rest.get('/api/analytics/prompts', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        totalPrompts: 100,
        totalQueries: 1500,
        avgResponseTime: 2.5,
        costThisMonth: 45.67,
        topModels: [
          { name: 'gpt-4', usage: 60 },
          { name: 'claude-3-opus', usage: 40 },
        ],
      })
    )
  }),

  // Health check
  rest.get('/api/health', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        services: {
          database: 'ok',
          redis: 'ok',
          llm_providers: 'ok',
        },
      })
    )
  }),

  // Error scenarios for testing
  rest.get('/api/error/500', (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ error: 'Internal Server Error' }))
  }),

  rest.get('/api/error/404', (req, res, ctx) => {
    return res(ctx.status(404), ctx.json({ error: 'Not Found' }))
  }),

  rest.get('/api/error/timeout', (req, res, ctx) => {
    return res(ctx.delay(30000), ctx.status(408))
  }),
]

// Create and export the server
export const server = setupServer(...handlers)

// Export handlers for reuse in tests
export { handlers }

// Helper functions for dynamic mocking
export const mockPromptResponse = (prompt: any) => {
  server.use(
    rest.get(`/api/prompts/${prompt.id}`, (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(prompt))
    })
  )
}

export const mockError = (endpoint: string, status: number, message: string) => {
  server.use(
    rest.get(endpoint, (req, res, ctx) => {
      return res(ctx.status(status), ctx.json({ error: message }))
    })
  )
}

export const mockLoadingDelay = (endpoint: string, delay: number) => {
  server.use(
    rest.get(endpoint, (req, res, ctx) => {
      return res(ctx.delay(delay), ctx.status(200), ctx.json({}))
    })
  )
}

// Reset all request handlers
export const resetMocks = () => {
  server.resetHandlers(...handlers)
}