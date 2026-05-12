# Phase 4 設計文件 — 資料擴展（20 條 G 系列）+ Dev 工具

- 日期：2026-05-13
- 作者：Peter Lu
- 狀態：Draft（待 brainstorming 階段最終確認）
- 前置：Phase 2.5 已 merge 到 release（commit f3b1546）

## 1. 目標與範圍

把 routes 從 Phase 1 樣本（僅 G02 一條 8 節點粗略樣本）擴展到完整 20 條 G 系列百岳路線，含準確 GPS 座標。同時建立 dev 工具讓未來新增/維護資料可重複使用。

### 在範圍內

- **OSM 整合**：自動抓取 OpenStreetMap Overpass API 取得 GPS 軌跡 + named POIs
- **`scripts/fetch-osm-route.ts`**：給 OSM relation ID，輸出 `gpx/G{NN}.gpx` + `osm-pois/G{NN}.json`
- **`scripts/validate-routes.ts`**：build-time 驗證 13 個 rules，error 擋 build
- **`OsmPoiMatcher` service**：Levenshtein 字串相似度 + 正規化匹配上河節點 ↔ OSM POI
- **`RouteValidator` service**：純函式驗證 13 個 rules
- **`/dev/route-editor`**：dev mode 三欄編輯器（上河圖 / 節點+邊清單 / 地圖+OSM）
- **上河時間準確性機制**：每個 edge 強制兩來源（`G{NN}_hiking.jpg` + `xG{NN}-N.jpg`）交叉驗證，confirmed=true 才能 export
- **20 條路線資料整理**：實際 fetch + 編輯，產出 `public/data/routes/G{01..20}.json`（不在 plan 範圍，是後續手動工作）
- **routesStore 改吃 manifest**：載所有 status=done 的路線
- **README 補 OSM attribution**（ODbL）

### 不在範圍內

- 多語言 UI（i.e. dev 工具中文 only）
- OSM relation 自動搜尋（需要人工查 ID 填 manifest）
- 路線資料即時同步上河（一次性 snapshot）
- routes 跨路線共用節點（每條獨立、prefix 區隔）
- E2E for dev tools（不必要）

## 2. 主要決策摘要

| 面向 | 決定 |
|---|---|
| 範圍 | A+D（20 條全做 + dev 工具） |
| GPS 來源 | OpenStreetMap Overpass API（ODbL，需 attribution） |
| 上河資料 | 我 Read 看 `sunriver.com.tw/images/hiking/G{NN}_hiking.jpg` 系列 |
| OSM POI 匹配 | 自動（Levenshtein 相似度 ≥ 0.5）+ 手動覆蓋 |
| 上河時間驗證 | 兩來源（拓撲圖 + 高差圖）交叉，不一致強制人工確認 |
| 儲存 | 瀏覽器下載 JSON → 我手動 git commit（不需要 dev 後端 endpoint） |
| 共用節點 | 每路線獨立 prefix（n_g02_xxx vs n_g05_xxx） |
| Dev 工具部署 | dev mode only，build 時 tree-shake |
| 驗證 | `prebuild` 自動跑 validate，error 擋 build |

## 3. 整體架構

```
工作流 A（一次性資料準備，每條 G{NN}）
=============================================
1. 我查 OSM 找對應 hiking route relation ID
   ↓
2. scripts/fetch-osm-route.ts <relation-id> <output-id>
   ├─ public/data/gpx/G{NN}.gpx           (路徑幾何)
   └─ public/data/osm-pois/G{NN}.json     (named POIs)
   ↓
3. 我 Read sunriver.com.tw/images/hiking/G{NN}_hiking.jpg
4. 我 Read sunriver.com.tw/images/hiking/xG{NN}-N.jpg
   ↓
5. /dev/route-editor?route=G{NN} 開瀏覽器編輯
   ├─ 左：上河圖 + xG{NN} 高差圖 tab 切換
   ├─ 中：節點/邊 清單 + 編輯
   └─ 右：Leaflet + GPX + OSM POI pin
   ↓
6. 瀏覽器下載 G{NN}.json → 我手動移到 public/data/routes/
   ↓
7. scripts/validate-routes.ts --route G{NN}
   ↓
8. git commit "feat(data): add G{NN} route data"

工作流 B（App runtime）
=============================================
routesStore.loadAll()
  ↓ 載 public/data/routes-manifest.json
  ↓ 並行載所有 manifest.routes 中 status=done 的 G{NN}.json
RoutesListView 顯示全部已完成的路線
```

