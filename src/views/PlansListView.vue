<script setup lang="ts">
import { onMounted } from 'vue';
import { NCard, NEmpty, NList, NListItem, NButton, NSpace, NPopconfirm, useMessage } from 'naive-ui';
import { useRouter } from 'vue-router';
import { usePlanStore } from '@/stores/planStore';
import TripTypeBadge from '@/components/common/TripTypeBadge.vue';

const planStore = usePlanStore();
const router = useRouter();
const message = useMessage();

onMounted(() => planStore.loadAllPlans());

async function deletePlan(id: number) {
  await planStore.deletePlan(id);
  message.success('已刪除');
}
</script>

<template>
  <div class="p-4 sm:p-6 max-w-4xl mx-auto">
    <h1 class="text-xl sm:text-2xl font-bold mb-4 text-brand-900">我的行程</h1>
    <NEmpty v-if="planStore.plans.length === 0" description="還沒建立任何行程">
      <template #extra>
        <NButton type="primary" @click="router.push('/routes')">前往路線</NButton>
      </template>
    </NEmpty>
    <NList v-else>
      <NListItem v-for="plan in planStore.plans" :key="plan.id">
        <NCard size="small">
          <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
            <div class="min-w-0 flex-1">
              <strong class="text-brand-900 break-words">{{ plan.name }}</strong>
              <div class="text-sm text-brand-gray mt-1">
                {{ plan.startDate }} · 倍率 {{ plan.paceMultiplier }}x · 節點 {{ plan.nodeSequence.length }}
              </div>
              <div class="mt-2">
                <TripTypeBadge :trip-type="plan.tripType" :custom-label="plan.customTripTypeLabel" />
              </div>
            </div>
            <div class="flex flex-wrap gap-2 sm:flex-shrink-0">
              <NButton
                size="small"
                @click="router.push({ name: 'schedule', params: { planId: plan.id } })"
              >
                查看
              </NButton>
              <NButton
                size="small"
                @click="router.push({ name: 'gear', params: { planId: plan.id } })"
              >
                裝備
              </NButton>
              <NPopconfirm @positive-click="deletePlan(plan.id!)">
                <template #trigger>
                  <NButton size="small" type="error" ghost>刪除</NButton>
                </template>
                確定刪除？
              </NPopconfirm>
            </div>
          </div>
        </NCard>
      </NListItem>
    </NList>
  </div>
</template>
