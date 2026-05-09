# Phase 2 設計文件 — 視覺化完整化 + 列印 + ESLint

- 日期：2026-05-09
- 作者：Peter Lu
- 狀態：Draft（待 brainstorming 階段最終確認）
- 前置：Phase 1 MVP（commit 619814f）已 ship 並使用過

## 1. 目標與範圍

把 Phase 1 留下的 V1 Gantt + V3 海拔曲線兩個視圖補齊，加上實用的列印功能，並修正 Phase 1 deferred 的 ESLint 9 flat config。

### 在範圍內

- **V1 Gantt**：每日獨立色塊 bar，bar 寬度比例 = 段落時長（樣式 G2）
- **V3 海拔曲線**：每日獨立小圖，x = 當日時間進度，y = 海拔（樣式 E3）
- **NTabs 切換**：PlanScheduleView 的行程表區塊改成 V1 / V2 / V3 三個 tab，預設 V2
- **列印**：按列印按鈕產出兩頁 PDF — 第 1 頁 V2 表格、第 2 頁裝備清單勾選表
- **ESLint 9 flat config**：取代 Phase 1 缺漏的 `.eslintrc.cjs`，恢復 `npm run lint`
- **共用服務抽出**：ScheduleGrouper（按 dayBreaks 切日）+ SegmentColor（依升降速判色）

### 不在範圍內

- V1 / V3 列印（列印只動 V2 + 裝備）
- 重型圖表函式庫（vis-timeline / ECharts），純 Vue + SVG 實作
- 列印含路線地圖縮圖（Leaflet 截圖難度高，延到 Phase 3 PWA tile 已快取後再做）
- 互動 chart 功能（hover popup、export PNG、縮放）— 用 SVG `<title>` 即可
- G05 等其他路線資料（屬 Phase 4 資料整理）
- PWA / Service Worker（Phase 3）

## 2. 主要決策摘要

| 面向 | 決定 |
|---|---|
| Phase 2 主軸 | 視覺化完整化 |
| V1 風格 | G2 段落色塊 bar（每日一條，bar flex 比例 = 段落時長） |
| V3 風格 | E3 多日分開（每日一張獨立 SVG 曲線） |
| 圖表技術 | 純 Vue + SVG + Tailwind，零新前端依賴 |
| Tab 切換 | Naive UI `NTabs` 包 V1 / V2 / V3 |
| 列印範圍 | 僅 V2 + 裝備清單附頁 |
| 列印機制 | screen / print 雙樹 + `@media print` CSS 切換 |
| 列印模板 | 自寫純 HTML `<table>` + `<ul>`（不用 NDataTable，CSS 控制乾淨） |
| ESLint | v9 flat config（`eslint.config.js`） |
| 共用邏輯抽出 | ScheduleGrouper + SegmentColor 兩個純函式 service |

## 3. 整體架構（Phase 2 動到的範圍）

### 新增檔案（6）

```
+ src/components/schedule/GanttView.vue       # V1 G2 風格
+ src/components/schedule/ElevationView.vue   # V3 E3 風格
+ src/components/schedule/PrintLayout.vue     # 列印專用模板
+ src/services/ScheduleGrouper.ts             # 按 dayBreaks 分組
+ src/services/SegmentColor.ts                # 段落顏色判定
+ eslint.config.js                            # ESLint 9 flat config
```

### 修改檔案（4）

```
~ src/views/PlanScheduleView.vue              # 加 NTabs + screen/print 雙樹 + load gear
~ src/components/schedule/TableView.vue       # 重構吃 ScheduleGrouper 輸出
~ src/style.css                                # 末尾追加 @media print 規則
~ package.json                                # 加 ESLint v9 deps + lint script 簡化
```

### 設計原則

