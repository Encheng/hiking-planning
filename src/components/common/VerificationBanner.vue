<script setup lang="ts">
import { computed } from 'vue';
import { NAlert } from 'naive-ui';
import { useRoutesStore } from '@/stores/routesStore';

const props = defineProps<{ routeId: string | undefined }>();

const routesStore = useRoutesStore();
const level = computed(() => (props.routeId ? routesStore.getVerification(props.routeId) : 'estimated'));

const config = computed(() => {
  switch (level.value) {
    case 'sunriver_verified':
      return { type: 'success', title: '時間已通過驗證', body: '節點與步程時間已逐筆對照上河圖並由人類覆核。' } as const;
    case 'sunriver_pending':
      return { type: 'info', title: '時間部分驗證', body: '節點來自上河圖步程示意圖，但仍有未逐筆覆核的段落。請保留至少 20% 緩衝。' } as const;
    case 'estimated':
    default:
      return {
        type: 'warning',
        title: '⚠ 時間為 AI 估算，未對照上河圖',
        body: '本路線節點與時間尚未經上河圖驗證，誤差可能很大。實際入山請務必交叉比對紙本上河圖、林務局申請資料、或健行筆記實測軌跡，並預留充足的時間與物資。錯誤的步程預估可能導致摸黑、體力透支等山難風險。',
      } as const;
  }
});
</script>

<template>
  <NAlert
    v-if="level !== 'n/a'"
    :type="config.type"
    :title="config.title"
    class="mb-3"
  >
    {{ config.body }}
  </NAlert>
</template>
