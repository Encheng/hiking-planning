import { test, expect } from '@playwright/test';

const SS = '/tmp/p25-zoom-fix';

test('zoom animation - markers and GPX scale correctly', async ({ page }) => {
  const consoleErrors: string[] = [];
  const consoleLogs: string[] = [];

  page.on('console', (msg) => {
    const text = msg.text();
    if (msg.type() === 'error') {
      consoleErrors.push(text);
      console.log(`[BROWSER ERROR] ${text}`);
    }
    consoleLogs.push(`${msg.type()}: ${text}`);
  });

  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  // Apply 玉山主峰單攻 preset
  const presetBtn = page.locator('a, button').filter({ hasText: '玉山' }).first();
  await presetBtn.click();
  await page.waitForURL('**/map**', { timeout: 10000 });
  await page.waitForSelector('.leaflet-container', { timeout: 15000 });
  await page.waitForTimeout(2000);

  await page.screenshot({ path: `${SS}/01-initial.png` });
  console.log('Initial page loaded');

  // Get the map element center for mouse interactions
  const mapEl = page.locator('.leaflet-container');
  const mapBox = await mapEl.boundingBox();
  expect(mapBox).not.toBeNull();
  const cx = mapBox!.x + mapBox!.width / 2;
  const cy = mapBox!.y + mapBox!.height / 2;

  // Record marker positions before zoom
  const markersBefore = await page.locator('.leaflet-marker-icon').count();
  console.log(`Markers before zoom: ${markersBefore}`);
  expect(markersBefore).toBeGreaterThan(0);

  // Test zoom cycles on initial (photo) tile
  await page.mouse.move(cx, cy);
  for (let i = 0; i < 3; i++) {
    await page.mouse.wheel(0, -500);
    await page.waitForTimeout(600);
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(600);
  }
  await page.screenshot({ path: `${SS}/02-after-zoom-photo.png` });
  const photoErrors = [...consoleErrors];
  console.log(`Errors after photo tile zoom: ${photoErrors.length}`);

  // Switch to 通用版 tile and zoom
  const nlscBtn = page.locator('button').filter({ hasText: '通用版' });
  await nlscBtn.click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: `${SS}/03-tile-nlsc.png` });

  const errorsBeforeNlscZoom = consoleErrors.length;
  for (let i = 0; i < 3; i++) {
    await page.mouse.wheel(0, -500);
    await page.waitForTimeout(600);
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(600);
  }
  await page.screenshot({ path: `${SS}/04-nlsc-zoom.png` });
  const nlscErrors = consoleErrors.slice(errorsBeforeNlscZoom);
  console.log(`Errors after NLSC tile zoom: ${nlscErrors.length}`);
  if (nlscErrors.length > 0) console.log('NLSC errors:', nlscErrors);

  // Switch to OSM tile and zoom
  const osmBtn = page.locator('button').filter({ hasText: 'OSM' });
  await osmBtn.click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: `${SS}/05-tile-osm.png` });

  const errorsBeforeOsmZoom = consoleErrors.length;
  for (let i = 0; i < 3; i++) {
    await page.mouse.wheel(0, -500);
    await page.waitForTimeout(600);
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(600);
  }
  await page.screenshot({ path: `${SS}/06-osm-zoom.png` });
  const osmErrors = consoleErrors.slice(errorsBeforeOsmZoom);
  console.log(`Errors after OSM tile zoom: ${osmErrors.length}`);
  if (osmErrors.length > 0) console.log('OSM errors:', osmErrors);

  // Final marker count
  const finalMarkerCount = await page.locator('.leaflet-marker-icon').count();
  console.log(`Final marker count: ${finalMarkerCount}`);
  expect(finalMarkerCount).toBeGreaterThan(0);

  // Check for the original bug signature
  const projectErrors = consoleErrors.filter(e => e.includes('project') || e.includes('Cannot read'));
  console.log(`Total console errors: ${consoleErrors.length}`);
  console.log(`Project-related errors: ${projectErrors.length}`);

  expect(projectErrors).toHaveLength(0);
  expect(consoleErrors).toHaveLength(0);
});

