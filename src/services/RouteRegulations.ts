/**
 * Per-route regulatory metadata: which permits/applications/hut bookings each route needs.
 *
 * Source: 台灣百岳路線官方申請規範（依各國家公園、林務局、警政署規定）。
 * 已驗證: 2026-05 各 NP 入園系統。
 */

export type RegulatoryAuthority =
  | 'yushan_np'        // 玉山國家公園
  | 'sheipa_np'        // 雪霸國家公園
  | 'taroko_np'        // 太魯閣國家公園
  | 'forestry_bureau'  // 林務局（林道、古道、保留區）
  | 'multiple';        // 跨多個管轄

export interface HutBooking {
  /** Hut name as displayed to user. */
  name: string;
  /** Why booking is needed: 'lottery' = 抽籤, 'first_come' = 預約即可, 'optional' = 可營地替代. */
  bookingType: 'lottery' | 'first_come' | 'optional';
}

export interface RouteRegulation {
  routeId: string;
  /** Primary authority managing the area. */
  authority: RegulatoryAuthority;
  /** 入山證 — issued by 警政署. Required for 山地管制區. */
  enterMountainPermit: boolean;
  /** 入園證 — issued by NP. */
  enterParkPermit: boolean;
  /** Application URL for park permit. */
  parkApplicationUrl?: string;
  /** Huts that require booking/lottery on this route. */
  hutBookings: HutBooking[];
  /** Notes for users (e.g. 原住民部落協議, 季節限制). */
  notes?: string;
}

const PARK_NAMES: Record<RegulatoryAuthority, string> = {
  yushan_np: '玉山國家公園',
  sheipa_np: '雪霸國家公園',
  taroko_np: '太魯閣國家公園',
  forestry_bureau: '林務局',
  multiple: '多個管轄機關',
};

/**
 * Stable landing pages (avoid deep links with internal GUIDs that may rotate).
 * Verified working as of 2026-05.
 */
const URLS = {
  // 內政部警政署 — 入山案件申辦系統
  mountain_permit: 'https://nv2.npa.gov.tw/',
  // 台灣國家公園 — 線上申請入園系統 (主入口，所有 NP 共用)
  np_application: 'https://npm.cpami.gov.tw/',
  // 個別 NP 官網（含入園資訊、最新公告）
  yushan_np: 'https://www.ysnp.gov.tw/',
  sheipa_np: 'https://www.spnp.gov.tw/',
  taroko_np: 'https://www.taroko.gov.tw/',
  // 林務局 (現為農業部林業及自然保育署)
  forestry: 'https://recreation.forest.gov.tw/',
  forestry_conservation: 'https://conservation.forest.gov.tw/',
  // 中央氣象署 山域天氣預報
  cwa_weather: 'https://www.cwa.gov.tw/V8/C/M/index.html',
};

