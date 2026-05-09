# 台灣百岳登山規劃 App — 設計文件

- 日期：2026-05-09
- 作者：Peter Lu
- 狀態：Draft（待 brainstorming 階段最終確認）

## 1. 專案目標與範圍

打造一個基於上河文化《2020 高山百岳地形圖》步程資料的個人登山規劃工具。功能上分兩大區塊：

1. **行程規劃**：在地圖上點選起終點 → 自動解析路徑、套用倍率估算時間、自動建議多日切點 → 產生可視化行程表（Gantt / 表格 / 海拔曲線）。
2. **裝備清單**：依行程類型自動推薦對應分類（輕裝攻頂 / 長日單攻 / 山屋過夜 / 紮營過夜），可勾選、加自訂物品、跨行程繼承。

### 使用範圍與版權

- **僅供個人使用**，不公開部署、不上架商店、不發布到任何 GitHub 公開 repo。
- 上河文化的步程數據為其商業資料；本 App 將其數位化內建僅在私人範圍內合理使用，不再分發。
- 列印行程表的 footer 標註「資料來源：上河文化《2020 高山百岳地形圖》（個人使用）」。

### 路線範圍

涵蓋上河 G01–G20 共 20 條百岳路線（玉山群峰、聖稜 Y 型、北一段、能高安東軍、丹大東郡、馬博拉斯、南二段、新康橫斷、南一段、北大武等）。

### 不在範圍

- 公開部署、社群分享、雲端同步
- 即時 GPS 定位 / 軌跡比對（保留未來擴充的可能）
- 天氣 API、智慧推薦類「過度設計」功能
- 跨用戶協作

## 2. 主要設計決策（討論結果摘要）

| 面向 | 決定 | 備註 |
|---|---|---|
| 使用範圍 | 自用 | 不公開、不商業 |
| 路線範圍 | 全 20 條 G 系列 | 分階段交付，先做 1-2 條跑通 |
| 主互動 | 地圖優先（Leaflet） | 上河節點 pin 在 GPX 軌跡上 |
| 點選行為 | 僅上河節點可點（B2 模式） | 簡單、最準確 |
| 多日切點 | 自動建議（山屋資料庫）+ 手動可改寫 | DayBreaker 服務 |
| 裝備清單 | 互動勾選 + 自訂物品 + 跨行程繼承 | 不做天氣動態推薦 |
| 行程表呈現 | V1 Gantt（預設）+ V2 表格 + V3 海拔曲線 | tab 切換 |
| 裝置目標 | 桌面規劃 + 手機 PWA 離線使用 | tile 快取 7 天過期 |
| 底圖預設 | 魯地圖 | 可切經建版 / OSM |
| UI 元件庫 | Naive UI | Vue 3 原生 |

## 3. 整體架構

```
┌──────────────────────────────────────────────────────────────┐
│                       UI 層 (Vue + Naive UI)                 │
├──────────┬──────────┬──────────┬──────────┬──────────────────┤
│ /map     │/planner  │/schedule │/gear     │/routes (路線清單)│
│ 地圖視圖  │行程編輯器 │行程表    │裝備清單   │管理 G01–G20      │
└──────────┴──────────┴──────────┴──────────┴──────────────────┘
         │           │           │            │
         ▼           ▼           ▼            ▼
┌──────────────────────────────────────────────────────────────┐
│                  Pinia stores (responsive state)             │
│  • routesStore   讀取 20 條路線靜態 JSON                     │
│  • planStore     當前行程：節點序列、倍率、日切、紮營點       │
│  • gearStore     裝備清單模板 + 各行程勾選狀態 + 自訂物品     │
│  • mapStore      地圖層、選中節點、UI 狀態                   │
│  • settingsStore 預設倍率、底圖偏好                          │
└──────────────────────────────────────────────────────────────┘
         │           │           │            │
         ▼           ▼           ▼            ▼
┌──────────────────────────────────────────────────────────────┐
│                       Domain 服務層                          │
│  • PathResolver   起終點 → 節點序列（圖搜尋 BFS）            │
│  • TimeCalculator 套倍率、累計、判定行程類型                  │
│  • DayBreaker     依山屋資料庫切日，可手動覆寫                │
│  • GearSuggester  行程類型 → 推薦裝備分類                    │
│  • GpxNodeMatcher Snap GPX 點 ↔ 上河節點                     │
│  • TileCacheManager PWA 離線磚管理（含 7 天過期）            │
└──────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│   資料 / 持久層                                              │
│  • /assets/data/routes/G01.json … G20.json   靜態路線        │
│  • /assets/data/gpx/G01.gpx       … G20.gpx  GPX 軌跡        │
│  • /assets/data/huts.json    山屋座標 + 容量                 │
│  • /assets/data/gear-templates.json  4 類裝備預設            │
│  • IndexedDB (Dexie):                                        │
│      - plans          (使用者建立的行程)                     │
│      - gearChecklists (各行程裝備勾選)                      │
│      - customItems    (使用者自訂裝備)                       │
│      - tileCache      (PWA 離線地圖磚, 7d TTL)               │
└──────────────────────────────────────────────────────────────┘
```

