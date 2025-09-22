// Global teardown for Playwright E2E tests
import { FullConfig } from '@playwright/test'

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown for E2E tests...')

  // Clean up test data
  await cleanupTestData()

  // Reset database to clean state
  await resetTestDatabase()

  // Clean up temporary files
  await cleanupTempFiles()

  console.log('✅ Global teardown completed')
}

async function cleanupTestData() {
  console.log('🗑️ Cleaning up test data...')

  try {
    // Remove test prompts
    await fetch('http://localhost:8000/api/test/prompts', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    })

    // Remove test users
    await fetch('http://localhost:8000/api/test/users', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    })

    console.log('✅ Test data cleaned up')
  } catch (error) {
    console.warn('⚠️ Could not clean up test data:', error)
  }
}

async function resetTestDatabase() {
  console.log('🔄 Resetting test database...')

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

async function cleanupTempFiles() {
  console.log('🧹 Cleaning up temporary files...')

  try {
    const fs = await import('fs/promises')
    const path = await import('path')

    // Clean up test screenshots
    const screenshotsDir = path.join(process.cwd(), 'test-results')
    try {
      await fs.rmdir(screenshotsDir, { recursive: true })
    } catch (error) {
      // Directory might not exist, which is fine
    }

    // Clean up any other temporary test files
    const tempFiles = [
      'playwright-report',
      'test-results.json',
      'coverage/tmp',
    ]

    for (const file of tempFiles) {
      try {
        await fs.rmdir(path.join(process.cwd(), file), { recursive: true })
      } catch (error) {
        // File might not exist, which is fine
      }
    }

    console.log('✅ Temporary files cleaned up')
  } catch (error) {
    console.warn('⚠️ Could not clean up temporary files:', error)
  }
}

export default globalTeardown