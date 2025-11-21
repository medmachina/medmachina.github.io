<template>
  <div v-if="company">
    <div class="header-with-logo d-flex align-items-center justify-content-between mb-4">
      <h1 class="mb-0">
        <router-link to="/companies" class="btn btn-outline-primary btn-lg" style="vertical-align:middle;">Companies</router-link> {{ company.name }}
      </h1>
      <router-link to="/" style="display: flex; align-items: center; text-decoration: none;">
        <img src="/text-logo.svg" alt="medmachina" style="height:41px; width:auto;" />
      </router-link>
    </div>

    <div class="container py-4">

      <div class="card mb-4">
        <div class="card-body">
          <h2 class="card-title h5">Information</h2>
          <p><strong>Country:</strong> {{ company.country }}</p>
          <p v-if="company.description">{{ company.description }}</p>

          <div v-if="company.linkedin_url" class="linkedin-container">
            <a :href="company.linkedin_url" target="_blank" rel="noopener noreferrer" class="linkedin-link">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="linkedin-icon">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
              </svg>
              <span>LinkedIn</span>
            </a>
          </div>

          <div v-if="company.urls && company.urls.length">
            <h3 class="h6 mt-4">Links</h3>
            <ul class="list-unstyled">
              <li v-for="url in company.urls" :key="url" class="mb-2">
                <a :href="url.url" target="_blank" rel="noopener noreferrer">{{ url.caption }}</a>
              </li>
            </ul>
          </div>

          <!-- Edit on GitHub Section -->
          <div class="edit-section mt-4">
            <a 
              href="https://github.com/medmachina/medmachina.github.io/edit/main/public/companies.json" 
              target="_blank" 
              rel="noopener noreferrer"
              class="btn btn-outline-secondary"
              title="Edit this company on GitHub"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 4px;">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
              </svg>
              Edit on GitHub
            </a>
          </div>
        </div>
      </div>

      <div class="card mb-4" v-if="companyRobots.length > 0">
        <div class="card-body">
          <h2 class="card-title h5">Robots</h2>
          <div class="row g-3">
            <div v-for="robot in companyRobots" :key="robot.id" class="col-12 col-md-6 col-lg-4">
              <div class="card h-100 shadow-sm card-clickable" @click="goToRobotDetail(robot)">
                <template v-if="getFirstPhotoUrl(robot)">
                  <img :src="getFirstPhotoUrl(robot)" alt="photo" class="card-img-top rounded-top"
                       style="object-fit:cover; max-height:180px; border-top-left-radius:1rem; border-top-right-radius:1rem;"
                       @error="handleImageError" />
                </template>
                <div class="card-body">
                  <h5 class="card-title">{{ robot.name }}</h5>
                  <div class="mb-2">
                    <span v-for="(tag, idx) in robot.tags.slice(0,5)" :key="tag" class="badge bg-secondary me-1">{{ tag }}</span>
                    <span v-if="robot.tags.length > 5">...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="container py-4">
    <div class="alert alert-warning">
      Company not found
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const company = ref(null);
const allRobots = ref([]);

onMounted(async () => {
  try {
    // Load companies data
    const companyResponse = await fetch('/companies.json');
    const companies = await companyResponse.json();

    // Find current company by name
    const companyName = route.params.name;
    company.value = companies.find(c => c.name === companyName);

    // Load robots data
    const robotsResponse = await fetch('/robots.json');
    allRobots.value = await robotsResponse.json();
  } catch (error) {
    console.error('Error loading data:', error);
  }
});

const companyRobots = computed(() => {
  if (!company.value || !company.value.robots || !allRobots.value.length) {
    return [];
  }

  return allRobots.value.filter(robot => company.value.robots.includes(robot.id));
});

function goToRobotDetail(robot) {
  router.push(`/robot/${robot.id}`);
}

function getFirstPhotoUrl(item) {
  return item.photos && item.photos.length > 0 ? item.photos[0].url : null;
}

function handleImageError(event) {
  event.target.src = '/text-logo.svg'; // Fallback image on error
}
</script>

<style scoped>
.card {
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 8px;
}

.card-title {
  color: var(--color-heading);
}

.card-text {
  color: var(--color-text);
}

.text-ellipsis {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.title {
  color: var(--color-heading);
}

.card-clickable {
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.card-clickable:hover {
  box-shadow: 0 4px 16px rgba(255,255,255,0.1);
}

.linkedin-container {
  margin: 1rem 0;
}

.linkedin-link {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background-color: #0077B5;
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.linkedin-link:hover {
  background-color: #005582;
  color: white;
}

.linkedin-icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
  margin-right: 8px;
}
</style>