### 設計原則

- **服務層純函式**：接 plain data 進、plain data 出，不依賴 Pinia / Vue。便於單元測試。
- **Pinia store 薄**：actions 只是 `services.calc(state) → state.value = result`。
- **靜態資料 vs 動態資料切開**：路線資料 build-time 載入，行程資料 runtime IndexedDB。
- **`map/` 元件夾為 Leaflet 唯一接觸點**：未來想換 MapLibre 或加 3D 只動這資料夾。

## 4. 技術棧

```
框架：     Vue 3 + Composition API + <script setup> + TypeScript
建構：     Vite 5 + vite-plugin-pwa
狀態：     Pinia
路由：     Vue Router
地圖：     Leaflet 1.9 + leaflet-gpx + leaflet.markercluster
Geo：      @turf/turf（距離、最近點計算）
GPX：      gpx-parser-builder（讀 GPX 檔）
儲存：     IndexedDB via Dexie.js
UI：       Naive UI + Tailwind CSS
時間軸：   vis-timeline（V1 Gantt）
圖表：     Apache ECharts（V3 海拔曲線）
PDF 列印： window.print() + @media print stylesheet
測試：     Vitest（單元 / 元件）+ Playwright（E2E）
```

### 底圖來源

- 魯地圖（預設）：`https://rudy-tile.appspot.com/{z}/{x}/{y}.png`
- 經建版二萬五（內政部 NLSC WMTS 公開）
- OpenStreetMap（fallback）

## 5. 資料模型

### 5.1 靜態路線 JSON：`/assets/data/routes/G02.json`

```jsonc
{
  "id": "G02",
  "name": "玉山群峰縱走",
  "version": "2020-update",
  "source": "上河文化《2020高山百岳地形圖》",
  "nodes": [
    {
      "id": "n_tataka",
      "name": "塔塔加遊客中心",
      "lat": 23.4756, "lng": 120.8932,
      "elevation": 2610,
      "category": "trailhead",
      "hutId": null,
      "tags": ["parking", "toilet"]
    },
    {
      "id": "n_paiyun",
      "name": "排雲山莊",
      "lat": 23.4731, "lng": 120.9534, "elevation": 3402,
      "category": "hut",
      "hutId": "hut_paiyun"
    },
    {
      "id": "n_yushan_main",
      "name": "玉山主峰",
      "lat": 23.4707, "lng": 120.9572, "elevation": 3952,
      "category": "peak",
      "tags": ["100mt"]
    }
  ],
  "edges": [
    {
      "from": "n_tataka", "to": "n_shang_dongpu",
      "minutes_forward": 10, "minutes_backward": 10,
      "source": "G02_hiking.jpg"
    },
    {
      "from": "n_paiyun", "to": "n_yushan_main",
      "minutes_forward": 90, "minutes_backward": 60,
      "source": "xG02-2.jpg"
    }
  ],
  "presets": [
    {
      "id": "G02-main",
      "name": "玉山主峰單攻 (2天1夜)",
      "startNodeId": "n_tataka",
      "endNodeId": "n_yushan_main",
      "viaNodeIds": ["n_paiyun"],
      "suggestedDayBreaks": [{ "atNodeId": "n_paiyun", "type": "hut" }]
    }
  ]
}
```

`category` 列舉：`trailhead | hut | peak | junction | waypoint | water`。

### 5.2 山屋：`/assets/data/huts.json`

