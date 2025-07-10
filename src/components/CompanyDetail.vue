<template>
  <div v-if="company">
    <div class="container py-4">
      <h1 class="mb-4 title">{{ company.name }}</h1>

      <div class="card mb-4">
        <div class="card-body">
          <h2 class="card-title h5">Information</h2>
          <p><strong>Country:</strong> {{ company.country }}</p>
          <p v-if="company.description">{{ company.description }}</p>

          <div v-if="company.urls && company.urls.length">
            <h3 class="h6 mt-4">Links</h3>
            <ul class="list-unstyled">
              <li v-for="url in company.urls" :key="url" class="mb-2">
                <a :href="url" target="_blank" rel="noopener noreferrer">{{ url }}</a>
              </li>
            </ul>
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
                  <h5 class="card-title">{{ robot.project_name }}</h5>
                  <p class="card-text text-ellipsis">{{ robot.description }}</p>
                  <div class="mb-2">
                    <span v-for="tag in robot.tags" :key="tag" class="badge bg-secondary me-1">{{ tag }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4">
        <router-link to="/companies" class="btn btn-outline-primary">
          Back to Companies
        </router-link>
      </div>
    </div>
  </div>
  <div v-else class="container py-4">
    <div class="alert alert-warning">
      Company not found
    </div>
    <router-link to="/companies" class="btn btn-outline-primary">
      Back to Companies
    </router-link>
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
    // Charger les données des entreprises
    const companyResponse = await fetch('/companies.json');
    const companies = await companyResponse.json();

    // Trouver l'entreprise actuelle par son nom
    const companyName = route.params.name;
    company.value = companies.find(c => c.name === companyName);

    // Charger les données des robots
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
  return item.photoURL && item.photoURL.length > 0 ? item.photoURL[0] : null;
}

function handleImageError(event) {
  event.target.src = '/src/assets/bot.png'; // Image de remplacement en cas d'erreur
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

.btn-outline-primary {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-outline-primary:hover {
  background-color: var(--color-primary);
  color: white;
}
</style>
