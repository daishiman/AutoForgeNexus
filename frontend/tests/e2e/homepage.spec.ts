import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('has title', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/AutoForge Nexus/);
  });

  test('displays main heading', async ({ page }) => {
    await page.goto('/');

    const heading = page.getByRole('heading', { name: 'AutoForge Nexus' });
    await expect(heading).toBeVisible();
  });

  test('has Get Started button', async ({ page }) => {
    await page.goto('/');

    const getStartedButton = page.getByRole('button', { name: 'Get Started' });
    await expect(getStartedButton).toBeVisible();
  });

  test('has Learn More button', async ({ page }) => {
    await page.goto('/');

    const learnMoreButton = page.getByRole('button', { name: 'Learn More' });
    await expect(learnMoreButton).toBeVisible();
  });

  test('displays version information', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('Next.js 15.5.4')).toBeVisible();
    await expect(page.getByText('React 19.0.0')).toBeVisible();
    await expect(page.getByText('TypeScript 5.9.2')).toBeVisible();
  });

  test('responsive layout works', async ({ page }) => {
    // Desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'AutoForge Nexus' })).toBeVisible();

    // Mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.getByRole('heading', { name: 'AutoForge Nexus' })).toBeVisible();
  });
});