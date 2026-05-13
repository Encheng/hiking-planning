<script setup lang="ts">
import { inject, watch, onBeforeUnmount, type Ref } from 'vue';
import L from 'leaflet';
import 'leaflet-gpx';

const props = defineProps<{ url: string; color?: string; weight?: number; opacity?: number }>();
const map = inject<Ref<L.Map | null>>('leaflet-map')!;

let gpxLayer: any = null;

function load() {
  if (!map.value) return;
  if (gpxLayer) {
    map.value.removeLayer(gpxLayer);
    gpxLayer = null;
  }
  // @ts-expect-error leaflet-gpx augments L
  gpxLayer = new L.GPX(props.url, {
    async: true,
    polyline_options: {
      color: props.color ?? '#dc2626',
      weight: props.weight ?? 3,
      opacity: props.opacity ?? 1,
    },
    // Disable start/end markers so they don't overlap with route node markers
    markers: { startIcon: null, endIcon: null },
  }).on('loaded', (e: any) => {
    map.value?.fitBounds(e.target.getBounds());
  }).addTo(map.value);
}

watch(map, (m) => {
  if (m) load();
}, { immediate: true });
watch(() => props.url, () => load());

onBeforeUnmount(() => {
  if (gpxLayer && map.value) map.value.removeLayer(gpxLayer);
});
</script>

<template><div /></template>