### 新增檔案

```
scripts/
+ fetch-osm-route.ts             # 抓 OSM relation → GPX + POIs JSON
+ validate-routes.ts             # build-time validation runner

public/data/
+ routes-manifest.json           # 20 條路線 metadata 索引
+ osm-pois/G{NN}.json × 20       # OSM POI 快取（commit 進 repo）
+ routes/G{NN}.json × 20         # 整理後的最終資料
+ gpx/G{NN}.gpx × 20             # OSM 路徑

src/views/dev/
+ RouteEditorView.vue            # /dev/route-editor 主編輯器
+ RouteEditorImageView.vue       # 左欄上河圖
+ RouteEditorSidebar.vue         # 中欄節點/邊清單與編輯
+ RouteEditorMatcher.vue         # OSM POI ↔ 上河節點匹配
+ RouteEditorMap.vue             # 右欄 Leaflet + GPX + 點選

src/services/
+ OsmPoiMatcher.ts               # 字串相似度匹配（純函式）
+ RouteValidator.ts              # 13 個驗證 rules（純函式）

src/types/
+ osm.ts                         # OsmNode, OsmWay, OsmPoi, OsmCategory
+ validation.ts                  # ValidationIssue
```

### 修改檔案

```
~ src/stores/routesStore.ts                 # loadAll 改吃 manifest
~ src/router/index.ts                       # 加 /dev/route-editor（dev mode only）
~ public/data/routes/G02-sample.json        # 重命名為 G02.json + 補完
~ public/data/gpx/G02-sample.gpx            # 重命名為 G02.gpx（OSM fetch 覆寫）
~ src/views/MapPlannerView.vue              # GPX URL 改 `/data/gpx/{route.id}.gpx`
~ README.md                                  # 加 OSM attribution + dev 工具說明
~ package.json                               # prebuild script + tsx devDep
```

### 設計原則

- **Dev 工具與 production 分離**：`/dev/*` routes 在 `src/router` 用 `import.meta.env.DEV` 條件導入
- **OSM 資料 commit 進 repo**：runtime 不 fetch OSM，避免依賴外部服務 + 加快載入
- **上河時間是第一優先**：UI 強制兩來源驗證，不能跳過
- **每路線獨立**：prefix node id，不跨路線參照，避免耦合

## 4. 技術棧增量

```
新增 dev 依賴：
  tsx                              # 跑 TypeScript script
  fast-levenshtein 或 string-similarity  # 字串相似度

零新 runtime 依賴。
```

## 5. 資料模型

### 5.1 `public/data/routes-manifest.json`

```jsonc
{
  "version": "2026-05-13",
  "attribution": "GPS coordinates © OpenStreetMap contributors (ODbL)",
  "routes": [
    {
      "id": "G01",
      "name": "高山百岳地形全圖",
      "osmRelationId": null,
      "sunriverImage": "G01_hiking.jpg",
      "elevationImages": [],
      "status": "skipped"
    },
    {
      "id": "G02",
      "name": "玉山群峰縱走",
      "osmRelationId": 13678202,
      "sunriverImage": "G02_hiking.jpg",
      "elevationImages": ["xG02-1.jpg", "xG02-2.jpg", "xG02-3.jpg"],
      "status": "pending",
      "fetchedAt": null
    }
  ]
}
```

`status` 可為 `pending | in_progress | done | skipped | failed`。

### 5.2 `public/data/osm-pois/G{NN}.json`

```jsonc
{
  "sourceRelation": 13678202,
  "fetchedAt": "2026-05-13T10:00:00Z",
  "pois": [
    {
      "id": "osm_node_12345678",
      "name": "玉山塔塔加鞍部登山口",
      "lat": 23.4757522,
      "lon": 120.8999713,
      "elevation": 2610,
      "tags": {
        "category": "trailhead",
        "raw": { "highway": "trailhead", "name": "..." }
      }
    }
  ]
}
```

### 5.3 `public/data/routes/G{NN}.json`