- **視圖只負責呈現**：所有切日、顏色、座標計算邏輯放在 `services/`，元件吃計算結果
- **零 store 變動**：完全重用 Phase 1 的 `planStore.computedTimes` 與 `gearStore.suggestion`
- **重用既有元件樣式**：marker 顏色、TripTypeBadge 等沿用 Phase 1 慣例
- **列印模板獨立**：不嘗試「重用螢幕元件套用 print CSS」（會被 NDataTable／Naive UI 樣式纏住），自寫單純 HTML
- **元件薄、service 厚**：方便單元測試 service，元件主要是 snapshot / DOM 結構驗證

## 4. 技術棧增量

```
新增依賴（dev）：
  @typescript-eslint/parser
  @typescript-eslint/eslint-plugin
  vue-eslint-parser

零新前端 runtime 依賴。
```

## 5. 資料運算 Service

### 5.1 `ScheduleGrouper.ts`

```ts
import type { Plan, Route, RouteNode, SegmentTime } from '@/types';

export interface DayGroup {
  index: number;                    // 1-based
  date: string;                     // 'YYYY-MM-DD'
  startNode: RouteNode;
  endNode: RouteNode;
  startTime: string;                // 'HH:mm'
  endTime: string;                  // 'HH:mm'
  totalAdjustedMinutes: number;
  daySegments: SegmentTime[];
  peakNode?: RouteNode;             // 當日海拔最高節點
}

export interface GrouperInput {
  plan: Plan;
  route: Route;
  segments: SegmentTime[];          // 來自 planStore.computedTimes
}

export function groupByDayBreaks(input: GrouperInput): DayGroup[];
```

**演算法**：
1. 從 `plan.startDate + plan.startTime` 起算
2. 遍歷 segments，累加 `adjustedMinutes`
3. 遇到 `dayBreaks[i].afterNodeId === seg.toNodeId` → 結束當前 DayGroup，開始下一個（date + 1 day）
4. 每個 DayGroup 內 derive `startTime` / `endTime` / `peakNode`（取 daySegments 的 toNodeId 中海拔最大的）

### 5.2 `SegmentColor.ts`

```ts
import type { Route, SegmentTime } from '@/types';

export type SegmentTrend = 'climb' | 'descent' | 'flat';

export function segmentTrend(seg: SegmentTime, route: Route): SegmentTrend;
export function segmentColor(seg: SegmentTime, route: Route): string;
```

**規則**：
```
elevDelta = toNode.elevation - fromNode.elevation
hours = adjustedMinutes / 60
ratePerHour = elevDelta / hours

if (ratePerHour > 50) return 'climb' → '#fb923c'  // 橘
if (ratePerHour < -50) return 'descent' → '#86efac' // 綠
return 'flat' → '#fcd34d'  // 黃
```

`segmentColor` = `segmentTrend` + 顏色查表。分兩個函式方便單元測試與獨立使用。

## 6. UI 元件設計

### 6.1 `GanttView.vue`

**Props**：
```ts
defineProps<{
  plan: Plan;
  segments: SegmentTime[];
}>()
```

**運算**：
```ts
const route = computed(() => routesStore.getById(props.plan.routeId)!);
const days = computed(() => groupByDayBreaks({ plan: props.plan, route: route.value, segments: props.segments }));
```

**模板（精簡）**：
```vue
<div class="space-y-6">
  <section v-for="day in days" :key="day.index">
    <h3 class="text-sm font-bold text-emerald-600 mb-2">
      DAY {{ day.index }} · {{ day.date }} · 總計 {{ fmt(day.totalAdjustedMinutes) }}
    </h3>
    <div class="relative h-14">
      <span class="absolute left-0 top-0 text-xs">{{ day.startTime }}</span>
      <span class="absolute right-0 top-0 text-xs">{{ day.endTime }}</span>
      <div class="absolute inset-x-0 top-5 h-5 flex gap-px bg-white">
        <div v-for="(seg, idx) in day.daySegments" :key="idx"
             :style="{ flex: seg.adjustedMinutes, background: segmentColor(seg, route) }"
             :title="`${nodeName(seg.toNodeId)} +${fmt(seg.adjustedMinutes)}`" />
      </div>
      <span class="absolute left-0 top-12 text-xs text-gray-600">{{ day.startNode.name }}</span>
      <span class="absolute right-0 top-12 text-xs text-gray-600">{{ day.endNode.name }}</span>
    </div>
  </section>
</div>
```

