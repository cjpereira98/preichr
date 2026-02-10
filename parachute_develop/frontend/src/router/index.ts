import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/HomeView.vue') },
  { path: '/example', name: 'Example', component: () => import('../views/ExampleView.vue') },
  { path: '/staffing_plan', name: 'Staffing Plan', component: () => import('../views/StaffingPlanView.vue') },
  { path: '/am_scorecard', name: 'AM Scorecard', component: () => import('../views/AMScorecardView.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/SettingsView.vue') },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