沿用 Phase 1 schema（Route type），但 edge 加 `sources` 與 `confirmed` 欄位：

```jsonc
{
  "id": "G02",
  "name": "玉山群峰縱走",
  "version": "2026-osm-2",
  "source": "上河文化《2020高山百岳地形圖》+ © OpenStreetMap contributors",
  "nodes": [...],
  "edges": [
    {
      "from": "n_g02_tataka",
      "to": "n_g02_shang_dongpu",
      "minutes_forward": 10,
      "minutes_backward": 10,
      "sources": [
        { "file": "G02_hiking.jpg",  "minutes_forward": 10, "minutes_backward": 10, "notedBy": "ai" },
        { "file": "xG02-2.jpg",      "minutes_forward": 10, "minutes_backward": 10, "notedBy": "ai" }
      ],
      "confirmed": true
    }
  ],
  "presets": [...]
}
```

`sources` 與 `confirmed` 是 Phase 4 新欄位。Phase 1+2 元件不用到，會被 ignore。

### 5.4 `src/types/osm.ts`

```ts
export type OsmCategory = 'trailhead' | 'hut' | 'peak' | 'junction' | 'water' | 'waypoint' | 'shelter';

export interface OsmPoi {
  id: string;
  name: string;
  lat: number;
  lon: number;
  elevation: number | null;
  tags: {
    category: OsmCategory;
    raw: Record<string, string>;
  };
}

export interface OsmPoisFile {
  sourceRelation: number;
  fetchedAt: string;
  pois: OsmPoi[];
}
```

### 5.5 `src/types/validation.ts`

```ts
export type ValidationSeverity = 'error' | 'warning';

export interface ValidationIssue {
  severity: ValidationSeverity;
  route: string;
  type: string;
  message: string;
  ref?: string;
}

export interface ValidationReport {
  errors: number;
  warnings: number;
  issues: ValidationIssue[];
}
```

## 6. Scripts

### 6.1 `scripts/fetch-osm-route.ts`

CLI：

```bash
npx tsx scripts/fetch-osm-route.ts --relation-id 13678202 --output-id G02
npx tsx scripts/fetch-osm-route.ts --batch
```

#### 演算法
1. POST Overpass API：`[out:json][timeout:60];relation({id});(._;>>;);out body;`
2. 收到 elements 後 index 為 nodes/ways/relation
3. 依 relation members 順序組裝 GPX trkseg（一個 way 一個 trkseg）
4. 篩 `tags.name` 不空的 node → POI；用 tag heuristic 推斷 category
5. 寫檔：`public/data/gpx/{outputId}.gpx`、`public/data/osm-pois/{outputId}.json`

#### Batch 模式
- 讀 manifest，對 `status === 'pending'` 且 `osmRelationId !== null` 的條目依序 fetch
- 每條間 sleep 5s（友善公開 Overpass）
- 進度寫回 manifest（`status: 'done'` + `fetchedAt`）

#### 錯誤處理
| 情況 | 對策 |
|---|---|
| 429 rate limited | sleep 30s 重試 1 次 |
| 5xx | sleep 60s 重試 1 次 |
| Timeout | log warning，manifest 標 failed，繼續 |
| Relation 不存在 | log error，status=failed |
| 多於 3000 nodes（極大 relation） | 完整輸出但 log warning |

### 6.2 `scripts/validate-routes.ts`

CLI：

```bash
npx tsx scripts/validate-routes.ts --route G05
npx tsx scripts/validate-routes.ts --all
```

#### 整合
```json
// package.json
"scripts": {
  "prebuild": "tsx scripts/validate-routes.ts --all",
  ...
}
```

#### 13 個 Rules

```ts
const RULES = [
  // 結構性 (error)
  rule_all_edges_reference_existing_nodes,
  rule_all_presets_reference_existing_nodes,
  rule_no_self_loop_edges,
  rule_huts_cross_reference,           // node.hutId 在 huts.json 存在
  rule_all_nodes_have_lat_lng,
  rule_edge_times_positive,
  
  // 一致性 (error)
  rule_node_ids_unique,
  rule_edge_confirmed,                  // 所有 edge confirmed=true
  
  // 連通性
  rule_all_preset_paths_resolvable,    // error
  rule_graph_connected,                 // warning
  
  // 合理性 (warning)
  rule_edge_time_reasonable,            // speed 範圍 0.1-10 km/h
  rule_elevation_present,
  rule_categories_used,                 // 至少 1 trailhead + 1 peak
];
```

