import { test, expect } from '@playwright/test';

test.describe('Create plan happy path', () => {
  test('select preset → save → view schedule → check gear', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('百岳路線')).toBeVisible();

    // 套用 preset
    await page.getByRole('button', { name: /玉山主峰單攻/ }).click();
    await expect(page).toHaveURL(/\/map/);

    // 等地圖容器出現後儲存行程（避免 tile 需要外部網路的問題）
    await page.waitForSelector('.leaflet-container', { timeout: 10000 });
    await page.waitForTimeout(2000); // give map a moment to initialize

    // 等待儲存行程按鈕可點擊 (resolvedPath 已計算完成)
    const saveButton = page.getByRole('button', { name: '儲存行程' });
    await expect(saveButton).not.toBeDisabled({ timeout: 10000 });
    await saveButton.click();

    // 進到 schedule
    await expect(page).toHaveURL(/\/schedule\//);
    await expect(page.getByText(/玉山主峰/).first()).toBeVisible();
    await expect(page.locator('table')).toBeVisible();

    // 進到 gear
    await page.getByRole('button', { name: '裝備清單' }).click();
    await expect(page).toHaveURL(/\/gear\//);
    await expect(page.getByText('輕裝攻頂', { exact: false }).first()).toBeVisible();

    // 勾選一個物品
    const firstCheckbox = page.locator('.n-checkbox').first();
    await firstCheckbox.click();
    await expect(firstCheckbox).toHaveClass(/n-checkbox--checked/);

    // 回到 plans 列表
    await page.goto('/plans');
    await expect(page.locator('text=玉山主峰').first()).toBeVisible();
  });
});
