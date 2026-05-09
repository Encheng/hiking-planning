<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, shallowRef, provide, watch } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const props = defineProps<{
  center: [number, number];
  zoom: number;
}>();

const mapEl = ref<HTMLDivElement | null>(null);
const mapInstance = shallowRef<L.Map | null>(null);

provide('leaflet-map', mapInstance);

onMounted(() => {
  if (!mapEl.value) return;
  const map = L.map(mapEl.value, {
    center: props.center,
    zoom: props.zoom,
  });
  mapInstance.value = map;
});

onBeforeUnmount(() => {
  mapInstance.value?.remove();
  mapInstance.value = null;
});

watch(() => props.center, (val) => mapInstance.value?.setView(val));
watch(() => props.zoom, (val) => mapInstance.value && mapInstance.value.setZoom(val));
</script>

<template>
  <div ref="mapEl" class="w-full h-full">
    <slot v-if="mapInstance" />
  </div>
</template>