#### 輸出格式

```
G05 (雪山西‧南稜縱走)
================================
✓ 28 edges OK
⚠ 2 warnings:
  - unreasonable_speed: n_g05_xueshanwest → n_g05_xueshansouth: 30min for 4.20km (8.4km/h)
  - elevation_present: n_g05_old_camp missing elevation
✗ 1 error:
  - edge_confirmed: 3 edges pending source verification

Exit 1.
```

Error 數 > 0 → exit 1 → 擋 build。可加 `--skip-errors` flag 開發期暫時跳過（不在 prebuild 用）。

## 7. Service 層

### 7.1 `OsmPoiMatcher.ts` API

```ts
import type { OsmPoi } from '@/types';

export interface MatchCandidate {
  poi: OsmPoi;
  similarity: number;
}

export function normalizeName(name: string): string;
export function matchPoisToNode(nodeName: string, pois: OsmPoi[]): MatchCandidate[];
```

#### 正規化
- 全形 → 半形
- 簡繁互轉（簡 → 繁）
- 移除常見後綴：「步道」「山莊」「山屋」「登山口」「岔路口」
- 小寫化拉丁字
- 數字 normalize：「369」≡「三六九」

#### 演算法
```ts
levenshtein_ratio(a: string, b: string): number  // 0-1
matchPoisToNode = (name, pois) => pois
  .map(poi => ({ poi, similarity: levenshtein_ratio(normalize(name), normalize(poi.name)) }))
  .filter(r => r.similarity > 0.5)
  .sort((a,b) => b.similarity - a.similarity);
```

### 7.2 `RouteValidator.ts` API

```ts
import type { Route, Hut, ValidationReport } from '@/types';

export interface ValidateInput {
  route: Route;
  huts: Hut[];
}

export function validateRoute(input: ValidateInput): ValidationReport;
```

純函式，可單元測試每個 rule。

## 8. Dev UI 元件

### 8.1 `RouteEditorView.vue`

主框架，URL：`/dev/route-editor?route=G05`

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router';
const route = useRoute();
const routeId = computed(() => route.query.route as string);
// 載入：manifest → osm-pois/{id}.json → gpx/{id}.gpx → (if exists) routes/{id}.json
// 載入上河圖 URLs
</script>

<template>
  <div class="grid grid-cols-[400px_400px_1fr] h-screen">
    <RouteEditorImageView :sunriver-image="..." :elevation-images="..." />
    <RouteEditorSidebar :nodes="..." :edges="..." @save="downloadJson" />
    <RouteEditorMap :gpx-url="..." :pois="..." :nodes="..." />
  </div>
</template>
```

### 8.2 `RouteEditorImageView.vue`

左欄。Naive UI `NTabs`：
- Tab 1: 上河 `G{NN}_hiking.jpg`（拓撲圖）
- Tab 2-N: `xG{NN}-1.jpg`, `xG{NN}-2.jpg`...（高差圖）

每 tab 顯示對應圖，支援 zoom（CSS transform）、pan（mouse drag）。可釘住某張圖在獨立 popout 窗口（用 `window.open` 開新窗）方便我跨圖比對。

### 8.3 `RouteEditorSidebar.vue`

中欄。兩個 collapse 區塊：
- **節點**：list 每節點 + 編輯表單（name, category, lat, lng, elevation, hutId, tags）
- **邊**：list 每 edge + 「上河時間驗證」UI

Edge 編輯子元件 `EdgeEditor`:

```vue
<template>
  <div>
    <NSelect v-model="from" :options="nodeOptions" />
    <NSelect v-model="to" :options="nodeOptions" />
    
    <div class="sources">
      <SourceEntry v-for="(s, i) in sources" :key="i" :source="s" @update="..." @remove="..." />
      <NButton @click="addSource">+ 來源</NButton>
    </div>
    
    <div class="final-time">
      <label>最終確認：</label>
      <span :class="{ 'text-red-600': inconsistent }">
        去 {{ minutes_forward }} / 返 {{ minutes_backward }}
      </span>
      <NCheckbox v-model="confirmed" :disabled="hasInconsistency">
        ✓ 已確認
      </NCheckbox>
      <div v-if="hasInconsistency" class="text-red-600">
        ⚠ 兩來源不一致，請手動選擇正確值
      </div>
    </div>
  </div>
