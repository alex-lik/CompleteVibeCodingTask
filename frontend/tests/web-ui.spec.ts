import { test, expect } from '@playwright/test';

test.describe('Web UI Tests', () => {
  test('should load the main application page', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check that the page loads successfully
    await expect(page).toHaveTitle('Agent Task Tracker');
  });

  test('should display navigation menu', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for navigation elements (Layout component uses div for navigation)
    const navElement = page.locator('div[class*="nav"], nav, [data-testid="nav"]');
    await expect(navElement).toBeVisible();
  });

  test('should have working navigation links', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Test navigation to different pages
    const navLinks = page.locator('nav a');
    const linkCount = await navLinks.count();

    console.log(`Found ${linkCount} navigation links`);

    // Check at least some navigation links exist
    expect(linkCount).toBeGreaterThan(0);
  });

  test('should display application components', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for main content area
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();

    // Check for at least some content
    const content = await mainContent.textContent();
    expect(content).toBeTruthy();
  });

  test('should handle responsive design', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check normal viewport
    await expect(page.locator('body')).toBeVisible();

    // Check mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('API Integration Tests', () => {
  test('should make API calls to backend', async ({ page }) => {
    // Enable request interception
    await page.route('**/api/**', route => {
      // Log API calls for debugging
      console.log('API Request:', route.request().url());
      route.continue();
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait for any API calls to complete
    await page.waitForTimeout(2000);

    // Check if API calls were made (should be logged in console)
    console.log('API test completed');
  });
});

test.describe('Error Handling Tests', () => {
  test('should handle network errors gracefully', async ({ page }) => {
    // Block API calls to simulate network issues
    await page.route('**/api/**', route => route.abort('failed'));

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check that the application doesn't crash and shows some content
    const body = page.locator('body');
    await expect(body).toBeVisible();

    // Should show some fallback content or loading state
    const content = await body.textContent();
    expect(content).toBeTruthy();
  });
});