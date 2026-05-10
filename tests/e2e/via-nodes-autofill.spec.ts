import { test, expect } from '@playwright/test';

test.describe('BFS via-nodes auto-fill', () => {
  test('玉山主峰單攻 preset: DAY 1 has 5 intermediate chips, DAY 2 has none', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /玉山主峰單攻/ }).click();
    await expect(page).toHaveURL(/\/map/);
    await page.waitForSelector('.leaflet-container', { timeout: 15000 });
    await page.waitForTimeout(2000);

    // Expand DAY 1
    const day1Btn = page.locator('button:has-text("DAY 1")').first();
    await day1Btn.click();
    await page.waitForTimeout(500);

    // Verify the 5 intermediate via-node chips are visible
    const expectedDay1Chips = [
      '上東埔停車場',
      '鹿林山莊',
      '排雲管理站',
      '大鐵杉',
      '白木林',
    ];
    for (const name of expectedDay1Chips) {
      await expect(page.getByText(name).first()).toBeVisible();
    }

    // Take a screenshot with DAY 1 expanded
    await page.screenshot({ path: 'tests/e2e/screenshots/via-nodes-day1.png', fullPage: false });

    // Collapse DAY 1 and expand DAY 2
    await day1Btn.click();
    await page.waitForTimeout(300);
    const day2Btn = page.locator('button:has-text("DAY 2")').first();
    await day2Btn.click();
    await page.waitForTimeout(500);

    // DAY 2 should have no intermediate via chips (paiyun directly connects to yushan_main)
    // Verify none of the DAY 1 via chips are visible (they should be hidden now)
    for (const name of expectedDay1Chips) {
      await expect(page.getByText(name)).toHaveCount(0);
    }

    await page.screenshot({ path: 'tests/e2e/screenshots/via-nodes-day2.png', fullPage: false });
  });
});