```jsonc
[
  {
    "id": "hut_paiyun",
    "name": "排雲山莊",
    "lat": 23.4731, "lng": 120.9534, "elevation": 3402,
    "capacity": 116,
    "type": "hut",
    "needPermit": true,
    "operator": "玉管處"
  }
]
```

`type` 列舉：`hut | shelter | campsite`。

### 5.3 裝備預設：`/assets/data/gear-templates.json`

```jsonc
{
  "categories": [
    {
      "id": "light_summit",
      "name": "輕裝攻頂 (≤4h)",
      "matchCondition": { "maxHours": 4, "overnight": false },
      "items": [
        { "id": "i_water_1l", "name": "水 1L", "essential": true, "weight_g": 1000 },
        { "id": "i_snack", "name": "行動糧", "essential": true },
        { "id": "i_raincoat", "name": "輕便雨衣", "essential": true }
      ]
    },
    { "id": "long_day", "name": "長日單攻 (>4h)", "matchCondition": { "maxHours": 99, "overnight": false }, "items": ["...見資料整理工作 D"] },
    { "id": "overnight_hut", "name": "山屋過夜", "matchCondition": { "minNights": 1, "camping": false }, "items": ["...見資料整理工作 D"] },
    { "id": "overnight_camp", "name": "紮營過夜", "matchCondition": { "minNights": 1, "camping": true }, "items": ["...見資料整理工作 D"] }
  ]
}
```

> 註：以上其他三個分類的 `items` 內容於資料整理工作 D 階段填入。此處僅展示 schema 結構。

`GearSuggester` 邏輯：每個分類的 `matchCondition` 跟當前 plan 比對，**命中的分類全部 union 顯示**（紮營行程會看到「紮營」+「山屋」+「長日」+「輕裝」所有分類，因紮營含這些情境）。

### 5.4 IndexedDB（Dexie）

```ts
db.version(1).stores({
  plans:           '++id, name, routeId, startDate, createdAt',
  gearChecklists:  '++id, planId',
  customItems:     '++id, name, lastUsedInPlanId',
  tileCache:       'url, expiresAt'
});

interface Plan {
  id?: number;
  name: string;
  routeId: string;
  startNodeId: string;
  endNodeId: string;
  nodeSequence: string[];
  paceMultiplier: number;
  startDate: string;
  startTime: string;
  dayBreaks: Array<{
    afterNodeId: string;
    type: 'hut' | 'shelter' | 'camp' | 'manual';
    hutId?: string;
  }>;
  tripType: 'light_summit' | 'long_day' | 'overnight_hut' | 'overnight_camp';
  notes?: string;
}

interface GearChecklist {
  id?: number;
  planId: number;
  checkedItemIds: string[];
  removedTemplateIds: string[];
}

interface CustomItem {
  id?: number;
  name: string;
  weightGrams?: number;
  defaultCategories: string[];
  lastUsedInPlanId?: number;
}

interface CachedTile {
  url: string;
  blob: Blob;
  expiresAt: number;
}
```

## 6. 服務層 API

### `PathResolver`

```ts
interface PathInput {
  route: Route;
  startNodeId: string;
  endNodeId: string;
  viaNodeIds?: string[];
}

interface PathOutput {
  forward: string[];
  backward: string[];
  combined: string[];
  isLoop: boolean;
  warnings: string[];
}

resolvePath(input: PathInput): PathOutput
```

實作：把 nodes/edges 建成無向 adjacency list，用 BFS 找節點數最少的路徑。`viaNodeIds` 用串接子路徑實作。回程預設 = 反向序列。

### `TimeCalculator`

```ts
interface SegmentTime {
  fromNodeId: string;
  toNodeId: string;
  baseMinutes: number;
  adjustedMinutes: number;
  arrivalTime: string;
  cumulativeMinutes: number;
  direction: 'forward' | 'backward';
}

calculateTimes(input: {
  route: Route;
  nodeSequence: string[];
  paceMultiplier: number;
  startDateTime: string;
}): { segments: SegmentTime[]; totalMinutes: number; totalAdjustedMinutes: number }
```

每段查 `route.edges`，看方向取 `minutes_forward` 或 `minutes_backward`。

### `DayBreaker`

```ts
suggestBreaks(input: {
  route: Route;
  segments: SegmentTime[];
  huts: Hut[];
  maxDailyHours: number;        // 預設 8
  preferredBreakType: 'hut' | 'shelter' | 'auto';
}): DayBreak[]
```

