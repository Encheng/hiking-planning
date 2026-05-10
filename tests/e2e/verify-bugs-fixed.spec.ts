import { test, expect } from '@playwright/test';

const SS = '/tmp/p25-bugs';

test('Bug 2: DAY toggle works for all days', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const presetBtn = page.locator('a, button').filter({ hasText: '玉山' }).first();
  await presetBtn.click();
  await page.waitForURL('**/map**', { timeout: 10000 });
  await page.waitForSelector('.leaflet-container', { timeout: 15000 });
  await page.waitForFunction(() =>
    [...document.querySelectorAll('button')].some(b => b.textContent?.includes('DAY')),
    { timeout: 15000 },
  );

  const dayBtns = page.locator('button').filter({ hasText: 'DAY' });
  const dayCount = await dayBtns.count();
  expect(dayCount).toBeGreaterThanOrEqual(2);

  // Click DAY 1 → should expand
  await dayBtns.nth(0).click();
  await page.waitForTimeout(300);
  const editors1 = await page.locator('[data-day-editor]').count();
  const day1Text1 = await dayBtns.nth(0).textContent();
  expect(editors1).toBe(1);
  expect(day1Text1).toContain('▾');

  // Click DAY 2 → should expand DAY 2, collapse DAY 1
  await dayBtns.nth(1).click();
  await page.waitForTimeout(300);
  await page.screenshot({ path: `${SS}/verify-day2-expanded.png` });
  const editors2 = await page.locator('[data-day-editor]').count();
  const day1Text2 = await dayBtns.nth(0).textContent();
  const day2Text2 = await dayBtns.nth(1).textContent();
  expect(editors2).toBe(1); // exactly one expanded
  expect(day1Text2).toContain('▸'); // DAY 1 collapsed
  expect(day2Text2).toContain('▾'); // DAY 2 expanded

  // Click DAY 1 again → should expand DAY 1
  await dayBtns.nth(0).click();
  await page.waitForTimeout(300);
  const editors3 = await page.locator('[data-day-editor]').count();
  const day1Text3 = await dayBtns.nth(0).textContent();
  expect(editors3).toBe(1);
  expect(day1Text3).toContain('▾');
});

test('Bug 1: Map popup shows action buttons when a day is expanded', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const presetBtn = page.locator('a, button').filter({ hasText: '玉山' }).first();
  await presetBtn.click();
  await page.waitForURL('**/map**', { timeout: 10000 });
  await page.waitForSelector('.leaflet-container', { timeout: 15000 });
  await page.waitForFunction(() =>
    [...document.querySelectorAll('button')].some(b => b.textContent?.includes('DAY')),
    { timeout: 15000 },
  );

  // Expand DAY 2
  const dayBtns = page.locator('button').filter({ hasText: 'DAY' });
  const dayCount = await dayBtns.count();
  await dayBtns.nth(dayCount >= 2 ? 1 : 0).click();
  await page.waitForTimeout(300);

  // Click marker
  const markers = page.locator('.leaflet-marker-icon');
  const markerCount = await markers.count();
  expect(markerCount).toBeGreaterThan(0);
  const mIdx = Math.min(5, markerCount - 1);
  await markers.nth(mIdx).click({ force: true });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SS}/verify-popup-with-buttons.png` });

  // Popup should be visible
  await expect(page.locator('.leaflet-popup')).toBeVisible();

  // Mount div should have content (ID is now dynamic: map-node-popup-mount-N)
  const mountContent = await page.locator('[id^="map-node-popup-mount-"]').innerHTML();
  expect(mountContent.length).toBeGreaterThan(10);

  // Both action buttons should be visible
  const setTargetBtn = page.locator('.leaflet-popup button').filter({ hasText: '當作' });
  const addViaBtn = page.locator('.leaflet-popup button').filter({ hasText: '加為' });
  await expect(setTargetBtn).toBeVisible();
  await expect(addViaBtn).toBeVisible();

  // Clicking "當作目標" should close the popup
  await setTargetBtn.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${SS}/verify-after-set-target.png` });
  const popupGone = await page.locator('.leaflet-popup').count();
  expect(popupGone).toBe(0);
});

test('Bug 1b: Popup shows hint when no day is expanded', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  const presetBtn = page.locator('a, button').filter({ hasText: '玉山' }).first();
  await presetBtn.click();
  await page.waitForURL('**/map**', { timeout: 10000 });
  await page.waitForSelector('.leaflet-container', { timeout: 15000 });
  await page.waitForFunction(() =>
    [...document.querySelectorAll('button')].some(b => b.textContent?.includes('DAY')),
    { timeout: 15000 },
  );

  // Do NOT expand any day — click a marker directly
  const markers = page.locator('.leaflet-marker-icon');
  const markerCount = await markers.count();
  expect(markerCount).toBeGreaterThan(0);
  await markers.nth(3).click({ force: true });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SS}/verify-popup-hint.png` });

  // Should show hint text instead of buttons
  const hintText = page.locator('.leaflet-popup').filter({ hasText: '請先在右側' });
  await expect(hintText).toBeVisible();
});
