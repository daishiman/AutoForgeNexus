// Test data factory for prompts
import { faker } from '@faker-js/faker'

export interface MockPrompt {
  id: string
  title: string
  content: string
  tags: string[]
  createdAt: string
  updatedAt: string
  userId: string
  description?: string
  category?: string
  isPublic?: boolean
  versions?: MockPromptVersion[]
  analytics?: MockPromptAnalytics
}

export interface MockPromptVersion {
  id: string
  content: string
  createdAt: string
  metrics?: {
    accuracy?: number
    relevance?: number
    coherence?: number
  }
}

export interface MockPromptAnalytics {
  totalUsage: number
  successRate: number
  avgResponseTime: number
  cost: number
  lastUsed: string
}

// Factory functions
export const createMockPrompt = (overrides: Partial<MockPrompt> = {}): MockPrompt => {
  const basePrompt: MockPrompt = {
    id: faker.string.uuid(),
    title: faker.lorem.words(3),
    content: faker.lorem.paragraphs(2),
    tags: faker.helpers.arrayElements(
      ['AI', 'ML', 'NLP', 'Creative', 'Technical', 'Business', 'Personal'],
      { min: 1, max: 3 }
    ),
    createdAt: faker.date.recent().toISOString(),
    updatedAt: faker.date.recent().toISOString(),
    userId: faker.string.uuid(),
    description: faker.lorem.sentence(),
    category: faker.helpers.arrayElement(['Productivity', 'Creative', 'Technical', 'Research']),
    isPublic: faker.datatype.boolean(),
  }

  return { ...basePrompt, ...overrides }
}

export const createMockPromptVersion = (
  overrides: Partial<MockPromptVersion> = {}
): MockPromptVersion => {
  const baseVersion: MockPromptVersion = {
    id: faker.string.uuid(),
    content: faker.lorem.paragraphs(2),
    createdAt: faker.date.recent().toISOString(),
    metrics: {
      accuracy: faker.number.float({ min: 0.7, max: 1.0, fractionDigits: 2 }),
      relevance: faker.number.float({ min: 0.7, max: 1.0, fractionDigits: 2 }),
      coherence: faker.number.float({ min: 0.7, max: 1.0, fractionDigits: 2 }),
    },
  }

  return { ...baseVersion, ...overrides }
}

export const createMockPromptAnalytics = (
  overrides: Partial<MockPromptAnalytics> = {}
): MockPromptAnalytics => {
  const baseAnalytics: MockPromptAnalytics = {
    totalUsage: faker.number.int({ min: 0, max: 1000 }),
    successRate: faker.number.float({ min: 0.5, max: 1.0, fractionDigits: 2 }),
    avgResponseTime: faker.number.float({ min: 0.5, max: 10.0, fractionDigits: 2 }),
    cost: faker.number.float({ min: 0.01, max: 50.0, fractionDigits: 2 }),
    lastUsed: faker.date.recent().toISOString(),
  }

  return { ...baseAnalytics, ...overrides }
}

// Collection factories
export const createMockPromptList = (count: number = 10): MockPrompt[] => {
  return Array.from({ length: count }, () => createMockPrompt())
}

export const createMockPromptWithVersions = (versionCount: number = 3): MockPrompt => {
  const prompt = createMockPrompt()
  prompt.versions = Array.from({ length: versionCount }, () => createMockPromptVersion())
  prompt.analytics = createMockPromptAnalytics()
  return prompt
}

// Scenario-specific factories
export const createRecentPrompt = (): MockPrompt => {
  return createMockPrompt({
    createdAt: faker.date.recent({ days: 1 }).toISOString(),
    updatedAt: faker.date.recent({ days: 1 }).toISOString(),
  })
}

export const createPopularPrompt = (): MockPrompt => {
  return createMockPrompt({
    analytics: createMockPromptAnalytics({
      totalUsage: faker.number.int({ min: 100, max: 1000 }),
      successRate: faker.number.float({ min: 0.8, max: 1.0, fractionDigits: 2 }),
    }),
    isPublic: true,
  })
}

export const createLongPrompt = (): MockPrompt => {
  return createMockPrompt({
    content: faker.lorem.paragraphs(10),
    title: faker.lorem.words(8),
  })
}

export const createEmptyPrompt = (): MockPrompt => {
  return createMockPrompt({
    content: '',
    tags: [],
    description: '',
  })
}

// Test scenarios
export const createPromptTestScenarios = () => {
  return {
    basic: createMockPrompt(),
    recent: createRecentPrompt(),
    popular: createPopularPrompt(),
    long: createLongPrompt(),
    empty: createEmptyPrompt(),
    withVersions: createMockPromptWithVersions(),
    list: createMockPromptList(5),
  }
}

// Mock API response factories
export const createMockPromptResponse = (prompt: MockPrompt) => {
  return {
    data: prompt,
    success: true,
    message: 'Prompt retrieved successfully',
  }
}

export const createMockPromptListResponse = (prompts: MockPrompt[], page = 1, limit = 10) => {
  return {
    data: prompts,
    meta: {
      page,
      limit,
      total: prompts.length,
      totalPages: Math.ceil(prompts.length / limit),
    },
    success: true,
    message: 'Prompts retrieved successfully',
  }
}

export const createMockErrorResponse = (message: string, code: number = 400) => {
  return {
    error: {
      message,
      code,
      timestamp: new Date().toISOString(),
    },
    success: false,
  }
}