**互動**：hover bar 由瀏覽器原生 `title` 顯示節點名 + 時長。不做 popup。

### 6.2 `ElevationView.vue`

**Props** 同 GanttView。

**運算**：
```ts
interface ElevationDay {
  index: number;
  date: string;
  startTime: string;
  endTime: string;
  totalMinutes: number;
  startNode: RouteNode;
  endNode: RouteNode;
  peakNode?: RouteNode;
  polylinePoints: string;     // SVG polyline points attr
  fillPath: string;           // 加底邊形成 area fill 的 SVG path
  highlights: Array<{
    x: number; y: number;
    name: string;
    elevation: number;
    time: string;
    type: 'peak' | 'hut' | 'trailhead';
  }>;
  yMin: number;               // 該日最低海拔（每 100m 取整）
  yMax: number;               // 該日最高海拔
}

const days = computed<ElevationDay[]>(...);
```

x 軸：當日累計時間（0 → totalMinutes，映射到 SVG x 20-380）
y 軸：海拔（yMin → yMax，反向映射到 SVG y 68 → 12）
**每日獨立 yMin/yMax**（不全行程共用），避免單日扁平化。

**模板**：見第 2 節（已展示）。

**dayColor 配色**：1=`#3b82f6`（藍）、2=`#a855f7`（紫）、3=`#ec4899`（粉）、循環。

### 6.3 `PrintLayout.vue`

只會在 `@media print` 時 visible。Props：
```ts
defineProps<{
  plan: Plan;
  route: Route;
  segments: SegmentTime[];
  gearSuggestion: SuggestOutput | null;  // 從 gearStore.suggestion
}>()
```

模板由 4 個 section 組成：
1. `<header class="print-header">` — 行程名 + metadata `<dl>`
2. `<section class="print-schedule">` — 純 `<table>` 帶 thead/tbody，自己 iterate `scheduleRows`（從 ScheduleGrouper 攤平回 row 結構）
3. `<section class="print-gear">` — 雙欄 `<ul>` 列出每分類所有物品，前面 `☐`
4. `<footer class="print-footer">` — 列印日期 + 上河版權標註

不重用 TableView / GearChecklist 元件。

### 6.4 `PlanScheduleView.vue` 修改

```vue
<div class="schedule-page p-6 max-w-5xl mx-auto">
  <NSpin :show="!plan">
    <template v-if="plan">
      <!-- 螢幕視圖 -->
      <div class="screen-only">
        <header>...</header>
        <DayBreakEditor />
        <NCard title="行程時刻表">
          <NTabs :default-value="'v2'">
            <NTabPane name="v1" tab="V1 Gantt">
              <GanttView :plan="plan" :segments="planStore.computedTimes" />
            </NTabPane>
            <NTabPane name="v2" tab="V2 表格">
              <TableView :plan="plan" :segments="planStore.computedTimes" />
            </NTabPane>
            <NTabPane name="v3" tab="V3 海拔">
              <ElevationView :plan="plan" :segments="planStore.computedTimes" />
            </NTabPane>
          </NTabs>
        </NCard>
      </div>

      <!-- 列印視圖 -->
      <div class="print-only">
        <PrintLayout :plan="plan" :route="route" :segments="planStore.computedTimes"
                      :gear-suggestion="gearStore.suggestion" />
      </div>
    </template>
  </NSpin>
</div>
```

