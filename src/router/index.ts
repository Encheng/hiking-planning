import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/routes' },
  { path: '/routes', name: 'routes', component: () => import('@/views/RoutesListView.vue') },
  { path: '/map', name: 'map', component: () => import('@/views/MapPlannerView.vue') },
  { path: '/plans', name: 'plans', component: () => import('@/views/PlansListView.vue') },
  { path: '/schedule/:planId', name: 'schedule', component: () => import('@/views/PlanScheduleView.vue'), props: true },
  { path: '/gear/:planId', name: 'gear', component: () => import('@/views/GearChecklistView.vue'), props: true },
  { path: '/checklist/:planId', name: 'checklist', component: () => import('@/views/PreTripChecklistView.vue'), props: true },
  { path: '/settings', name: 'settings', component: () => import('@/views/SettingsView.vue') },
];

if (import.meta.env.DEV) {
  routes.push({
    path: '/dev/route-editor',
    name: 'dev-route-editor',
    component: () => import('@/views/dev/RouteEditorView.vue'),
  });
}

export default createRouter({
  history: createWebHistory(),
  routes,
});
