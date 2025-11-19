import { createRouter, createWebHistory } from 'vue-router';
import RobotList from './components/RobotList.vue';
import RobotDetail from './components/RobotDetail.vue';
import TestComponent from './components/TestComponent.vue';
import HomeComponent from './components/HomeComponent.vue';
import HowToContribute from './components/HowToContribute.vue';
import ContactUs from './components/ContactUs.vue';
import CompaniesComponent from './components/CompaniesComponent.vue';
import CompanyDetail from './components/CompanyDetail.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeComponent
  },
  {
    path: '/robot/:id',
    name: 'RobotDetail',
    component: RobotDetail
  },
  {
    path: '/test',
    name: 'Test',
    component: TestComponent
  },
  {
    path: '/contribute',
    name: 'Contribute',
    component: HowToContribute
  },
  {
    path: '/contact',
    name: 'Contact',
    component: ContactUs
  },
  {
    path: '/companies',
    name: 'Companies',
    component: CompaniesComponent
  },
  {
    path: '/company/:name',
    name: 'CompanyDetail',
    component: CompanyDetail
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
