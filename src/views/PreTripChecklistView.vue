<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import {
  NSpin, NSpace, NCard, NButton, NCheckbox, NInput, NSelect,
  NProgress, NTag, NAlert, NDatePicker, NIcon, useMessage,
} from 'naive-ui';
import { usePlanStore } from '@/stores/planStore';
import { useRoutesStore } from '@/stores/routesStore';
import {
  generateSuggestedItems, mergeChecklist, checklistStats,
} from '@/services/PreTripChecklist';
import type { ChecklistItem, ChecklistCategory, EmergencyContact, PreTripChecklist } from '@/types';

const props = defineProps<{ planId: string }>();
const planStore = usePlanStore();
const routesStore = useRoutesStore();
const router = useRouter();
const message = useMessage();

const loading = ref(true);
const checklist = ref<PreTripChecklist>({
  items: [],
  custodian: undefined,
  emergencyContacts: [],
  expectedReturnAt: undefined,
  notifyMethods: [],
  notes: '',
});

const plan = computed(() => planStore.currentPlan);
const route = computed(() => plan.value ? routesStore.getById(plan.value.routeId) : null);

const stats = computed(() => checklistStats(checklist.value));

const byCategory = computed(() => {
  const groups: Record<ChecklistCategory, ChecklistItem[]> = {
    legal: [], safety: [], gear: [], external: [], custom: [],
  };
  for (const item of checklist.value.items) {
    const cat = item.systemSuggested ? item.category : 'custom';
    groups[cat].push(item);
  }
  return groups;
});

const categoryMeta: Record<ChecklistCategory, { title: string; subtitle: string }> = {
  legal: { title: '法規申請', subtitle: '入山證、入園證、山屋訂位' },
  safety: { title: '安全資訊', subtitle: '留守人、緊急聯絡、保險' },
  gear: { title: '裝備', subtitle: '基本生命安全裝備檢查' },
  external: { title: '外部因素', subtitle: '天氣、交通、路況' },
  custom: { title: '自訂項目', subtitle: '個人化補充項目' },
};

async function loadAll() {
  loading.value = true;
  try {
    const id = Number(props.planId);
    await planStore.loadPlan(id);
    if (!plan.value) return;

    // Get existing checklist + regenerate suggestions
    const existing = plan.value.preTripChecklist;
    const generated = generateSuggestedItems(plan.value);
    const merged = mergeChecklist(existing?.items, generated);

    checklist.value = {
      items: merged,
      custodian: existing?.custodian ?? undefined,
      emergencyContacts: existing?.emergencyContacts ?? [],
      expectedReturnAt: existing?.expectedReturnAt ?? undefined,
      notifyMethods: existing?.notifyMethods ?? [],
      notes: existing?.notes ?? '',
    };
  } finally {
    loading.value = false;
  }
}

onMounted(loadAll);
watch(() => props.planId, loadAll);

function toggleItem(itemId: string, checked: boolean) {
  const item = checklist.value.items.find((i) => i.id === itemId);
  if (!item) return;
  item.checkedAt = checked ? new Date().toISOString() : undefined;
}

// ─── Custom items ───
const newItemTitle = ref('');
const newItemCategory = ref<ChecklistCategory>('custom');
const newItemRequired = ref(false);
const categoryOptions = [
  { label: '自訂', value: 'custom' },
  { label: '法規', value: 'legal' },
  { label: '安全', value: 'safety' },
  { label: '裝備', value: 'gear' },
  { label: '外部', value: 'external' },
];

