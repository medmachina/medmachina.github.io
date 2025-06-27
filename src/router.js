import { createRouter, createWebHistory } from 'vue-router';
import CardList from './components/CardList.vue';
import ProjectDetail from './components/ProjectDetail.vue';
import TestComponent from './components/TestComponent.vue';
import HomeComponent from './components/HomeComponent.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeComponent
  },
  {
    path: '/robot/:id',
    name: 'RobotDetail',
    component: ProjectDetail//,
    //props: true
  },
  {
    path: '/test',
    name: 'Test',
    component: TestComponent
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