演算法：累加 `adjustedMinutes`，當累計 > `maxDailyHours * 60` 時，回退找前面 60 分鐘內最近的山屋節點作為切點；找不到則切在當前節點並標 type=`camp`。

### `GearSuggester`

```ts
suggestGear(input: {
  totalHours: number;
  hasOvernight: boolean;
  hasCamping: boolean;
  customItems: CustomItem[];
  lastChecklist?: GearChecklist;
}): {
  tripType: 'light_summit' | 'long_day' | 'overnight_hut' | 'overnight_camp';
  categories: Array<{
    id: string;
    name: string;
    items: Array<GearItem & { source: 'template' | 'custom' | 'last_trip' }>;
  }>;
}
```

### `GpxNodeMatcher`

```ts
// 開發期：批次匹配 GPX waypoints 到上河節點名（Levenshtein 字串相似度）
matchNodesToGpx(nodes: NodeWithName[], gpxFile: GpxData): TagSuggestion[]

// 執行期：使用者點地圖某點 → 找最近上河節點
findNearestNode(latlng: LatLng, route: Route, threshold_m: number): Node | null
```

### `TileCacheManager`

- 寫入時記 `expiresAt = now + 7 days`
- App 啟動時跑一次 `db.tileCache.where('expiresAt').below(Date.now()).delete()`
- 讀取時若該 tile 過期但 SW 仍有命中，先回傳舊 tile，同時觸發背景刷新

## 7. Vue 元件結構

```
src/
  components/
    map/
      MapCanvas.vue          # Leaflet container
      NodeMarkerLayer.vue    # 上河節點 pin（依 category icon）
      GpxLayer.vue           # leaflet-gpx 軌跡
      TileSwitcher.vue       # 魯地圖 / 經建版 / OSM 切換
    planner/
      PlanForm.vue           # 倍率、日期、切點編輯
      DayBreakEditor.vue
      PathPreview.vue
    schedule/
      ScheduleTabs.vue       # V1 / V2 / V3 切換
      GanttView.vue          # V1
      TableView.vue          # V2
      ElevationView.vue      # V3
    gear/
      GearChecklist.vue
      CustomItemForm.vue
      GearCategorySection.vue
    common/
      PaceSlider.vue
      TripTypeBadge.vue
  views/
    RoutesListView.vue       # /routes
    MapPlannerView.vue       # /map
    PlanScheduleView.vue     # /schedule/:planId
    GearChecklistView.vue    # /gear/:planId
    PlansListView.vue        # /plans
    SettingsView.vue         # /settings — 預設倍率、底圖偏好、儲存空間檢視、清理快取、匯出/匯入備份
  stores/         # 5 個 Pinia stores
  services/       # 6 個服務（純函式）
  data/           # 靜態 JSON / GPX
  db/             # Dexie 設定 + schemas
```

## 8. 主要使用者流程

### Flow 1 — 從零建立行程

1. `/routes` 選 G02 玉山群峰
2. 跳到 `/map?route=G02`，Leaflet 載入魯地圖底圖 + GPX 軌跡 + 節點 pin
3. 點起點 pin（marker 變綠色「起」）
4. 點終點 pin（marker 變紅色「終」）
5. `PathResolver` BFS 解出路徑（往返自動補上）
6. 顯示「行程預覽」：總時長、需幾天、建議切點、倍率 slider（預設 1.2x）、出發日期 / 時間
7. 按「儲存行程」→ 寫入 IndexedDB
8. 跳到 `/schedule/{planId}`，預設 V1 Gantt 視圖
9. 自動跳出裝備清單邊欄（`GearSuggester` 算出 tripType，顯示對應分類）

### Flow 2 — 套用 preset

`/routes` 每條路線下方列 `presets`（如「玉山主峰單攻 2D1N」），點選直接跳到 Flow 1 第 6 步（路徑、切點預填）。

### Flow 3 — 手動改寫切點

行程預覽面板的切點清單可點「換切點」→ 選該日內任一節點 → tripType 與裝備清單自動連動。

### Flow 4 — 裝備清單跨行程繼承

進入 `/gear/{planId}`：依 tripType 抓對應分類預設項 → 撈 customItems 命中項 → 撈上次同類型 plan 的勾選狀態（已勾顯示淺灰底色 +「上次有勾」標籤） → 使用者勾 / 取消 / 加自訂 → 即時寫 IndexedDB。

