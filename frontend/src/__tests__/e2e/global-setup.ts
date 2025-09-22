// Global setup for Playwright E2E tests
import { FullConfig } from '@playwright/test'

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for E2E tests...')

  // Set up test environment variables
  process.env.NODE_ENV = 'test'
  process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = 'pk_test_mock'

  // Wait for services to be ready
  await waitForServices()

  // Set up test database state if needed
  await setupTestDatabase()

  // Create test users and data
  await seedTestData()

  console.log('✅ Global setup completed')
}

async function waitForServices() {
  const services = [
    { name: 'Frontend', url: 'http://localhost:3000/api/health' },
    { name: 'Backend', url: 'http://localhost:8000/health' },
  ]

  for (const service of services) {
    await waitForService(service.name, service.url)
  }
}

async function waitForService(name: string, url: string, maxRetries = 30) {
  console.log(`⏳ Waiting for ${name} to be ready...`)

  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url)
      if (response.ok) {
        console.log(`✅ ${name} is ready`)
        return
      }
    } catch (error) {
      // Service not ready yet
    }

    await new Promise(resolve => setTimeout(resolve, 2000))
  }

  throw new Error(`❌ ${name} failed to start within timeout`)
}

async function setupTestDatabase() {
  console.log('🗄️ Setting up test database...')

  // Reset database to clean state
  try {
    await fetch('http://localhost:8000/api/test/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    console.log('✅ Test database reset')
  } catch (error) {
    console.warn('⚠️ Could not reset test database:', error)
  }
}

async function seedTestData() {
  console.log('🌱 Seeding test data...')

  // Create test users
  const testUsers = [
    {
      id: 'test_user_1',
      email: 'test1@example.com',
      firstName: 'Test',
      lastName: 'User',
    },
    {
      id: 'test_user_2',
      email: 'test2@example.com',
      firstName: 'Demo',
      lastName: 'Account',
    },
  ]

  // Create test prompts
  const testPrompts = [
    {
      id: 'test_prompt_1',
      title: 'E2E Test Prompt',
      content: 'This is a test prompt for E2E testing',
      tags: ['test', 'e2e'],
      userId: 'test_user_1',
      isPublic: true,
    },
    {
      id: 'test_prompt_2',
      title: 'Private Test Prompt',
      content: 'This is a private test prompt',
      tags: ['test', 'private'],
      userId: 'test_user_1',
      isPublic: false,
    },
  ]

  try {
    // Seed users
    for (const user of testUsers) {
      await fetch('http://localhost:8000/api/test/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user),
      })
    }

    // Seed prompts
    for (const prompt of testPrompts) {
      await fetch('http://localhost:8000/api/test/prompts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(prompt),
      })
    }

    console.log('✅ Test data seeded successfully')
  } catch (error) {
    console.warn('⚠️ Could not seed test data:', error)
  }
}

export default globalSetup