/**
 * Pre-trip checklist generator.
 *
 * For a given plan, generates the suggested system items (法規/安全/裝備/外部).
 * Merges with the user's existing items, preserving check state and any user-added items.
 */
import type { Plan, ChecklistItem, PreTripChecklist } from '@/types';
import { getRegulation, getAuthorityName, getParkInfoUrl, COMMON_URLS } from './RouteRegulations';

/** Generate the suggested-by-system items for a plan. */
export function generateSuggestedItems(plan: Plan): ChecklistItem[] {
  const items: ChecklistItem[] = [];
  const reg = getRegulation(plan.routeId);

  // ─── 法規申請 ───
  if (reg?.enterMountainPermit) {
    items.push({
      id: 'legal_mountain_permit',
      category: 'legal',
      title: '入山證（警政署）',
      description: '進入山地管制區須事先申請。建議出發前 5 日完成。',
      externalLink: COMMON_URLS.mountain_permit,
      required: true,
      systemSuggested: true,
    });
  }
  if (reg?.enterParkPermit) {
    items.push({
      id: `legal_park_permit_${reg.authority}`,
      category: 'legal',
      title: `${getAuthorityName(reg.authority)}入園證`,
      description: '線上申請；抽籤路線需提早 1 個月以上。',
      externalLink: reg.parkApplicationUrl,
      required: true,
      systemSuggested: true,
    });
  }
  if (reg?.authority === 'forestry_bureau') {
    items.push({
      id: 'legal_forestry_application',
      category: 'legal',
      title: '林務局申請（古道、林道、保留區）',
      description: '部分路線需林務局或地方林管處許可。',
      externalLink: COMMON_URLS.forestry,
      required: false,
      systemSuggested: true,
    });
  }
  // Hut bookings
  if (reg?.hutBookings && reg.hutBookings.length > 0) {
    for (const hut of reg.hutBookings) {
      const typeLabel = hut.bookingType === 'lottery' ? '抽籤' :
                        hut.bookingType === 'first_come' ? '預約' : '可選'
      items.push({
        id: `legal_hut_${hut.name}`,
        category: 'legal',
        title: `山屋訂位：${hut.name}（${typeLabel}）`,
        description: hut.bookingType === 'lottery'
          ? '熱門山屋，建議出發前 1 個月以上申請。'
          : hut.bookingType === 'first_come'
            ? '需事先預約以保留床位。'
            : '若山屋客滿可改以營地替代。',
        externalLink: reg.parkApplicationUrl,
        required: hut.bookingType !== 'optional',
        systemSuggested: true,
      });
    }
  }

  // ─── 安全 ───
  items.push({
    id: 'safety_custodian',
    category: 'safety',
    title: '行程留守人填寫並通知',
    description: '留守人需知道你的詳細行程、預計回報時間及緊急聯絡方式。',
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'safety_return_time',
    category: 'safety',
    title: '預計回報時間設定',
    description: '逾時未回需啟動搜救程序。',
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'safety_emergency_contacts',
    category: 'safety',
    title: '緊急聯絡人填寫（至少 2 位）',
    description: '家人、隊友、保險公司等。',
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'safety_insurance',
    category: 'safety',
    title: '保險投保（登山綜合險）',
    description: '建議含搜救/直升機後送險，超過 3000m 需注意保單條款。',
    required: false,
    systemSuggested: true,
  });
  items.push({
    id: 'safety_route_briefing',
    category: 'safety',
    title: '隊伍行前說明會',
    description: '討論行程、撤退路線、應變措施、體能準備。',
    required: true,
    systemSuggested: true,
  });

  // ─── 裝備 ───
  items.push({
    id: 'gear_checklist_link',
    category: 'gear',
    title: '完成裝備清單檢查',
    description: '前往裝備清單頁逐項勾選。',
    internalRoute: plan.id ? `/gear/${plan.id}` : undefined,
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'gear_headlamp',
    category: 'gear',
    title: '頭燈 + 備用電池',
    description: '至少 1 顆主燈 + 1 顆備用；電池檢查。',
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'gear_firstaid',
    category: 'gear',
    title: '急救包確認',
    description: '止血、消毒、止痛、抗組織胺、個人用藥。',
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'gear_food_water',
    category: 'gear',
    title: '糧食/水分計算',
    description: '每日約 2500-3500 大卡；山上每人每日 2-3L 水。',
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'gear_communication',
    category: 'gear',
    title: '通訊裝備（手機/PLB/衛星電話）',
    description: 'PLB / Garmin inReach 等衛星通訊強烈建議長程縱走攜帶。',
    required: false,
    systemSuggested: true,
  });
  items.push({
    id: 'gear_navigation',
    category: 'gear',
    title: '地圖 + 指北針 / 已下載 GPX',
    description: '紙本上河圖 + 手機離線地圖，避免單一失效。',
    required: true,
    systemSuggested: true,
  });

  // ─── 外部因素 ───
  items.push({
    id: 'ext_weather',
    category: 'external',
    title: '天氣查詢（出發前 3 日內 + 行程期間）',
    description: '中央氣象局山域天氣、雷雨/颱風預警。',
    externalLink: COMMON_URLS.cwa_weather,
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'ext_hut_phone',
    category: 'external',
    title: '山屋訂位確認電話',
    description: '即使線上申請成功，建議出發前致電山屋確認。',
    required: false,
    systemSuggested: true,
  });
  items.push({
    id: 'ext_transport',
    category: 'external',
    title: '接駁/交通安排',
    description: '尤其縱走路線兩端不同位置，需確認接駁、停車、火車時刻。',
    required: true,
    systemSuggested: true,
  });
  items.push({
    id: 'ext_park_status',
    category: 'external',
    title: '路況/封山公告查詢',
    description: '颱風、地震後常有封山或路徑變更；出發前查詢公告。',
    externalLink: reg ? getParkInfoUrl(reg.authority) : COMMON_URLS.forestry,
    required: true,
    systemSuggested: true,
  });

  return items;
}

