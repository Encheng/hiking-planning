import { createRouter, createWebHistory } from 'vue-router';

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/routes' },
    { path: '/routes', name: 'routes', component: () => import('@/views/RoutesListView.vue') },
    { path: '/map', name: 'map', component: () => import('@/views/MapPlannerView.vue') },
    { path: '/plans', name: 'plans', component: () => import('@/views/PlansListView.vue') },
    { path: '/schedule/:planId', name: 'schedule', component: () => import('@/views/PlanScheduleView.vue'), props: true },
    { path: '/gear/:planId', name: 'gear', component: () => import('@/views/GearChecklistView.vue'), props: true },
    { path: '/settings', name: 'settings', component: () => import('@/views/SettingsView.vue') },
  ],
});
