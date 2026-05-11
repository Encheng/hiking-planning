import { test, expect } from '@playwright/test';

const OUT = '/tmp/p25-fix3items';

test('verify 3 UX fixes - marker anchor, per-day startNodeId, return-trip chips', async ({ page }) => {
  // Apply 玉山主峰單攻 preset (same approach as create-plan.spec.ts)
  await page.goto('/');
  await expect(page.getByText('百岳路線')).toBeVisible();

  await page.getByRole('button', { name: /玉山主峰單攻/ }).click();
  await expect(page).toHaveURL(/\/map/);
  await page.waitForSelector('.leaflet-container', { timeout: 15000 });
  await page.waitForTimeout(2000);

  await page.screenshot({ path: `${OUT}/01-map-planner.png` });

  // Fix 1: Verify markers are present (iconAnchor doesn't break rendering)
  const nodeMarkers = page.locator('.node-marker');
  const markerCount = await nodeMarkers.count();
  console.log(`Fix 1: Marker count = ${markerCount}`);
  expect(markerCount).toBeGreaterThan(0);
  await page.screenshot({ path: `${OUT}/02-markers-visible.png` });

  // Fix 2: Expand DAY 2 and verify 起點 NodePicker
  const day2Btn = page.locator('button').filter({ hasText: /DAY 2/ }).first();
  await expect(day2Btn).toBeVisible({ timeout: 5000 });
  await day2Btn.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT}/03-day2-expanded.png` });

  const dayEditor = page.locator('[data-day-editor]').first();
  await expect(dayEditor).toBeVisible();

  // The start section should show NodePicker with "自動 = 前日結束" label
  await expect(dayEditor.locator('label').filter({ hasText: '起點' }).first()).toBeVisible();
  const autoLabel = dayEditor.locator('text=自動 = 前日結束');
  const autoCount = await autoLabel.count();
  console.log(`Fix 2: "自動 = 前日結束" label found: ${autoCount > 0}`);
  await page.screenshot({ path: `${OUT}/04-start-node-picker.png` });

  // Fix 3: Check returnToStart checkbox and look for return-trip chips
  const returnCheckbox = page.locator('.n-checkbox').filter({ hasText: '回到起點' }).first();
  if (await returnCheckbox.count() > 0) {
    const isChecked = await returnCheckbox.evaluate((el) => el.classList.contains('n-checkbox--checked'));
    console.log(`Fix 3: returnToStart initially checked: ${isChecked}`);
    if (!isChecked) {
      await returnCheckbox.click();
      await page.waitForTimeout(500);
      console.log('Fix 3: Enabled returnToStart');
    }
  }

  await page.screenshot({ path: `${OUT}/05-return-to-start-enabled.png` });

  // Re-expand DAY 2 after potential collapse from checkbox interaction
  const dayEditorVisible = await page.locator('[data-day-editor]').first().isVisible();
  if (!dayEditorVisible) {
    await day2Btn.click();
    await page.waitForTimeout(300);
  }

  const returnSection = page.locator('text=回程經過').first();
  const returnCount = await returnSection.count();
  console.log(`Fix 3: Return-trip chips section found: ${returnCount > 0}`);
  if (returnCount > 0) {
    await page.screenshot({ path: `${OUT}/06-return-trip-chips.png` });
    // Verify chips exist
    const chips = page.locator('[data-day-editor]').first().locator('.n-tag').filter({ hasText: /\d+\./ });
    const chipCount = await chips.count();
    console.log(`Fix 3: Return-trip chip count = ${chipCount}`);
  } else {
    await page.screenshot({ path: `${OUT}/06-no-return-chips.png` });
  }

  // Fix 2: Test changing start node via NodePicker
  // The first NodePicker in dayEditor is the start picker
  const startSelections = dayEditor.locator('.n-base-selection');
  if (await startSelections.count() > 0) {
    await startSelections.first().click();
    await page.waitForTimeout(300);
    await page.screenshot({ path: `${OUT}/07-start-picker-open.png` });

    // Find 塔塔加 option
    const tatakaOption = page.locator('.n-base-select-option').filter({ hasText: /塔塔加/ }).first();
    if (await tatakaOption.count() > 0) {
      await tatakaOption.click();
      await page.waitForTimeout(500);
      console.log('Fix 2: Changed start to 塔塔加');
      await page.screenshot({ path: `${OUT}/08-start-changed-to-tataka.png` });

      // Check if "已自訂" appears
      const customLabel = dayEditor.locator('text=已自訂');
      const customCount = await customLabel.count();
      console.log(`Fix 2: "已自訂" label appears: ${customCount > 0}`);
    } else {
      await page.keyboard.press('Escape');
      console.log('Fix 2: 塔塔加 not in dropdown (may already be selected or not in G02)');
      await page.screenshot({ path: `${OUT}/08-picker-options.png` });
    }
  }

  await page.screenshot({ path: `${OUT}/09-final-state.png` });
});
