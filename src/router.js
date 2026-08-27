import { createRouter, createWebHistory } from 'vue-router';
import RobotList from './components/RobotList.vue';
import RobotDetail from './components/RobotDetail.vue';
import TestComponent from './components/TestComponent.vue';
import HomeComponent from './components/HomeComponent.vue';
import HowToContribute from './components/HowToContribute.vue';
import Links from './components/Links.vue';
import CompaniesComponent from './components/CompaniesComponent.vue';
import CompanyDetail from './components/CompanyDetail.vue';
import Publications from './components/Publications.vue';
import { updateSeo } from './utils/seo';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeComponent,
    meta: {
      title: 'Medical Robots Directory | Med Machina',
      description: 'A spare-time, best-effort directory listing medical and surgical robotics systems, companies, and regulatory approvals. Community contributions are welcome!',
      jsonLd: {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': 'Med Machina',
        'url': 'https://medmachina.github.io/',
        'description': 'A spare-time, best-effort directory listing medical and surgical robotics systems, companies, and regulatory approvals. Community contributions are welcome!'
      }
    }
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
    component: HowToContribute,
    meta: {
      title: 'How to Contribute | Med Machina',
      description: 'Learn how to contribute data or request updates for the Med Machina surgical robotics directory.'
    }
  },
  {
    path: '/links',
    name: 'Links',
    component: Links,
    meta: {
      title: 'Medical Robotics Links & Resources | Med Machina',
      description: 'Curated links and resources for medical robotics, regulatory databases, and industry news.'
    }
  },
  {
    path: '/companies',
    name: 'Companies',
    component: CompaniesComponent,
    meta: {
      title: 'Medical Robotics Companies | Med Machina',
      description: 'Browse companies manufacturing medical and surgical robotics systems worldwide.'
    }
  },
  {
    path: '/company/:name',
    name: 'CompanyDetail',
    component: CompanyDetail
  },
  {
    path: '/publications',
    name: 'Publications',
    component: Publications,
    meta: {
      title: 'Medical Robotics Publications & Literature | Med Machina',
      description: 'Curated landmark research papers, clinical trials, and survey articles covering the field of medical and surgical robotics.'
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.afterEach((to) => {
  if (to.meta && to.meta.title) {
    updateSeo({
      title: to.meta.title,
      description: to.meta.description,
      path: to.path,
      jsonLd: to.meta.jsonLd
    });
  }
});

export default router;

