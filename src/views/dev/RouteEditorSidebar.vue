<script setup lang="ts">
import { ref } from 'vue';
import {
  NCollapse, NCollapseItem, NButton, NInput, NInputNumber,
  NSelect, NCheckbox, NTag, useMessage,
} from 'naive-ui';
import type { Route, RouteNode, RouteEdge, OsmPoi, NodeCategory } from '@/types';
import RouteEditorMatcher from './RouteEditorMatcher.vue';

const props = defineProps<{
  route: Route;
  osmPois: OsmPoi[];
}>();

const emit = defineEmits<{ save: [] }>();

const message = useMessage();

const categoryOptions: Array<{ label: string; value: NodeCategory }> = [
  { label: '⛰ 山頭', value: 'peak' },
  { label: '🏠 山屋', value: 'hut' },
  { label: '🚪 登山口', value: 'trailhead' },
  { label: '🔀 岔路', value: 'junction' },
  { label: '💧 水源', value: 'water' },
  { label: '⛳ 其他', value: 'waypoint' },
];

const editingNodeId = ref<string | null>(null);
const editingEdgeIndex = ref<number | null>(null);

function addNode(): void {
  const id = `n_${props.route.id.toLowerCase()}_${Date.now()}`;
  props.route.nodes.push({
    id, name: '', lat: 0, lng: 0, elevation: 0, category: 'waypoint',
  });
  editingNodeId.value = id;
}

function removeNode(nodeId: string): void {
  const idx = props.route.nodes.findIndex((n) => n.id === nodeId);
  if (idx >= 0) props.route.nodes.splice(idx, 1);
  for (let i = props.route.edges.length - 1; i >= 0; i--) {
    if (props.route.edges[i].from === nodeId || props.route.edges[i].to === nodeId) {
      props.route.edges.splice(i, 1);
    }
  }
}

const OSM_TO_NODE_CATEGORY: Record<string, NodeCategory> = {
  trailhead: 'trailhead',
  hut: 'hut',
  shelter: 'hut',         // mountain shelter mapped to hut for app's category model
  peak: 'peak',
  junction: 'junction',
  water: 'water',
  waypoint: 'waypoint',
};

function selectMatchedPoi(node: RouteNode, poi: OsmPoi): void {
  node.lat = poi.lat;
  node.lng = poi.lon;
  if (poi.elevation !== null) node.elevation = poi.elevation;
  if (!node.name) node.name = poi.name;
  const mapped = OSM_TO_NODE_CATEGORY[poi.tags.category];
  if (mapped && mapped !== 'waypoint') node.category = mapped;
}

function addEdge(): void {
  if (props.route.nodes.length < 2) {
    message.warning('至少需要 2 個節點才能新增邊');
    return;
  }
  props.route.edges.push({
    from: props.route.nodes[0].id,
    to: props.route.nodes[1].id,
    minutes_forward: 0,
    minutes_backward: 0,
    source: 'manual',
    sources: [],
    confirmed: false,
  });
  editingEdgeIndex.value = props.route.edges.length - 1;
}

function removeEdge(idx: number): void {
  props.route.edges.splice(idx, 1);
}

function addEdgeSource(edge: RouteEdge): void {
  if (!edge.sources) edge.sources = [];
  edge.sources.push({
    file: '', minutes_forward: null, minutes_backward: null, notedBy: 'manual',
  });
}

function removeEdgeSource(edge: RouteEdge, idx: number): void {
  edge.sources?.splice(idx, 1);
}

function isEdgeInconsistent(edge: RouteEdge): boolean {
  if (!edge.sources || edge.sources.length < 2) return false;
  const fwd = edge.sources.map((s) => s.minutes_forward).filter((v) => v !== null);
  const bwd = edge.sources.map((s) => s.minutes_backward).filter((v) => v !== null);
  return new Set(fwd).size > 1 || new Set(bwd).size > 1;
}

function nodeOptions() {
  return props.route.nodes.map((n) => ({ label: `${n.name || '(未命名)'} [${n.id}]`, value: n.id }));
}
</script>

