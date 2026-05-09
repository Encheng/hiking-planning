import { test, expect } from '@playwright/test';

test.describe('Create plan happy path', () => {
  test('select preset → save → view schedule (V1/V2/V3) → check gear → print', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('百岳路線')).toBeVisible();

    await page.getByRole('button', { name: /玉山主峰單攻/ }).click();
    await expect(page).toHaveURL(/\/map/);

    await page.waitForSelector('.leaflet-container', { timeout: 15000 });
    await page.waitForTimeout(2000);
    await page.getByRole('button', { name: '儲存行程' }).click();

    await expect(page).toHaveURL(/\/schedule\//);
    await expect(page.getByText(/玉山主峰/).first()).toBeVisible();

    // V2 (default) — table visible
    await expect(page.locator('table').first()).toBeVisible();

    // Switch to V1 Gantt
    await page.locator('.n-tabs-tab:has-text("V1")').click();
    await expect(page.locator('[data-segment-bar]').first()).toBeVisible();

    // Switch to V3 Elevation
    await page.locator('.n-tabs-tab:has-text("V3")').click();
    await expect(page.locator('svg polyline').first()).toBeVisible();

    // Switch back to V2
    await page.locator('.n-tabs-tab:has-text("V2")').click();
    await expect(page.locator('table').first()).toBeVisible();

    // Print: stub window.print, click button, assert called
    await page.evaluate(() => {
      (window as unknown as { __printCalls: number }).__printCalls = 0;
      window.print = () => {
        (window as unknown as { __printCalls: number }).__printCalls += 1;
      };
    });
    // Wait for the print button to be enabled (gear loaded)
    await page.waitForFunction(() => {
      const btn = Array.from(document.querySelectorAll('button')).find((b) => b.textContent?.trim() === '列印');
      return btn !== undefined && !btn.hasAttribute('disabled') && !btn.classList.contains('n-button--disabled');
    }, { timeout: 5000 });
    await page.getByRole('button', { name: '列印' }).click();
    const printCalls = await page.evaluate(() => (window as unknown as { __printCalls: number }).__printCalls);
    expect(printCalls).toBe(1);

    // Continue to gear page
    await page.getByRole('button', { name: '裝備清單' }).click();
    await expect(page).toHaveURL(/\/gear\//);
    await expect(page.getByText('輕裝攻頂', { exact: false }).first()).toBeVisible();

    const firstCheckbox = page.locator('.n-checkbox').first();
    await firstCheckbox.click();
    await expect(firstCheckbox).toHaveClass(/n-checkbox--checked/);

    await page.goto('/plans');
    await expect(page.locator('text=玉山主峰').first()).toBeVisible();
  });
});
