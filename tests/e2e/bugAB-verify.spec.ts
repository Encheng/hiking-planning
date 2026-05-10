import { test, expect } from '@playwright/test';

const SS = '/tmp/p25-bugAB';

test('desktop layout and popup repeated clicks', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
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

  const markers = page.locator('.leaflet-marker-icon');
  const markerCount = await markers.count();
  expect(markerCount).toBeGreaterThan(0);
  console.log(`Found ${markerCount} node markers`);

  // Helper: click a marker and verify popup has buttons
  async function clickAndVerify(idx: number, label: string) {
    await markers.nth(idx).click({ force: true });
    // Wait for popup to appear with buttons
    await expect(page.locator('.leaflet-popup button').filter({ hasText: '當作' })).toBeVisible({ timeout: 8000 });
    const btns = await page.locator('.leaflet-popup button').filter({ hasText: '當作' }).count();
    console.log(`${label}: buttons = ${btns}`);
    expect(btns).toBeGreaterThan(0);
  }

  // Click first marker
  await clickAndVerify(0, 'Popup 1 (marker 0, 1st click)');
  await page.screenshot({ path: `${SS}/popup-1.png` });

  // Click SAME first marker AGAIN (Bug A: 2nd click same marker)
  await clickAndVerify(0, 'Popup 2 (marker 0, 2nd click - Bug A)');
  await page.screenshot({ path: `${SS}/popup-2.png` });

  // Close with X and click again
  await page.locator('.leaflet-popup-close-button').first().click();
  await page.waitForTimeout(500);
  await clickAndVerify(0, 'Popup 3 (marker 0, after X + reclick)');
  await page.screenshot({ path: `${SS}/popup-3.png` });

  // Click different markers — close previous popup first to avoid overlay interference
  await page.locator('.leaflet-popup-close-button').first().click();
  await page.waitForTimeout(300);
  await clickAndVerify(1, 'Popup 4 (marker 1)');

  await page.locator('.leaflet-popup-close-button').first().click();
  await page.waitForTimeout(300);
  await clickAndVerify(2, 'Popup 5 (marker 2)');
});

test('mobile layout: aside stacks below map, map is tappable', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const presetBtn = page.locator('a, button').filter({ hasText: '玉山' }).first();
  await presetBtn.click();
  await page.waitForURL('**/map**', { timeout: 10000 });
  await page.waitForSelector('.leaflet-container', { timeout: 15000 });
  await page.screenshot({ path: `${SS}/mobile-layout.png` });

  // Check map has positive dimensions
  const mapBox = await page.locator('.leaflet-container').boundingBox();
  console.log(`Map bounding box: ${JSON.stringify(mapBox)}`);
  expect(mapBox).not.toBeNull();
  expect(mapBox!.width).toBeGreaterThan(100);
  expect(mapBox!.height).toBeGreaterThan(100);

  // Check layout is vertical: aside should be below map (y > map.y)
  const aside = page.locator('aside').first();
  const asideBox = await aside.boundingBox();
  console.log(`Aside bounding box: ${JSON.stringify(asideBox)}`);
  expect(asideBox).not.toBeNull();
  // On mobile, aside should start below the map (y position > map y position)
  expect(asideBox!.y).toBeGreaterThan(mapBox!.y);

  await page.waitForFunction(() =>
    [...document.querySelectorAll('button')].some(b => b.textContent?.includes('DAY')),
    { timeout: 15000 },
  );

  // Expand DAY 2 on mobile
  const dayBtns = page.locator('button').filter({ hasText: 'DAY' });
  const dayCount = await dayBtns.count();
  await dayBtns.nth(dayCount >= 2 ? 1 : 0).click();
  await page.waitForTimeout(300);

  // Click a marker on mobile
  const markers = page.locator('.leaflet-marker-icon');
  const markerCount = await markers.count();
  expect(markerCount).toBeGreaterThan(0);
  await markers.nth(0).click({ force: true });
  await expect(page.locator('.leaflet-popup')).toBeVisible({ timeout: 5000 });
  await page.screenshot({ path: `${SS}/mobile-popup.png` });

  const popupCount = await page.locator('.leaflet-popup').count();
  console.log(`Mobile popup count: ${popupCount}`);
  expect(popupCount).toBeGreaterThan(0);
});