<template>
  <div class="h-full overflow-y-auto p-3 space-y-3">
    <NCollapse :default-expanded-names="['nodes', 'edges']">
      <NCollapseItem :title="`節點 (${route.nodes.length})`" name="nodes">
        <div v-for="n in route.nodes" :key="n.id" class="border rounded p-2 mb-2">
          <div class="flex justify-between items-center mb-1">
            <strong class="text-xs">{{ n.name || '(未命名)' }}</strong>
            <div class="flex gap-1">
              <NButton size="tiny" @click="editingNodeId = editingNodeId === n.id ? null : n.id">
                {{ editingNodeId === n.id ? '收起' : '編輯' }}
              </NButton>
              <NButton size="tiny" type="error" ghost @click="removeNode(n.id)">✕</NButton>
            </div>
          </div>
          <div class="text-xs text-gray-500">
            {{ n.lat.toFixed(4) }}, {{ n.lng.toFixed(4) }} · {{ n.elevation }}m · {{ n.category }}
          </div>
          <div v-if="editingNodeId === n.id" class="mt-2 space-y-2">
            <NInput v-model:value="n.name" placeholder="名稱" size="small" />
            <div class="flex gap-2">
              <NInputNumber v-model:value="n.lat" placeholder="lat" size="small" :precision="6" />
              <NInputNumber v-model:value="n.lng" placeholder="lng" size="small" :precision="6" />
            </div>
            <NInputNumber v-model:value="n.elevation" placeholder="elevation" size="small" />
            <NSelect v-model:value="n.category" :options="categoryOptions" size="small" />
            <NInput v-model:value="n.hutId" placeholder="hutId (optional)" size="small" />
            <RouteEditorMatcher
              :node-name="n.name"
              :pois="osmPois"
              @select="(poi) => selectMatchedPoi(n, poi)"
            />
          </div>
        </div>
        <NButton size="small" block dashed @click="addNode">+ 新增節點</NButton>
      </NCollapseItem>

      <NCollapseItem :title="`邊 (${route.edges.length})`" name="edges">
        <div v-for="(e, i) in route.edges" :key="i" class="border rounded p-2 mb-2">
          <div class="flex justify-between items-center mb-1">
            <span class="text-xs">{{ e.from }} → {{ e.to }}</span>
            <div class="flex gap-1">
              <NButton size="tiny" @click="editingEdgeIndex = editingEdgeIndex === i ? null : i">
                {{ editingEdgeIndex === i ? '收起' : '編輯' }}
              </NButton>
              <NButton size="tiny" type="error" ghost @click="removeEdge(i)">✕</NButton>
            </div>
          </div>
          <div class="text-xs flex gap-2 items-center">
            <span>去 {{ e.minutes_forward }}m / 返 {{ e.minutes_backward }}m</span>
            <NTag v-if="e.confirmed" type="success" size="small">✓</NTag>
            <NTag v-else type="warning" size="small">待確認</NTag>
            <NTag v-if="isEdgeInconsistent(e)" type="error" size="small">⚠ 來源不一致</NTag>
          </div>
          <div v-if="editingEdgeIndex === i" class="mt-2 space-y-2">
            <div class="flex gap-1">
              <NSelect v-model:value="e.from" :options="nodeOptions()" size="small" />
              <NSelect v-model:value="e.to" :options="nodeOptions()" size="small" />
            </div>
            <div class="flex gap-1">
              <NInputNumber v-model:value="e.minutes_forward" placeholder="去程分鐘" size="small" />
              <NInputNumber v-model:value="e.minutes_backward" placeholder="返程分鐘" size="small" />
            </div>
            <div>
              <div class="text-xs text-gray-500 mb-1">來源 (交叉驗證)</div>
              <div v-for="(s, si) in e.sources ?? []" :key="si" class="flex gap-1 mb-1 text-xs">
                <NInput v-model:value="s.file" placeholder="檔名" size="small" />
                <NInputNumber v-model:value="s.minutes_forward" placeholder="去" size="small" style="width: 60px" />
                <NInputNumber v-model:value="s.minutes_backward" placeholder="返" size="small" style="width: 60px" />
                <NButton size="tiny" type="error" ghost @click="removeEdgeSource(e, si)">✕</NButton>
              </div>
              <NButton size="tiny" @click="addEdgeSource(e)">+ 來源</NButton>
            </div>
            <NCheckbox v-model:checked="e.confirmed" :disabled="isEdgeInconsistent(e)">
              ✓ 已確認時間正確
            </NCheckbox>
          </div>
        </div>
        <NButton size="small" block dashed @click="addEdge">+ 新增邊</NButton>
      </NCollapseItem>
    </NCollapse>

    <NButton type="primary" block size="small" @click="emit('save')">💾 下載 JSON</NButton>
  </div>
</template>