const ROUTE_REGULATIONS: Record<string, RouteRegulation> = {
  G02: {
    routeId: 'G02', authority: 'yushan_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '排雲山莊', bookingType: 'lottery' },
      { name: '圓峰山屋', bookingType: 'lottery' },
    ],
    notes: '排雲山莊每年抽籤搶手，建議提早 1 個月以上申請。',
  },
  G03: {
    routeId: 'G03', authority: 'forestry_bureau',
    enterMountainPermit: true, enterParkPermit: false,
    parkApplicationUrl: URLS.forestry,
    hutBookings: [],
    notes: '郡大林道車輛通行需事先確認林道狀況。',
  },
  G04: {
    routeId: 'G04', authority: 'sheipa_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '九九山莊', bookingType: 'lottery' },
      { name: '七卡山莊', bookingType: 'first_come' },
      { name: '三六九山莊', bookingType: 'lottery' },
      { name: '雪北山屋', bookingType: 'first_come' },
      { name: '翠池山屋', bookingType: 'first_come' },
      { name: '桃山山屋', bookingType: 'first_come' },
      { name: '新達山屋', bookingType: 'first_come' },
    ],
    notes: '雪霸路線多個山屋需各別申請；九九/三六九熱門。',
  },
  G05: {
    routeId: 'G05', authority: 'sheipa_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '七卡山莊', bookingType: 'first_come' },
      { name: '三六九山莊', bookingType: 'lottery' },
      { name: '翠池山屋', bookingType: 'first_come' },
    ],
  },
  G06: {
    routeId: 'G06', authority: 'forestry_bureau',
    enterMountainPermit: true, enterParkPermit: false,
    parkApplicationUrl: URLS.forestry,
    hutBookings: [],
    notes: '紅香溫泉到登山口為原住民部落產業道路，請尊重在地居民。',
  },
  G07: {
    routeId: 'G07', authority: 'taroko_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '新雲稜山莊', bookingType: 'first_come' },
      { name: '審馬陣山莊', bookingType: 'first_come' },
      { name: '南湖圈谷山莊', bookingType: 'first_come' },
    ],
    notes: '北一段為長程縱走，建議分段申請並注意鋸山稜線天氣。',
  },
  G08: {
    routeId: 'G08', authority: 'taroko_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [],
    notes: '畢祿羊頭連峰中橫進出，林道路況須確認。',
  },
  G09: {
    routeId: 'G09', authority: 'taroko_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '成功山屋', bookingType: 'first_come' },
      { name: '奇萊山莊', bookingType: 'first_come' },
      { name: '天池山莊', bookingType: 'lottery' },
    ],
    notes: '天池山莊（能高越嶺道）住宿熱門需抽籤；屏風山路徑須特別小心。',
  },
  G10: {
    routeId: 'G10', authority: 'taroko_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [],
    notes: '太魯閣山列為長程連峰縱走，無山屋僅營地。',
  },
  G11: {
    routeId: 'G11', authority: 'forestry_bureau',
    enterMountainPermit: true, enterParkPermit: false,
    parkApplicationUrl: URLS.forestry,
    hutBookings: [
      { name: '天池山莊', bookingType: 'lottery' },
      { name: '雲海保線所', bookingType: 'optional' },
      { name: '檜林保線所', bookingType: 'optional' },
      { name: '奇萊保線所', bookingType: 'optional' },
    ],
    notes: '能高越嶺道屬林務局管轄；天池山莊抽籤需提早申請。',
  },
  G12: {
    routeId: 'G12', authority: 'multiple',
    enterMountainPermit: true, enterParkPermit: false,
    parkApplicationUrl: URLS.forestry,
    hutBookings: [
      { name: '天池山莊', bookingType: 'lottery' },
    ],
    notes: '能高安東軍縱走南段為林務局管轄；安東軍山屋已撤除，需露宿。',
  },
  G13: {
    routeId: 'G13', authority: 'forestry_bureau',
    enterMountainPermit: true, enterParkPermit: false,
    parkApplicationUrl: URLS.forestry,
    hutBookings: [],
    notes: '干卓萬群峰縱走起訖點為原住民部落，需事先協調並支付部落入山費用。',
  },
  G14: {
    routeId: 'G14', authority: 'forestry_bureau',
    enterMountainPermit: true, enterParkPermit: false,
    parkApplicationUrl: URLS.forestry,
    hutBookings: [],
    notes: '萬榮林道路況變化大，出發前須確認；七彩湖路徑無山屋。',
  },
  G15: {
    routeId: 'G15', authority: 'forestry_bureau',
    enterMountainPermit: true, enterParkPermit: false,
    parkApplicationUrl: URLS.forestry,
    hutBookings: [
      { name: '丹大山屋', bookingType: 'first_come' },
    ],
    notes: '丹大東郡橫斷為長程縱走，需自備帳篷；林道車輛通行管制嚴格。',
  },
  G16: {
    routeId: 'G16', authority: 'yushan_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '樂樂山屋', bookingType: 'lottery' },
      { name: '觀高登山服務站', bookingType: 'first_come' },
      { name: '中央金礦山屋', bookingType: 'lottery' },
      { name: '白洋金礦山屋', bookingType: 'lottery' },
      { name: '秀姑巒山屋', bookingType: 'lottery' },
      { name: '馬博拉斯山屋', bookingType: 'first_come' },
    ],
    notes: '馬博橫斷為八通關古道延伸；山屋多需排雲管理處抽籤。',
  },
  G17: {
    routeId: 'G17', authority: 'yushan_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '向陽山屋', bookingType: 'lottery' },
      { name: '嘉明湖避難山屋', bookingType: 'lottery' },
      { name: '拉庫音溪山屋', bookingType: 'first_come' },
      { name: '塔芬谷山屋', bookingType: 'first_come' },
      { name: '大水窟山屋', bookingType: 'first_come' },
    ],
    notes: '向陽山屋與嘉明湖避難山屋每年抽籤搶手；南二段全程需 7 天以上。',
  },
  G18: {
    routeId: 'G18', authority: 'yushan_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '向陽山屋', bookingType: 'lottery' },
      { name: '嘉明湖避難山屋', bookingType: 'lottery' },
      { name: '抱崖山屋', bookingType: 'first_come' },
      { name: '瓦拉米山屋', bookingType: 'first_come' },
    ],
    notes: '新康橫斷由南橫向陽進入，瓦拉米端出，需安排兩端接駁。',
  },
  G19: {
    routeId: 'G19', authority: 'yushan_np',
    enterMountainPermit: true, enterParkPermit: true,
    parkApplicationUrl: URLS.np_application,
    hutBookings: [
      { name: '埡口山莊', bookingType: 'first_come' },
      { name: '庫哈諾辛山屋', bookingType: 'first_come' },
      { name: '3026山屋', bookingType: 'first_come' },
    ],
    notes: '南一段為超長縱走（通常 7 天以上），多段無山屋需露營，水源規劃尤其重要。',
  },
  G20: {
    routeId: 'G20', authority: 'forestry_bureau',
    enterMountainPermit: true, enterParkPermit: false,
    parkApplicationUrl: URLS.forestry,
    hutBookings: [
      { name: '檜谷山莊', bookingType: 'lottery' },
    ],
    notes: '北大武山檜谷山莊熱門，需抽籤；林務局屏東分署管轄。',
  },
};

export function getRegulation(routeId: string): RouteRegulation | null {
  return ROUTE_REGULATIONS[routeId] ?? null;
}

export function getAuthorityName(authority: RegulatoryAuthority): string {
  return PARK_NAMES[authority];
}

/**
 * Return the official info/announcement website for the authority
 * (closure notices, weather warnings, hut status). Distinct from the
 * shared `npm.cpami.gov.tw` apply portal.
 */
export function getParkInfoUrl(authority: RegulatoryAuthority): string {
  switch (authority) {
    case 'yushan_np': return URLS.yushan_np;
    case 'sheipa_np': return URLS.sheipa_np;
    case 'taroko_np': return URLS.taroko_np;
    case 'forestry_bureau':
    case 'multiple':
    default:
      return URLS.forestry;
  }
}

export const COMMON_URLS = URLS;