### Flow 5 — 離線下載這條路線（PWA）

`/schedule` 右上 [📥 下載離線包]：算 GPX bounding box + buffer，迴圈下載魯地圖 zoom 13~16 tile 到 `tileCache`，記 `expiresAt = now + 7 days`，進度條呈現。完成後 `/plans` 列表顯示 ✅ 離線可用。

### Flow 6 — 列印

`/schedule` 右上 [🖨 列印] → `window.print()` + `@media print` stylesheet：預設印 V2 表格，隱藏地圖、操作面板，加 footer（列印日期、上河版本、倍率），底部留紙本裝備勾選區。

## 9. 演算法重點

### BFS 路徑解析

百岳節點圖規模小（單條 30~100 節點），BFS 找最短節點數路徑足夠。`viaNodeIds` 用分段 BFS 串接後去重接點。

### DayBreaker

```
累加 adjustedMinutes
當累計 > maxDailyHours * 60：
  回退找前面 60 分鐘內最近的山屋 → 切為 hut break
  找不到 → 切在當前節點，type=camp，警告無山屋
重置該日累計繼續
```

### Naismith 公式（自訂中繼點 fallback）

```
時間(min) = (距離_km / 速度_km每h) * 60 + 上升_m / 上升速率_m每min
預設：平地速度 4 km/h、上升速率 10 m/min
```

供未來擴充自訂中繼點用。MVP 階段用不到（B2 只能點上河節點）。

## 10. 邊界情況與錯誤處理

| 情況 | 對策 |
|---|---|
| 兩節點不連通 | `PathResolver` 回 `warnings: ['no_path']`，UI 顯示「資料缺失」 |
| via 順序衝突 | BFS 失敗時嘗試 via 排列；仍失敗則 warning |
| 倍率拉長後無山屋可切 | DayBreaker 切 camp 節點，UI 警告「需自備帳篷」，自動切 tripType |
| GPX 不在路線範圍 | 警告「GPX 不在範圍」，仍允許但不參與 snap |
| IndexedDB 寫入失敗（隱私模式） | fallback sessionStorage，提示「不持久」 |
| 離線下載超 storage estimate 80% | 中止，提示「儲存空間不足」 |
| 上河資料版本更新 | route.json 帶 version；plan 記錄當時版本 |
| 刪除 plan 連帶 GearChecklist | Dexie hook on `plans.delete` cascade 清理 |
| Service Worker 更新 | vite-plugin-pwa autoUpdate + 提示重新載入 |
| Safari 7 天 IndexedDB eviction | `navigator.storage.persist()`，拒絕則 banner 提示備份 |
| 列印長行程跨頁 | `@media print` `page-break-inside: avoid` + 重複表頭 |

### Build-time 驗證

`scripts/validate-routes.ts`：
- edges 引用的 node 都在 nodes 列表
- 每個 node 有 lat/lng（GPS tagging 完成）
- huts.json 與 route.json 山屋互相對應
- presets 引用節點存在
- 連通性檢查（找不出孤立節點群）

驗證失敗 → build 失敗。

## 11. 測試策略

### 單元測試（Vitest）— 服務層 90%+ coverage

```
PathResolver.test.ts        # BFS、viaNodeIds、O型回程、不連通
TimeCalculator.test.ts      # 去/返程方向、倍率、跨日邊界
DayBreaker.test.ts          # 8h/12h/16h、無山屋切 camp
GearSuggester.test.ts       # tripType 判定、跨行程繼承、union
```

### 元件測試（Vitest + Vue Test Utils）

```
GanttView.test.ts           # 給定 segments 渲染正確 bar
GearChecklist.test.ts       # 勾選 / 新增 / 刪除即時更新
PaceSlider.test.ts          # value 變動 emit
```

### E2E 測試（Playwright）

```
e2e/create-plan.spec.ts     # Flow 1 全跑
e2e/edit-day-break.spec.ts  # Flow 3
e2e/gear-checklist.spec.ts  # Flow 4
e2e/print-schedule.spec.ts  # 列印 PDF 比對
e2e/offline-mode.spec.ts    # SW + IndexedDB 離線
```

### 瀏覽器相容性

- 桌面：Chrome / Edge / Firefox / Safari 最新兩版（macOS 為主）
- 手機：iOS Safari 16+、Android Chrome 最新版（PWA 安裝）
- 不支援 IE

