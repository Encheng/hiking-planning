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
  <div class="p-6 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">我的行程</h1>
    <NEmpty v-if="planStore.plans.length === 0" description="還沒建立任何行程">
      <template #extra>
        <NButton type="primary" @click="router.push('/routes')">前往路線</NButton>
      </template>
    </NEmpty>
    <NList v-else>
      <NListItem v-for="plan in planStore.plans" :key="plan.id">
        <NCard size="small">
          <NSpace justify="space-between" align="center">
            <div>
              <strong>{{ plan.name }}</strong>
              <div class="text-sm text-gray-500">
                {{ plan.startDate }} · 倍率 {{ plan.paceMultiplier }}x · 節點 {{ plan.nodeSequence.length }}
              </div>
              <TripTypeBadge :trip-type="plan.tripType" />
            </div>
            <NSpace>
              <NButton size="small" @click="router.push({ name: 'schedule', params: { planId: plan.id } })">查看</NButton>
              <NButton size="small" @click="router.push({ name: 'gear', params: { planId: plan.id } })">裝備</NButton>
              <NPopconfirm @positive-click="deletePlan(plan.id!)">
                <template #trigger>
                  <NButton size="small" type="error" ghost>刪除</NButton>
                </template>
                確定刪除？
              </NPopconfirm>
            </NSpace>
          </NSpace>
        </NCard>
      </NListItem>
    </NList>
  </div>
</template>