test('detect rebuild during zoom', async ({ page }) => {
  const consoleErrors: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const presetBtn = page.locator('a, button').filter({ hasText: '玉山' }).first();
  await presetBtn.click();
  await page.waitForURL('**/map**', { timeout: 10000 });
  await page.waitForSelector('.leaflet-container', { timeout: 15000 });
  await page.waitForTimeout(2000);

  // Track marker DOM changes as a proxy for rebuild
  const result = await page.evaluate(() => {
    return new Promise<{ changes: number; errors: string[] }>((resolve) => {
      let changes = 0;
      const domErrors: string[] = [];
      const markerPane = document.querySelector('.leaflet-marker-pane');
      if (!markerPane) { resolve({ changes: -1, errors: ['no marker pane'] }); return; }

      const observer = new MutationObserver((mutations) => {
        const removals = mutations.filter(m => m.removedNodes.length > 0);
        if (removals.length > 0) {
          changes++;
          console.log(`[MARKER REBUILD DETECTED] DOM change #${changes} during zoom`);
        }
      });
      observer.observe(markerPane, { childList: true, subtree: true });

      const map = (window as any).__leafletMap;
      if (!map) { resolve({ changes: -99, errors: ['no __leafletMap'] }); return; }

      const currentZoom = map.getZoom();
      console.log(`Starting zoom test from zoom level ${currentZoom}`);

      // Zoom in
      map.setZoom(currentZoom + 2, { animate: true });
      setTimeout(() => {
        // Zoom out
        map.setZoom(currentZoom, { animate: true });
        setTimeout(() => {
          observer.disconnect();
          resolve({ changes, errors: domErrors });
        }, 1500);
      }, 1500);
    });
  });

  console.log(`Marker pane DOM changes during zoom: ${result.changes}`);
  console.log(`Console errors: ${consoleErrors.length}`);

  if (result.changes > 0) {
    console.log('BUG CONFIRMED: rebuild() fired during zoom animation!');
  } else if (result.changes === 0) {
    console.log('No rebuild during zoom - behavior looks correct');
  }

  await page.screenshot({ path: `${SS}/rebuild-during-zoom.png` });

  // Check no errors
  const projectErrors = consoleErrors.filter(e => e.includes('project') || e.includes('Cannot read'));
  expect(projectErrors).toHaveLength(0);
  expect(result.changes).toBe(0);
});

test('tile switch then zoom - detect stale listener bug', async ({ page }) => {
  const consoleErrors: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const presetBtn = page.locator('a, button').filter({ hasText: '玉山' }).first();
  await presetBtn.click();
  await page.waitForURL('**/map**', { timeout: 10000 });
  await page.waitForSelector('.leaflet-container', { timeout: 15000 });
  await page.waitForTimeout(2000);

  // Switch tiles multiple times then zoom - this is where the original bug manifested
  const tiles = [
    { selector: '通用版', name: 'nlsc' },
    { selector: 'OSM', name: 'osm' },
    { selector: '通用版', name: 'nlsc2' },
    { selector: '正射影像', name: 'photo' },
  ];

  const mapEl = page.locator('.leaflet-container');
  const mapBox = await mapEl.boundingBox();
  const cx = mapBox!.x + mapBox!.width / 2;
  const cy = mapBox!.y + mapBox!.height / 2;

  for (const tile of tiles) {
    const btn = page.locator('button').filter({ hasText: tile.selector });
    await btn.click();
    await page.waitForTimeout(500);

    const beforeErrors = consoleErrors.length;
    await page.mouse.move(cx, cy);
    await page.mouse.wheel(0, -500);
    await page.waitForTimeout(600);
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(600);

    const newErrors = consoleErrors.slice(beforeErrors);
    console.log(`Tile: ${tile.name}, new errors after zoom: ${newErrors.length}`);
    if (newErrors.length > 0) {
      console.log(`Errors on ${tile.name}:`, newErrors);
    }
    await page.screenshot({ path: `${SS}/tile-${tile.name}.png` });
  }

  console.log(`Total errors: ${consoleErrors.length}`);
  expect(consoleErrors).toHaveLength(0);
});