/**
 * Merge generated suggestions with user's existing checklist:
 * - System items: replace title/description from latest generation (in case content updated),
 *   but preserve checkedAt state by id.
 * - User-added items (systemSuggested=false): keep as-is.
 * - System items in `existing` that no longer appear in `generated` are dropped.
 */
export function mergeChecklist(
  existing: ChecklistItem[] | undefined,
  generated: ChecklistItem[],
): ChecklistItem[] {
  const existingById = new Map((existing ?? []).map((i) => [i.id, i]));
  const merged: ChecklistItem[] = [];
  for (const gen of generated) {
    const prev = existingById.get(gen.id);
    if (prev && prev.systemSuggested) {
      merged.push({
        ...gen,
        checkedAt: prev.checkedAt,
      });
      existingById.delete(gen.id);
    } else {
      merged.push(gen);
    }
  }
  // Append remaining user-added items
  for (const [, item] of existingById) {
    if (!item.systemSuggested) {
      merged.push(item);
    }
  }
  return merged;
}

/** Compute completion stats for the UI. */
export function checklistStats(checklist: PreTripChecklist | undefined): {
  total: number;
  checked: number;
  required: number;
  requiredChecked: number;
  percent: number;
  requiredPercent: number;
} {
  const items = checklist?.items ?? [];
  const total = items.length;
  const checked = items.filter((i) => i.checkedAt).length;
  const required = items.filter((i) => i.required).length;
  const requiredChecked = items.filter((i) => i.required && i.checkedAt).length;
  return {
    total, checked, required, requiredChecked,
    percent: total > 0 ? Math.round((checked / total) * 100) : 0,
    requiredPercent: required > 0 ? Math.round((requiredChecked / required) * 100) : 0,
  };
}