## 12. 一次性資料整理工作

| 工作 | 工時估計 | 備註 |
|---|---|---|
| A. 路線 JSON（節點 + 邊 + 時間） | 30-60h | 20 條 × 1.5-3h |
| B. GPS Tagging（節點 ↔ GPX） | 20-40h | 20 條 × 1-2h |
| C. 山屋資料庫 | 6-8h | 政府開放平台半自動 |
| D. 裝備預設清單 | 6-8h | 健行筆記等抄改 |
| Dev 整理工具開發 | 8-16h | 但能省 30% A+B |
| **資料整理小計** | **70-130h** | 約 2-4 週兼職 |
| 前端 App 開發 | 80-120h | 估計值 |
| **總計** | **150-250h** | |

### 資料整理流程建議

1. 寫 dev 工具 `/dev/route-editor`（左上傳上河圖、右編輯 JSON）
2. 寫 dev 工具 `/dev/gps-tagger`（左 Leaflet + GPX、右節點清單）
3. 先做 G02（玉山）一條 + 完整跑通整個 App 流程，schema 鎖定後再批次擴展剩餘 19 條

## 13. 安全 / 隱私

- 全部資料 local-only，無後端、無 telemetry
- IndexedDB 不存個資
- 列印 footer 標註資料來源以尊重原作者

## 14. 階段性交付建議

> **時間說明**：以下 Phase 工期為「前端 App 開發」週數，假設專注全職投入。資料整理工作（70-130h）與 App 開發**可平行進行**——例如 Phase 1 期間先把 G02 整理完（約 3-5h），Phase 4 才批量整理剩餘 17 條。

**Phase 1（MVP）— 約 4 週**
- 服務層全套 + 測試
- 基本 UI（Routes / Map / Schedule V2 表格 / Gear）
- 1 條路線完整資料（G02 玉山）
- localStorage 持久化（先不做 PWA）

**Phase 2 — 約 2 週**
- V1 Gantt + V3 海拔曲線
- DayBreaker 自動建議 + 改寫 UI
- Cross-trip 裝備繼承
- 加 G05 雪山西稜資料

**Phase 3 — 約 2 週**
- PWA + Service Worker + tile 快取
- 列印 stylesheet
- 加 G09 合歡奇萊資料

**Phase 4（資料擴展）— 約 4-6 週**
- 批次補完剩餘 17 條路線資料
- 整理時遇到的 schema 微調

**Phase 5（未來）**
- GPS 即時定位、軌跡比對
- 自訂中繼點 + Naismith
- 縱走多端點（A 點上、B 點下）

## 15. 待議 / 未來再討論

- 是否做手機原生 App（React Native / Capacitor）?
- 是否加「使用者上傳自己的 GPX」覆蓋預設?
- 是否做行程匯出 / 匯入 JSON（備份用）?
- 是否做緊急聯絡卡（行程備案、緊急聯絡人）?

---

## 附錄 A：上河資料來源

- 入口頁：`https://www.sunriver.com.tw/step2020.htm`
- 節點圖：`images/hiking/G{NN}_hiking.jpg`、`G07_hiking_new.jpg`、`G09_hiking_new.jpg`（更新版）
- 高差圖：`images/hiking/xG{NN}-{N}.jpg`

20 條路線清單：

| ID | 名稱 |
|---|---|
| G01 | 高山百岳地形全圖 |
| G02 | 玉山群峰縱走 |
| G03 | 郡大山‧西巒大山 |
| G04 | 聖稜 Y 型縱走 |
| G05 | 雪山西‧南稜縱走 |
| G06 | 白姑大山單登 |
| G07 | 北一段縱走（已更新） |
| G08 | 北二段縱走 |
| G09 | 合歡‧奇萊縱走（已更新） |
| G10 | 太魯閣山列 |
| G11 | 能高越嶺 |
| G12 | 能高安東軍縱走 |
| G13 | 干卓萬群峰縱走 |
| G14 | 七彩湖‧六順山 |
| G15 | 丹大‧東郡橫斷縱走 |
| G16 | 馬博拉斯橫斷縱走 |
| G17 | 南二段縱走 |
| G18 | 新康橫斷縱走 |
| G19 | 南一段縱走 |
| G20 | 北大武山登峰 |
