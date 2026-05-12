import { test, expect } from '@playwright/test';

test('popup shows buttons on repeated node clicks', async ({ page }) => {
  // 1. Open the planner
  await page.goto('http://localhost:5175/');

  // 2. Click 玉山主峰單攻 preset
  await page.getByText('玉山主峰單攻').click();
  await page.waitForSelector('.leaflet-container', { timeout: 10000 });

  // 3. Expand DAY 2 (click DAY 2 header)
  await page.getByText('DAY 2').click();
  await page.waitForTimeout(300);

  // Get node markers (specifically node-marker class, not gpx markers)
  const markers = page.locator('.leaflet-marker-icon.node-marker');
  const count = await markers.count();
  console.log(`Found ${count} node markers`);

  // --- Popup 1: Click first node marker ---
  await markers.nth(0).click();
  await page.waitForTimeout(600);

  const popup1 = page.locator('.leaflet-popup-content');
  await expect(popup1).toBeVisible({ timeout: 5000 });
  const btn1Text = await popup1.textContent();
  console.log('Popup 1 text:', btn1Text);
  expect(btn1Text).toContain('▶');
  await page.screenshot({ path: '/tmp/p25-bug3rd/popup1-first-click.png' });

  // Close popup via the close button
  const closeBtn1 = page.locator('.leaflet-popup-close-button');
  await closeBtn1.click();
  await page.waitForTimeout(300);

  // --- Popup 2: Click second node marker ---
  await markers.nth(1).click();
  await page.waitForTimeout(600);

  const popup2 = page.locator('.leaflet-popup-content');
  await expect(popup2).toBeVisible({ timeout: 5000 });
  const btn2Text = await popup2.textContent();
  console.log('Popup 2 text:', btn2Text);
  expect(btn2Text).toContain('▶');
  await page.screenshot({ path: '/tmp/p25-bug3rd/popup2-second-marker.png' });

  // Close popup
  const closeBtn2 = page.locator('.leaflet-popup-close-button');
  await closeBtn2.click();
  await page.waitForTimeout(300);

  // --- Popup 3: Click third node marker ---
  await markers.nth(2).click();
  await page.waitForTimeout(600);

  const popup3 = page.locator('.leaflet-popup-content');
  await expect(popup3).toBeVisible({ timeout: 5000 });
  const btn3Text = await popup3.textContent();
  console.log('Popup 3 text:', btn3Text);
  expect(btn3Text).toContain('▶');
  await page.screenshot({ path: '/tmp/p25-bug3rd/popup3-third-marker.png' });

  // Close popup
  const closeBtn3 = page.locator('.leaflet-popup-close-button');
  await closeBtn3.click();
  await page.waitForTimeout(300);

  // --- Popup 4: Click the FIRST marker AGAIN (bug scenario: same node second click) ---
  await markers.nth(0).click();
  await page.waitForTimeout(600);

  const popup4 = page.locator('.leaflet-popup-content');
  await expect(popup4).toBeVisible({ timeout: 5000 });
  const btn4Text = await popup4.textContent();
  console.log('Popup 4 text (same node, second click):', btn4Text);
  expect(btn4Text).toContain('▶');
  await page.screenshot({ path: '/tmp/p25-bug3rd/popup4-same-node-again.png' });

  console.log('All 4 popups verified successfully!');
});