</template>
```

### 8.4 `RouteEditorMatcher.vue`

子元件嵌在 NodeEditor 內：

```vue
<template>
  <div>
    <NDivider>OSM POI 匹配候選</NDivider>
    <div v-for="c in candidates" :key="c.poi.id" class="candidate">
      <NRadio :checked="selectedPoiId === c.poi.id" @change="select(c.poi)">
        {{ c.poi.name }}
        <NTag size="small">{{ (c.similarity * 100).toFixed(0) }}%</NTag>
        <span class="text-xs">{{ c.poi.lat.toFixed(4) }}, {{ c.poi.lon.toFixed(4) }}</span>
      </NRadio>
    </div>
    <NInput v-model="searchTerm" placeholder="搜尋 OSM POI" />
  </div>
</template>
```

### 8.5 `RouteEditorMap.vue`

右欄。Leaflet 地圖 + GPX 軌跡 + OSM POI 為 pin + 已 tag 節點為彩色 pin（依 category）。功能：
- 點地圖空白處 → emit 「lat/lng selected」，Sidebar 套用到當前編輯節點
- Hover 上 POI / 節點 → 顯示 name + similarity
- Highlight 當前編輯節點

## 9. routesStore 改動

```ts
// 載入流程
async function loadAll() {
  loading.value = true;
  try {
    const manifest: RoutesManifest = await fetchJson('/data/routes-manifest.json');
    const doneRoutes = manifest.routes.filter((r) => r.status === 'done');
    const huts: Hut[] = await fetchJson('/data/huts.json');
    const routePromises = doneRoutes.map((m) =>
      fetchJson<Route>(`/data/routes/${m.id}.json`).catch((e) => {
        console.warn(`Failed to load ${m.id}:`, e);
        return null;
      })
    );
    const loaded = (await Promise.all(routePromises)).filter((r): r is Route => r !== null);
    routes.value = loaded;
    huts.value_ = huts;
  } finally {
    loading.value = false;
  }
}
```

開發階段沒 G{NN}.json 的條目自動跳過。

## 10. 邊界條件

涵蓋於各節 + 第 4 節驗證 rules。額外：

| 情境 | 對策 |
|---|---|
| OSM relation 不存在於台灣某小眾路線 | manifest 標 `osmRelationId: null`，路線仍能編輯（純手動 lat/lng） |
| OSM 軌跡與上河圖路線實際走法略差 | 以上河圖為主，OSM 只用於 GPS。Resolver 走上河 node graph 不走 GPX |
| 大量資料 commit 進 repo | OSM POI JSON ~50KB/route × 20 ~ 1MB，GPX ~200KB/route × 20 ~ 4MB，可接受 |
| 同節點在多條 G 路線都出現（玉山西峰）| 各路線獨立 prefix（`n_g02_xifeng` vs `n_g05_xifeng`） |
| 上河圖節點名含特殊字符（／、＋等）| route-editor 允許但 prefix id 須 sanitize（slug 化） |
| 已編輯到一半但沒存 → 重整 | 自動儲存到 sessionStorage，重整後 prompt「續編」 |
| 雙來源不一致時 confirmed=true 強制要求人工選 | UI 阻擋自動 confirmed，需手動選正確值 + 標記 |
| validator error 在 dev 時擋 build | 加 `--skip-errors` flag 開發期暫繞，CI 不傳 flag |

## 11. 測試策略

### 單元測試

```
scripts/fetch-osm-route.test.ts (mock Overpass)
  - 多 way relation → 多 trkseg GPX
  - POI tag 推斷正確（alpine_hut, natural=peak, etc.）
  - 無 name node 不進 POI
  - way 引用不存在 node → warning + skip

services/OsmPoiMatcher.test.ts
  - 完全一致 → 1.0
  - 簡繁差異 → > 0.7
  - 全形半形 → 正規化後一致
  - 後綴「步道」「山莊」剝除
  - 「369」≡「三六九」
  - 無關名稱 → < 0.5

