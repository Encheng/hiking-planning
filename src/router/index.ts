import { createRouter, createWebHistory } from 'vue-router';

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/routes' },
    { path: '/routes', component: () => import('@/views/RoutesListView.vue') },
  ],
});