`onMounted`：除 `loadPlan` + `computedTimes` 外，**也載 gear**：
```ts
await planStore.loadPlan(Number(props.planId));
if (planStore.currentPlan) {
  await gearStore.loadChecklist(planStore.currentPlan.id!);
  const totalMins = planStore.computedTimes.reduce((s, x) => s + x.adjustedMinutes, 0);
  const hasOvernight = planStore.currentPlan.dayBreaks.length > 0;
  const hasCamping = planStore.currentPlan.dayBreaks.some(b => b.type === 'camp');
  await gearStore.refreshSuggestion({
    totalHours: totalMins / 60,
    hasOvernight,
    hasCamping,
  });
}
```

列印按鈕 disabled 直到 `gearStore.suggestion` 有值。

### 6.5 `TableView.vue` 重構

把內嵌的「按 dayBreaks 切日」邏輯拿掉，改吃 `ScheduleGrouper.groupByDayBreaks` 輸出，攤平成 row[]。對外行為 100% 一致。

## 7. 列印 CSS（追加於 `src/style.css` 末尾）

```css
@media screen {
  .print-only { display: none; }
}

@media print {
  .screen-only { display: none !important; }
  .print-only { display: block; }
  body { background: white; color: black; }

  @page { margin: 1.5cm 1.2cm; }

  .print-header h1 { margin: 0 0 4px; font-size: 16pt; }
  .print-header dl { display: grid; grid-template-columns: repeat(2, 1fr);
                     font-size: 10pt; gap: 2px 16px; margin: 4px 0 16px; }
  .print-header dt { display: inline; font-weight: bold; margin-right: 6px; }
  .print-header dd { display: inline; margin: 0; }

  .print-schedule { page-break-after: always; }
  .print-schedule table { width: 100%; border-collapse: collapse; font-size: 9pt; }
  .print-schedule th, .print-schedule td {
    border: 1px solid #999; padding: 3px 5px; text-align: left;
  }
  .print-schedule th { background: #f3f4f6; }
  .print-schedule thead { display: table-header-group; }
  .print-schedule tr { page-break-inside: avoid; }
  .print-schedule tr.is-break { background: #fef3c7; }

  .print-gear h2 { margin-top: 0; }
  .print-gear h3 { font-size: 11pt; margin: 12px 0 4px;
                   border-bottom: 1px solid #ccc; }
  .print-gear ul { list-style: none; padding: 0; columns: 2; column-gap: 24px; }
  .print-gear li { font-size: 10pt; padding: 1px 0; break-inside: avoid; }

  .print-footer { font-size: 8pt; color: #666; margin-top: 16px;
                  border-top: 1px solid #ccc; padding-top: 4px; }
}
```

## 8. ESLint 9 Flat Config

### `eslint.config.js`

```js
import js from '@eslint/js';
import vue from 'eslint-plugin-vue';
import vueParser from 'vue-eslint-parser';
import tsParser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';

export default [
  {
    ignores: [
      'dist/**', 'node_modules/**',
      '.worktrees/**', '.superpowers/**',
      'tests/e2e/**', 'public/**',
    ],
  },
  js.configs.recommended,
  ...vue.configs['flat/recommended'],
  {
    files: ['**/*.{ts,vue}'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        ecmaVersion: 2022,
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
      },
    },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      'vue/multi-word-component-names': 'off',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-undef': 'off',          // TS handles
      'no-unused-vars': 'off',    // delegate to TS plugin
    },
  },
];
```

### `package.json`

```json
"lint": "eslint ."
```

依賴新增：`@typescript-eslint/parser`、`@typescript-eslint/eslint-plugin`、`vue-eslint-parser`（其餘已在 Phase 1）。

## 9. 邊界條件處理