services/RouteValidator.test.ts (13 個 case)
  - 合法 G02 → 0 issue
  - edge 引用不存在 node → 1 error
  - preset 不可達 → 1 error
  - confirmed=false → 1 error
  - 不合理速率 → 1 warning
  - 孤立節點群 → 1 warning
  - hutId 找不到對應 huts.json → 1 error
  - 缺 lat/lng → 1 error
  - 缺 elevation → 1 warning
  - 缺 trailhead/peak → 1 warning
  - self-loop → 1 error
  - 負數時間 → 1 error
  - 重複節點 ID → 1 error
```

### 元件測試

```
components/dev/RouteEditorView.test.ts
  - 渲染三欄
  - 載入完成 → 顯示節點/邊

components/dev/RouteEditorMatcher.test.ts
  - 顯示 sorted candidates
  - 點選 → emit poi-selected

components/dev/RouteEditorMap.test.ts
  - 渲染 GPX 軌跡
  - 點空白處 → emit latlng
```

### 整合測試

```
tests/integration/fetch-osm-fixture.test.ts
  - 用 fixture OSM JSON 跑 fetch-osm-route → 比對輸出 GPX + POI JSON
```

不做 E2E（dev 工具非 production）。

## 12. 階段交付（12 task）

### Step 1 — Scripts + 資料層
- T1 `OsmPoiMatcher.ts` service + 6 個測試
- T2 `RouteValidator.ts` service + 13 個測試
- T3 `scripts/fetch-osm-route.ts` + 測試（mock Overpass）
- T4 `public/data/routes-manifest.json` 初始檔（20 條 entry, osmRelationId 留空）
- T5 `routesStore.loadAll` 改吃 manifest

### Step 2 — Route Editor UI
- T6 `RouteEditorView.vue` 主框架 + 載入流程
- T7 `RouteEditorImageView.vue`（左欄上河圖 zoom/pan + popout）
- T8 `RouteEditorSidebar.vue`（中欄節點/邊清單 + EdgeEditor 含雙來源驗證）
- T9 `RouteEditorMatcher.vue`（POI 候選顯示）
- T10 `RouteEditorMap.vue`（右欄 Leaflet + GPX + POI pin + 點選）

### Step 3 — Integration & Validation
- T11 `/dev/route-editor` route 加入（dev mode only）+ scripts 整合 `prebuild`
- T12 README + huts.json 擴展（依各路線山屋）+ G02-sample → G02 重命名

### 後續手動工作（不在 plan 範圍）
- 我查 OSM relation IDs 填 manifest（約 1-2 小時）
- 我跑 `fetch-osm-route --batch`
- 我看上河圖 + 用 route-editor + 我自己 commit 每條路線（每條 ~30 分鐘 agent，total ~10 小時）

## 13. 風險評估

| 風險 | 機率 | 緩解 |
|---|---|---|
| Overpass API 速率限制 | 中 | 5s 間隔 + 自動 retry + log 失敗條目 |
| OSM 部分路線資料缺漏 | 高 | manifest `osmRelationId: null` 允許手動編輯 lat/lng |
| 上河時間 OCR 錯誤 | 中 | 雙來源強制交叉驗證，confirmed=false 擋 export |
| 我長串轉錄注意力疲乏導致錯誤 | 中 | validator 抓不合理速率/缺欄位 + 你最終人工抽檢 |
| dev 工具未來 maintenance 負擔 | 低 | dev-only，build tree-shake；無 user-facing 影響 |
| 共用節點命名衝突 | 低 | prefix 強制隔離；驗證器抓重複 ID |

## 14. 安全 / 隱私 / 版權

- OSM 資料採 ODbL，需附 attribution（已加在 manifest 與 README）
- 上河資料維持 Phase 1 立場（私人使用 / 不分發）
- Dev 工具僅 dev mode 啟用，production build tree-shake
- OSM POI JSON commit 進 public repo OK（ODbL 允許 + 已 attribute）

## 15. 待議 / 未來

- Phase 5（PWA / 即時 GPS / 自訂中繼點）
- 上河資料定期更新 detector（compare against新版`step2020.htm`）
- Multi-route 共用節點機制（暫不做）
- Dev 工具 i18n（不做）
