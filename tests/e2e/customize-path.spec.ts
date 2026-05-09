import { test, expect } from '@playwright/test';

test.describe('Customize daily plan', () => {
  test('preset → 2 day cards visible', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /玉山主峰單攻/ }).click();
    await expect(page).toHaveURL(/\/map/);
    await page.waitForSelector('.leaflet-container', { timeout: 15000 });
    await page.waitForTimeout(2000);

    const dayCards = page.locator('button:has-text("DAY")');
    await expect(dayCards).toHaveCount(2);
    await expect(dayCards.nth(0)).toContainText('DAY 1');
    await expect(dayCards.nth(1)).toContainText('DAY 2');
  });

  test('add a day → 3 day cards', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /玉山主峰單攻/ }).click();
    await page.waitForSelector('.leaflet-container', { timeout: 15000 });
    await page.waitForTimeout(2000);

    await page.getByRole('button', { name: /加一天/ }).click();
    const dayCards = page.locator('button:has-text("DAY")');
    await expect(dayCards).toHaveCount(3);
  });

  test('toggle returnToStart off', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /玉山主峰單攻/ }).click();
    await page.waitForSelector('.leaflet-container', { timeout: 15000 });
    await page.waitForTimeout(2000);

    // Naive UI NCheckbox renders as role="checkbox" with aria-checked, not a native <input>
    const checkbox = page.getByRole('checkbox', { name: '回到起點' }).first();
    await expect(checkbox).toHaveAttribute('aria-checked', 'true');
    await checkbox.click();
    await expect(checkbox).toHaveAttribute('aria-checked', 'false');
  });

  test('remove a day with confirmation', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /玉山主峰單攻/ }).click();
    await page.waitForSelector('.leaflet-container', { timeout: 15000 });
    await page.waitForTimeout(2000);

    // Expand Day 2 by clicking its summary button
    const day2Btn = page.locator('button:has-text("DAY 2")').first();
    await day2Btn.click();
    await page.waitForTimeout(500);

    // Click remove button (NPopconfirm trigger)
    const removeBtn = page.locator('button:has-text("移除這天")').first();
    await removeBtn.click();
    await page.waitForTimeout(500);

    // Confirm in popconfirm dialog
    const confirmBtn = page.getByRole('button', { name: '確定' }).last();
    await confirmBtn.click();

    const dayCards = page.locator('button:has-text("DAY")');
    await expect(dayCards).toHaveCount(1);
  });
});
