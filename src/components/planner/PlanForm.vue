<script setup lang="ts">
import { ref, watch } from 'vue';
import { NCard, NForm, NFormItem, NDatePicker, NTimePicker } from 'naive-ui';
import PaceSlider from './PaceSlider.vue';
import { usePlanStore } from '@/stores/planStore';
import { useSettingsStore } from '@/stores/settingsStore';

const planStore = usePlanStore();
const settings = useSettingsStore();

const draft = planStore.draft ?? {};
const pace = ref<number>(draft.paceMultiplier ?? settings.defaultPaceMultiplier);
const startDateTs = ref<number>(draft.startDate ? new Date(draft.startDate).getTime() : Date.now());
const startTimeTs = ref<number>(draft.startTime ? hmToMs(draft.startTime) : hmToMs('06:00'));

function hmToMs(hm: string) {
  const [h, m] = hm.split(':').map(Number);
  const d = new Date();
  d.setHours(h, m, 0, 0);
  return d.getTime();
}

function msToHm(ms: number) {
  const d = new Date(ms);
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

watch([pace, startDateTs, startTimeTs], () => {
  planStore.draft = {
    ...(planStore.draft ?? {}),
    paceMultiplier: pace.value,
    startDate: new Date(startDateTs.value).toISOString().slice(0, 10),
    startTime: msToHm(startTimeTs.value),
  };
});
</script>

<template>
  <NCard title="行程設定">
    <NForm label-placement="left" label-width="80">
      <NFormItem label="出發日期">
        <NDatePicker v-model:value="startDateTs" type="date" />
      </NFormItem>
      <NFormItem label="出發時間">
        <NTimePicker v-model:value="startTimeTs" format="HH:mm" />
      </NFormItem>
      <NFormItem label="腳程">
        <PaceSlider v-model="pace" />
      </NFormItem>
    </NForm>
  </NCard>
</template>
