// Example E2E test for prompt management
import { test, expect } from '@playwright/test'

test.describe('Prompt Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to prompts page
    await page.goto('/prompts')

    // Wait for the page to load
    await page.waitForSelector('[data-testid="prompts-page"]')
  })

  test.describe('Prompt List', () => {
    test('should display list of prompts', async ({ page }) => {
      // Check if prompts are displayed
      await expect(page.locator('[data-testid="prompt-card"]')).toHaveCount(2)

      // Check specific prompt content
      await expect(page.locator('text=E2E Test Prompt')).toBeVisible()
      await expect(page.locator('text=Private Test Prompt')).toBeVisible()
    })

    test('should filter prompts by tags', async ({ page }) => {
      // Click on tag filter
      await page.click('[data-testid="tag-filter-test"]')

      // Check that only prompts with "test" tag are shown
      const visiblePrompts = page.locator('[data-testid="prompt-card"]:visible')
      await expect(visiblePrompts).toHaveCount(2)

      // Check that all visible prompts have the "test" tag
      const tagElements = page.locator('[data-testid="prompt-tag"]:has-text("test")')
      await expect(tagElements).toHaveCountGreaterThan(0)
    })

    test('should search prompts by title', async ({ page }) => {
      // Type in search box
      await page.fill('[data-testid="search-input"]', 'E2E Test')

      // Wait for search results
      await page.waitForTimeout(500)

      // Check that only matching prompts are shown
      await expect(page.locator('[data-testid="prompt-card"]')).toHaveCount(1)
      await expect(page.locator('text=E2E Test Prompt')).toBeVisible()
    })

    test('should sort prompts by creation date', async ({ page }) => {
      // Click sort dropdown
      await page.click('[data-testid="sort-dropdown"]')

      // Select sort by date
      await page.click('[data-testid="sort-created-desc"]')

      // Check that prompts are sorted correctly
      const promptTitles = await page.locator('[data-testid="prompt-title"]').allTextContents()
      expect(promptTitles[0]).toBe('Private Test Prompt') // Assuming it's newer
    })
  })

  test.describe('Prompt Creation', () => {
    test('should create a new prompt', async ({ page }) => {
      // Click create button
      await page.click('[data-testid="create-prompt-button"]')

      // Fill form
      await page.fill('[data-testid="prompt-title-input"]', 'New E2E Prompt')
      await page.fill('[data-testid="prompt-content-textarea"]', 'This is a new prompt created via E2E test')
      await page.fill('[data-testid="prompt-tags-input"]', 'new, e2e, automated')

      // Select category
      await page.selectOption('[data-testid="prompt-category-select"]', 'Technical')

      // Save prompt
      await page.click('[data-testid="save-prompt-button"]')

      // Check success message
      await expect(page.locator('[data-testid="success-toast"]')).toBeVisible()
      await expect(page.locator('text=Prompt created successfully')).toBeVisible()

      // Check that we're redirected to the new prompt's page
      await expect(page).toHaveURL(/\/prompts\/[a-zA-Z0-9]+/)

      // Verify prompt content
      await expect(page.locator('[data-testid="prompt-title"]')).toHaveText('New E2E Prompt')
      await expect(page.locator('[data-testid="prompt-content"]')).toContainText('This is a new prompt created via E2E test')
    })

    test('should validate required fields', async ({ page }) => {
      // Click create button
      await page.click('[data-testid="create-prompt-button"]')

      // Try to save without filling required fields
      await page.click('[data-testid="save-prompt-button"]')

      // Check validation errors
      await expect(page.locator('[data-testid="title-error"]')).toHaveText('Title is required')
      await expect(page.locator('[data-testid="content-error"]')).toHaveText('Content is required')
    })

    test('should save as draft', async ({ page }) => {
      // Click create button
      await page.click('[data-testid="create-prompt-button"]')

      // Fill minimal data
      await page.fill('[data-testid="prompt-title-input"]', 'Draft Prompt')

      // Save as draft
      await page.click('[data-testid="save-draft-button"]')

      // Check success message
      await expect(page.locator('text=Draft saved successfully')).toBeVisible()

      // Navigate to drafts
      await page.click('[data-testid="drafts-tab"]')

      // Check that draft is listed
      await expect(page.locator('text=Draft Prompt')).toBeVisible()
      await expect(page.locator('[data-testid="draft-badge"]')).toBeVisible()
    })
  })

  test.describe('Prompt Editing', () => {
    test('should edit an existing prompt', async ({ page }) => {
      // Click on a prompt to view it
      await page.click('[data-testid="prompt-card"]:first-child')

      // Click edit button
      await page.click('[data-testid="edit-prompt-button"]')

      // Modify content
      await page.fill('[data-testid="prompt-title-input"]', 'Updated E2E Test Prompt')
      await page.fill('[data-testid="prompt-content-textarea"]', 'Updated content for E2E testing')

      // Save changes
      await page.click('[data-testid="save-prompt-button"]')

      // Check success message
      await expect(page.locator('text=Prompt updated successfully')).toBeVisible()

      // Verify changes
      await expect(page.locator('[data-testid="prompt-title"]')).toHaveText('Updated E2E Test Prompt')
      await expect(page.locator('[data-testid="prompt-content"]')).toContainText('Updated content for E2E testing')
    })

    test('should create a new version when editing', async ({ page }) => {
      // Click on a prompt to view it
      await page.click('[data-testid="prompt-card"]:first-child')

      // Check current version count
      const initialVersions = await page.locator('[data-testid="version-item"]').count()

      // Click edit button
      await page.click('[data-testid="edit-prompt-button"]')

      // Modify content significantly
      await page.fill('[data-testid="prompt-content-textarea"]', 'Completely new content that should create a new version')

      // Save changes
      await page.click('[data-testid="save-prompt-button"]')

      // Check that a new version was created
      await expect(page.locator('[data-testid="version-item"]')).toHaveCount(initialVersions + 1)

      // Check that the latest version is active
      await expect(page.locator('[data-testid="active-version"]')).toContainText('Completely new content')
    })
  })

  test.describe('Prompt Testing', () => {
    test('should test prompt with LLM provider', async ({ page }) => {
      // Click on a prompt to view it
      await page.click('[data-testid="prompt-card"]:first-child')

      // Click test button
      await page.click('[data-testid="test-prompt-button"]')

      // Select LLM provider
      await page.selectOption('[data-testid="provider-select"]', 'openai')
      await page.selectOption('[data-testid="model-select"]', 'gpt-4')

      // Add test input if required
      await page.fill('[data-testid="test-input"]', 'Test input for the prompt')

      // Run test
      await page.click('[data-testid="run-test-button"]')

      // Wait for results
      await expect(page.locator('[data-testid="test-results"]')).toBeVisible({ timeout: 30000 })

      // Check that response is displayed
      await expect(page.locator('[data-testid="llm-response"]')).not.toBeEmpty()

      // Check metadata
      await expect(page.locator('[data-testid="response-metadata"]')).toBeVisible()
      await expect(page.locator('[data-testid="token-count"]')).not.toBeEmpty()
      await expect(page.locator('[data-testid="cost-estimate"]')).not.toBeEmpty()
    })

    test('should compare multiple provider responses', async ({ page }) => {
      // Click on a prompt to view it
      await page.click('[data-testid="prompt-card"]:first-child')

      // Click compare button
      await page.click('[data-testid="compare-providers-button"]')

      // Select multiple providers
      await page.check('[data-testid="provider-openai"]')
      await page.check('[data-testid="provider-anthropic"]')

      // Run comparison
      await page.click('[data-testid="run-comparison-button"]')

      // Wait for results
      await expect(page.locator('[data-testid="comparison-results"]')).toBeVisible({ timeout: 60000 })

      // Check that both responses are displayed
      await expect(page.locator('[data-testid="openai-response"]')).toBeVisible()
      await expect(page.locator('[data-testid="anthropic-response"]')).toBeVisible()

      // Check comparison metrics
      await expect(page.locator('[data-testid="comparison-metrics"]')).toBeVisible()
    })
  })

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 })

      // Check that mobile navigation works
      await page.click('[data-testid="mobile-menu-button"]')
      await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible()

      // Check that prompts are displayed properly
      await expect(page.locator('[data-testid="prompt-card"]')).toBeVisible()

      // Check that actions are accessible
      await page.click('[data-testid="prompt-card"]:first-child')
      await expect(page.locator('[data-testid="mobile-actions"]')).toBeVisible()
    })

    test('should work on tablet devices', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 })

      // Check layout adaptation
      const promptGrid = page.locator('[data-testid="prompts-grid"]')
      await expect(promptGrid).toHaveCSS('grid-template-columns', /repeat\(2/)
    })
  })

  test.describe('Performance', () => {
    test('should load prompts quickly', async ({ page }) => {
      const startTime = Date.now()

      // Navigate to prompts page
      await page.goto('/prompts')

      // Wait for content to load
      await page.waitForSelector('[data-testid="prompt-card"]')

      const loadTime = Date.now() - startTime

      // Check that page loads within 3 seconds
      expect(loadTime).toBeLessThan(3000)
    })

    test('should handle large number of prompts', async ({ page }) => {
      // Navigate to prompts page with pagination
      await page.goto('/prompts?limit=100')

      // Check that pagination works
      await expect(page.locator('[data-testid="pagination"]')).toBeVisible()

      // Check that performance is acceptable
      const navigation = await page.evaluate(() => performance.getEntriesByType('navigation')[0])
      expect(navigation.loadEventEnd - navigation.fetchStart).toBeLessThan(5000)
    })
  })
})