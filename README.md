# 台灣百岳登山規劃 App

個人登山行程規劃工具：依上河圖步程資料自動解析路徑、套用倍率估算時間、自動建議多日切點、產生可視化行程表，並依行程類型推薦對應裝備清單。

## 資料來源與版權

本 App 內建的步程節點與時間數據參考自：

> **上河文化《2020 高山百岳地形圖》**
> https://www.sunriver.com.tw/step2020.htm

數據著作權歸**上河文化**所有。本專案為個人學習與規劃用途，僅作為參考工具，不對外提供商業服務。如欲取得完整、最新的步程資料，請支持原版地形圖。

### GPS 座標資料

地圖節點 GPS 座標資料衍生自 OpenStreetMap：

> © OpenStreetMap contributors, licensed under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/)

OSM POI 資料透過 `scripts/fetch-osm-route.ts` 從 Overpass API 抓取，快取於 `public/data/osm-pois/`。

## 技術棧

- **Frontend**: Vue 3 + TypeScript + Vite 5 + Composition API
- **State**: Pinia
- **Routing**: Vue Router
- **UI**: Naive UI + Tailwind CSS
- **Map**: Leaflet 1.9 + leaflet-gpx (NLSC PHOTO_MIX / EMAP5 / OSM)
- **Geo**: @turf/turf
- **Storage**: IndexedDB via Dexie.js
- **Tests**: Vitest (unit) + Playwright (E2E)

## 主要功能

- **行程規劃**：地圖點選起終點 → BFS 路徑解析 → 倍率時間估算
- **多日切點**：依山屋資料庫自動建議過夜點，可手動改寫
- **行程表呈現**：V2 表格時刻表（V1 Gantt / V3 海拔曲線於後續 phase 加入）
- **裝備清單**：依行程類型自動分類，互動勾選，跨行程繼承
- **PWA 離線**（Phase 3）：地圖磚與行程資料離線可用

## 開發

```bash
npm install
npm run dev          # http://localhost:5173
npm run test:run     # 單元測試
npm run test:e2e     # E2E 測試
npm run typecheck
npm run build
```

## 路線資料

目前內建：

| ID | 名稱 | 狀態 |
|---|---|---|
| G02 | 玉山主峰單攻 | ✅ 樣本（8 節點） |
| G01, G03–G20 | 其他百岳路線 | ⏳ Phase 4 整理 |

GPX 檔案來源：個人從健行筆記 / 政府開放資料平台等收集。

## 文件

- `docs/superpowers/specs/2026-05-09-hiking-planning-design.md` — 整體設計文件
- `docs/superpowers/plans/2026-05-09-phase1-mvp.md` — Phase 1 實作計畫

## License

MIT (程式碼)。內建上河步程數據與 GPX 軌跡資料**不適用** MIT，依原始來源各自的版權條款處理。

## Dev 工具

### `/dev/route-editor`

僅在 `npm run dev` 模式可用的路線編輯器。三欄式介面整合上河圖、節點/邊編輯、Leaflet 地圖。

```
http://localhost:5173/dev/route-editor?route=G05
```

工作流程：
1. `npx tsx scripts/fetch-osm-route.ts --relation-id <OSM ID> --output-id G05`
2. 開啟編輯器，看上河圖、自動匹配 OSM POI、補節點/邊
3. 確認雙來源時間後勾選 ✓
4. 「下載 JSON」→ 移到 `public/data/routes/G05.json`
5. `npx tsx scripts/validate-routes.ts --route G05`

### `scripts/fetch-osm-route.ts`

從 OpenStreetMap Overpass API 抓 hiking route relation，輸出 `gpx/G{NN}.gpx` 與 `osm-pois/G{NN}.json`。

```bash
# 單條
npx tsx scripts/fetch-osm-route.ts --relation-id 13678202 --output-id G02

# 批次（manifest 中 status=pending 的全部）
npx tsx scripts/fetch-osm-route.ts --batch
```

### `scripts/validate-routes.ts`

`prebuild` 自動跑。手動驗證：

```bash
npx tsx scripts/validate-routes.ts --route G02
npx tsx scripts/validate-routes.ts --all
```