function addCustomItem() {
  if (!newItemTitle.value.trim()) return;
  checklist.value.items.push({
    id: `user_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    category: newItemCategory.value,
    title: newItemTitle.value.trim(),
    required: newItemRequired.value,
    systemSuggested: false,
  });
  newItemTitle.value = '';
  newItemRequired.value = false;
}

function removeItem(id: string) {
  checklist.value.items = checklist.value.items.filter((i) => i.id !== id);
}

// ─── Emergency contacts ───
function addEmergencyContact() {
  if (!checklist.value.emergencyContacts) checklist.value.emergencyContacts = [];
  checklist.value.emergencyContacts.push({ name: '', phone: '', relation: '' });
}
function removeEmergencyContact(idx: number) {
  checklist.value.emergencyContacts?.splice(idx, 1);
}

function ensureCustodian(): EmergencyContact {
  if (!checklist.value.custodian) {
    checklist.value.custodian = { name: '', phone: '', relation: '留守人' };
  }
  return checklist.value.custodian;
}
ensureCustodian();

// ─── Expected return time (Naive uses timestamp ms) ───
const returnTs = computed<number | null>({
  get: () => checklist.value.expectedReturnAt
    ? new Date(checklist.value.expectedReturnAt).getTime()
    : null,
  set: (v) => {
    checklist.value.expectedReturnAt = v ? new Date(v).toISOString() : undefined;
  },
});

// ─── Save ───
async function save() {
  if (!plan.value) return;
  const updated = {
    ...JSON.parse(JSON.stringify(plan.value)),
    preTripChecklist: JSON.parse(JSON.stringify(checklist.value)),
  };
  await planStore.savePlan(updated);
  message.success('已儲存行前準備資料');
}

function backToSchedule() {
  router.push({ name: 'schedule', params: { planId: props.planId } });
}

function goToGearChecklist() {
  router.push({ name: 'gear', params: { planId: props.planId } });
}

function openExternalLink(url: string) {
  window.open(url, '_blank', 'noopener');
}
</script>

<template>
  <div class="p-6 max-w-5xl mx-auto">
    <NSpin :show="loading">
      <template v-if="plan && route">
        <header class="mb-4 flex justify-between items-start">
          <div>
            <h1 class="text-2xl font-bold">行前準備</h1>
            <p class="text-gray-600 mt-1">
              <span class="font-medium">{{ plan.name }}</span>
              <span class="text-sm text-gray-500 ml-2">
                · {{ route.name }} · 出發 {{ plan.startDate }} {{ plan.startTime }}
              </span>
            </p>
          </div>
          <NSpace>
            <NButton @click="backToSchedule">返回行程</NButton>
            <NButton type="primary" @click="save">儲存</NButton>
          </NSpace>
        </header>

        <!-- Progress summary -->
        <NCard size="small" class="mb-4">
          <div class="flex items-center gap-6 flex-wrap">
            <div class="flex-1 min-w-[200px]">
              <div class="text-sm text-gray-600 mb-1">
                全部進度：{{ stats.checked }} / {{ stats.total }}
              </div>
              <NProgress :percentage="stats.percent" :indicator-placement="'inside'" />
            </div>
            <div class="flex-1 min-w-[200px]">
              <div class="text-sm mb-1" :class="stats.requiredChecked < stats.required ? 'text-red-600 font-medium' : 'text-gray-600'">
                必要項目：{{ stats.requiredChecked }} / {{ stats.required }}
              </div>
              <NProgress
                :percentage="stats.requiredPercent"
                :status="stats.requiredChecked === stats.required ? 'success' : 'warning'"
                :indicator-placement="'inside'"
              />
            </div>
          </div>
          <NAlert
            v-if="stats.requiredChecked < stats.required"
            type="warning" class="mt-3"
          >
            還有 {{ stats.required - stats.requiredChecked }} 項必要項目未完成，請於出發前完成。
          </NAlert>
        </NCard>

        <!-- 法規申請 -->
        <NCard :title="categoryMeta.legal.title" class="mb-4">
          <template #header-extra>
            <span class="text-xs text-gray-500">{{ categoryMeta.legal.subtitle }}</span>
          </template>
          <div v-for="item in byCategory.legal" :key="item.id" class="py-2 border-b last:border-b-0">
            <div class="flex items-start gap-3">
              <NCheckbox
                :checked="!!item.checkedAt"
                @update:checked="(v) => toggleItem(item.id, v)"
              />
              <div class="flex-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span :class="{ 'line-through text-gray-400': item.checkedAt }">
                    {{ item.title }}
                  </span>
                  <NTag v-if="item.required" type="error" size="small">必要</NTag>
                </div>
                <p v-if="item.description" class="text-xs text-gray-500 mt-1">{{ item.description }}</p>
                <NButton
                  v-if="item.externalLink"
                  size="tiny" text type="info" class="mt-1"
                  @click="openExternalLink(item.externalLink)"
                >
                  開啟申請網址 →
                </NButton>
              </div>
            </div>
          </div>
        </NCard>

        <!-- 安全資訊 -->
        <NCard :title="categoryMeta.safety.title" class="mb-4">
          <template #header-extra>
            <span class="text-xs text-gray-500">{{ categoryMeta.safety.subtitle }}</span>
          </template>

          <!-- 留守人 -->
          <div class="mb-4 p-3 bg-emerald-50 rounded">
            <h3 class="text-sm font-medium mb-2">留守人（出發前及回程後須通知）</h3>
            <NSpace>
              <NInput v-model:value="ensureCustodian().name" placeholder="姓名" style="width: 140px" />
              <NInput v-model:value="ensureCustodian().phone" placeholder="電話" style="width: 160px" />
              <NInput v-model:value="ensureCustodian().relation" placeholder="關係" style="width: 100px" />
            </NSpace>
          </div>

          <!-- 預計回報時間 -->
          <div class="mb-4 p-3 bg-amber-50 rounded">
            <h3 class="text-sm font-medium mb-2">預計回報時間</h3>
            <NDatePicker
              v-model:value="returnTs"
              type="datetime"
              format="yyyy-MM-dd HH:mm"
              placeholder="選擇預計安全下山並回報的時間"
              style="width: 280px"
            />
            <p class="text-xs text-gray-500 mt-1">逾此時間未回報，留守人應啟動搜救聯絡。</p>
          </div>

          <!-- 緊急聯絡人 -->
          <div class="mb-4 p-3 bg-blue-50 rounded">
            <div class="flex justify-between items-center mb-2">
              <h3 class="text-sm font-medium">緊急聯絡人（至少 2 位）</h3>
              <NButton size="tiny" @click="addEmergencyContact">+ 新增</NButton>
            </div>
            <div v-if="!checklist.emergencyContacts?.length" class="text-xs text-gray-500">尚未新增</div>
            <div
              v-for="(c, idx) in checklist.emergencyContacts"
              :key="idx" class="mb-2"
            >
              <NSpace>
                <NInput v-model:value="c.name" placeholder="姓名" style="width: 140px" />
                <NInput v-model:value="c.phone" placeholder="電話" style="width: 160px" />
                <NInput v-model:value="c.relation" placeholder="關係" style="width: 100px" />
                <NButton size="small" tertiary @click="removeEmergencyContact(idx)">移除</NButton>
              </NSpace>
            </div>
          </div>

          <!-- 安全項目 checkbox list -->
          <div v-for="item in byCategory.safety" :key="item.id" class="py-2 border-b last:border-b-0">
            <div class="flex items-start gap-3">
              <NCheckbox
                :checked="!!item.checkedAt"
                @update:checked="(v) => toggleItem(item.id, v)"
              />
              <div class="flex-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span :class="{ 'line-through text-gray-400': item.checkedAt }">{{ item.title }}</span>
                  <NTag v-if="item.required" type="error" size="small">必要</NTag>
                </div>
                <p v-if="item.description" class="text-xs text-gray-500 mt-1">{{ item.description }}</p>
              </div>
            </div>
          </div>
        </NCard>

        <!-- 裝備 -->
        <NCard :title="categoryMeta.gear.title" class="mb-4">
          <template #header-extra>
            <NButton size="small" tertiary @click="goToGearChecklist">前往裝備清單 →</NButton>
          </template>
          <div v-for="item in byCategory.gear" :key="item.id" class="py-2 border-b last:border-b-0">
            <div class="flex items-start gap-3">
              <NCheckbox
                :checked="!!item.checkedAt"
                @update:checked="(v) => toggleItem(item.id, v)"
              />
              <div class="flex-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span :class="{ 'line-through text-gray-400': item.checkedAt }">{{ item.title }}</span>
                  <NTag v-if="item.required" type="error" size="small">必要</NTag>
                </div>
                <p v-if="item.description" class="text-xs text-gray-500 mt-1">{{ item.description }}</p>
                <NButton
                  v-if="item.internalRoute"
                  size="tiny" text type="info" class="mt-1"
                  @click="router.push(item.internalRoute)"
                >
                  前往 →
                </NButton>
              </div>
            </div>
          </div>
        </NCard>

        <!-- 外部因素 -->
        <NCard :title="categoryMeta.external.title" class="mb-4">
          <template #header-extra>
            <span class="text-xs text-gray-500">{{ categoryMeta.external.subtitle }}</span>
          </template>
          <div v-for="item in byCategory.external" :key="item.id" class="py-2 border-b last:border-b-0">
            <div class="flex items-start gap-3">
              <NCheckbox
                :checked="!!item.checkedAt"
                @update:checked="(v) => toggleItem(item.id, v)"
              />
              <div class="flex-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span :class="{ 'line-through text-gray-400': item.checkedAt }">{{ item.title }}</span>
                  <NTag v-if="item.required" type="error" size="small">必要</NTag>
                </div>
                <p v-if="item.description" class="text-xs text-gray-500 mt-1">{{ item.description }}</p>
                <NButton
                  v-if="item.externalLink"
                  size="tiny" text type="info" class="mt-1"
                  @click="openExternalLink(item.externalLink)"
                >
                  開啟連結 →
                </NButton>
              </div>
            </div>
          </div>
        </NCard>

        <!-- 自訂項目 -->
        <NCard :title="categoryMeta.custom.title" class="mb-4">
          <template #header-extra>
            <span class="text-xs text-gray-500">個人補充</span>
          </template>
          <div
            v-for="item in byCategory.custom"
            :key="item.id"
            class="py-2 border-b last:border-b-0"
          >
            <div class="flex items-start gap-3">
              <NCheckbox
                :checked="!!item.checkedAt"
                @update:checked="(v) => toggleItem(item.id, v)"
              />
              <div class="flex-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span :class="{ 'line-through text-gray-400': item.checkedAt }">{{ item.title }}</span>
                  <NTag v-if="item.required" type="error" size="small">必要</NTag>
                </div>
              </div>
              <NButton size="tiny" tertiary @click="removeItem(item.id)">移除</NButton>
            </div>
          </div>

          <div class="mt-3 pt-3 border-t flex gap-2 flex-wrap">
            <NInput v-model:value="newItemTitle" placeholder="新增項目..." style="min-width: 200px; flex: 1" />
            <NSelect v-model:value="newItemCategory" :options="categoryOptions" style="width: 100px" />
            <NCheckbox v-model:checked="newItemRequired">必要</NCheckbox>
            <NButton type="primary" @click="addCustomItem">＋ 加入</NButton>
          </div>
        </NCard>

        <!-- 備註 -->
        <NCard title="備註" class="mb-4">
          <NInput
            v-model:value="checklist.notes"
            type="textarea"
            placeholder="特殊天氣、隊員身體狀況、其他注意事項..."
            :autosize="{ minRows: 3, maxRows: 8 }"
          />
        </NCard>

        <div class="sticky bottom-0 bg-white py-3 border-t -mx-6 px-6 flex justify-end gap-2">
          <NButton @click="backToSchedule">返回</NButton>
          <NButton type="primary" size="large" @click="save">儲存行前準備</NButton>
        </div>
      </template>
    </NSpin>
  </div>
</template>