| 情境 | 對策 |
|---|---|
| 單日行程（無 dayBreaks） | ScheduleGrouper 回 1 個 DayGroup，UI 正常 |
| 行程跨年（startDate 12/31） | 用 Date 物件加日數，跨月跨年自動處理 |
| 海拔資料缺失（elevation 0） | SegmentColor fallback `flat` → 黃；ElevationView 顯示 0（異常會被使用者察覺） |
| 行程超長（10+ 天縱走） | 各日 stack 垂直顯示，無上限。列印自動 page-break |
| 列印時 gear 未載完 | 按鈕 disabled 至 `gearStore.suggestion` 有值 |
| 列印 dialog 取消 | 純 CSS 機制，不需特殊處理 |
| 段落時間 = 0 分鐘（退化） | GanttView 跳過該段不渲染 bar；ElevationView 不影響（仍畫線） |
| ESLint 配置遇到 .vue 檔 parse 失敗 | flat config 用 vue-eslint-parser 包 ts-parser，能正確處理混合語法 |

## 10. 測試策略

### 單元測試（Vitest）

```
services/ScheduleGrouper.test.ts
  - 單日行程：1 個 DayGroup
  - 一個過夜：2 個 DayGroup，第二日 startNode = 切點 toNode
  - 三日縱走：3 個 DayGroup
  - peakNode 判定：取該日 daySegments toNodeId 中 elevation 最大者
  - date 推算：startDate + 過夜天數
  - startTime / endTime 從 segments 第一/末段取 arrival
services/SegmentColor.test.ts
  - 上升 100m / 1h → climb (橘)
  - 下降 100m / 1h → descent (綠)
  - 上升 30m / 1h → flat (黃)
  - 平地 → flat (黃)
  - 0 分鐘段（退化）→ flat 不 throw
```

### 元件測試（Vue Test Utils）

```
components/schedule/GanttView.test.ts
  - 給 segments + plan 渲染正確日數 section
  - bar flex 比例符合 adjustedMinutes
  - bar background = SegmentColor 預期輸出
  - 包含 startNode / endNode 名稱
components/schedule/ElevationView.test.ts
  - polyline points 數量 = daySegments + 1
  - 每日獨立 yMin/yMax
  - peak / hut / trailhead markers 出現在該日對應位置
components/schedule/PrintLayout.test.ts
  - 表格 row 數 = scheduleRows 數
  - 裝備清單分類數 = gearSuggestion.categories.length
  - footer 包含「上河文化」字樣（版權標註）
```

### E2E（Playwright）— 擴充 `create-plan.spec.ts`

```
- 切到 V1 tab → .gantt-view 元素 visible
- 切到 V3 tab → SVG element visible
- 切回 V2 → table visible
- 點列印按鈕 → mock window.print 被呼叫一次
- 模擬 @media print → screen-only hidden, print-only visible
```

### 涵蓋率目標

服務層 90%+（純函式好測），元件 70%+（snapshot + DOM 結構），E2E 跑通 happy path。

## 11. 階段性交付建議

### Step 1（後端準備）
1. 寫 ScheduleGrouper 含測試
2. 寫 SegmentColor 含測試
3. TableView 重構吃 ScheduleGrouper

### Step 2（兩個視圖）
4. GanttView 含測試
5. ElevationView 含測試

### Step 3（列印 + 整合）
6. PrintLayout 含測試
7. PlanScheduleView 加 NTabs + 雙樹 + load gear
8. style.css 加 @media print

### Step 4（工具）
9. ESLint flat config + 安裝 deps
10. 跑 `npm run lint` 修首次掃出的問題（estimated 5-15 個 minor warnings）

### Step 5（E2E）
11. 擴充 create-plan E2E

## 12. 安全 / 隱私 / 版權

- Phase 2 不引入新外部請求（純前端 SVG 渲染）
- 列印 footer 標註資料來源（與 Phase 1 README 立場一致）
- ESLint 不會洩漏程式碼到第三方 service

## 13. 待議 / 未來

- V1 / V3 列印（可能延到 Phase 4 整理完更多路線後再評估視覺需求）
- chart 互動（hover detail popup、export PNG）— 視使用回饋
- 列印含路線地圖縮圖 — 等 Phase 3 PWA tile 快取完成後實作
