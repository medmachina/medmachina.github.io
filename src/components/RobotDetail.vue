<template>
  <div class="project-detail">
    <div class="header">
      <button class="home-btn" @click="goHome" title="Accueil">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
      </button>
      <h1 class="project-title">{{ filteredProject["project_name"] }}</h1>
    </div>

    <div class="project-description">
      {{ filteredProject["description"] }}
    </div>

    <!-- Photo Gallery Section -->
    <div v-if="validPhotoUrls.length > 0" class="photo-gallery">
      <div class="gallery-grid">
        <div
          v-for="(photoUrl, index) in validPhotoUrls"
          :key="index"
          class="photo-item"
          @click="openPhoto(photoUrl)"
        >
          <img
            :src="photoUrl"
            :alt="`Photo ${index + 1} du projet`"
            class="photo-thumbnail"
            @error="handleImageError(photoUrl)"
          />
        </div>
      </div>
    </div>

    <!-- Tags Section -->
    <div v-if="projectTags.length > 0" class="tags-section">
      <div class="d-flex flex-wrap align-items-center gap-2">
        <span
          v-for="tag in projectTags"
          :key="tag"
          class="badge tag-cloud-badge dark-tag"
        >
          {{ tag }}
        </span>
      </div>
    </div>

    <!-- URLs Section -->
    <div v-if="projectUrls.length > 0" class="urls-section">
      <h3>Links</h3>
      <div class="url-list">
        <div v-for="(url, index) in projectUrls" :key="index" class="url-item">
          <div class="url-info">
            <button class="btn btn-primary" @click="openUrl(url)">{{ getUrlTitle(url) }}</button>
            <span class="url-complete">({{ url }})</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Company Link Section -->
    <div v-if="companyInfo" class="company-link-section">
      <h3>Company</h3>
      <div class="company-info">
        <div class="company-details">
          <strong>{{ companyInfo.name }}</strong>
          <p>{{ companyInfo.description }}</p>
        </div>
        <button class="btn btn-primary" @click="goToCompany(companyInfo.name)">
          See company details
        </button>
      </div>
    </div>

    <div v-if="!project">
      <p>Projet introuvable.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const project = ref(null);
const companies = ref([]);
const invalidPhotoUrls = ref(new Set()); // Set pour stocker les URLs d'images invalides

onMounted(async () => {
  console.log("Fetching project data for ID:", route.params.id);

  // Charger les données des robots
  const resRobots = await fetch('/robots.json');
  const dataRobots = await resRobots.json();
  project.value = dataRobots.find(p => String(p.id) === route.params.id);

  // Charger les données des entreprises
  const resCompanies = await fetch('/companies.json');
  const dataCompanies = await resCompanies.json();
  companies.value = dataCompanies;
});

function goHome() {
  router.push('/');
}

function isUrl(value) {
  return /^(http|https):\/\/[^ "]+$/.test(value);
}

function getUrlTitle(url) {
  const urlObj = new URL(url);
  return urlObj.hostname.replace('www.', '');
}

function openUrl(url) {
  window.open(url, '_blank');
}

function openPhoto(photoUrl) {
  window.open(photoUrl, '_blank');
}

function handleImageError(photoUrl) {
  console.warn('Image non disponible:', photoUrl);

  // Ajouter l'URL à la liste des URLs invalides
  invalidPhotoUrls.value.add(photoUrl);
}

// Computed property pour trouver l'entreprise associée au robot
const companyInfo = computed(() => {
  if (!project.value || !companies.value.length) return null;

  return companies.value.find(company =>
    company.robots && company.robots.includes(project.value.id)
  );
});

// Fonction pour naviguer vers la page de détail de l'entreprise
function goToCompany(companyName) {
  router.push(`/company/${companyName}`);
}

// Computed properties pour extraire les photos et filtrer le projet
const photoUrls = computed(() => {
  if (!project.value?.photoURL) return [];

  // Si photoURL est une chaîne avec plusieurs URLs séparées par des virgules
  if (typeof project.value.photoURL === 'string') {
    return project.value.photoURL.split(',').map(url => url.trim()).filter(url => url);
  }

  // Si photoURL est un array
  if (Array.isArray(project.value.photoURL)) {
    return project.value.photoURL.filter(url => url);
  }

  // Si photoURL est une seule URL
  return [project.value.photoURL];
});

// Filtrer les URLs des photos valides (celles qui ne sont pas cassées)
const validPhotoUrls = computed(() => {
  return photoUrls.value.filter(url => {
    // Vérifier si l'URL de l'image est valide et n'est pas dans la liste des URLs invalides
    return isUrl(url) && !invalidPhotoUrls.value.has(url);
  });
});

const filteredProject = computed(() => {
  if (!project.value) return {};

  const filtered = { ...project.value };
  delete filtered.photoURL; // Supprimer photoURL car affiché séparément
  delete filtered.tags; // Supprimer tags car affiché séparément
  delete filtered.urls; // Supprimer urls car affiché séparément
  return filtered;
});

// Computed property pour les tags du projet
const projectTags = computed(() => {
  if (!project.value?.tags) return [];

  // Si tags est un array (comme dans les données JSON)
  if (Array.isArray(project.value.tags)) {
    return project.value.tags.filter(tag => tag);
  }

  // Si tags est une chaîne séparée par des virgules
  if (typeof project.value.tags === 'string') {
    return project.value.tags.split(',').map(tag => tag.trim()).filter(tag => tag);
  }

  return [];
});

// Computed property pour les URLs du projet
const projectUrls = computed(() => {
  if (!project.value?.urls) return [];

  // Si urls est un array (comme dans les données JSON)
  if (Array.isArray(project.value.urls)) {
    return project.value.urls.filter(url => url);
  }

  // Si urls est une chaîne séparée par des virgules
  if (typeof project.value.urls === 'string') {
    return project.value.urls.split(',').map(url => url.trim()).filter(url => url);
  }

  return [];
});
</script>

<style scoped>
.project-detail {
  max-width: 1200px;
  width: 100%;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-background-soft);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.header {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}
.home-btn {
  background: none;
  border: none;
  cursor: pointer;
  margin-right: 1rem;
  color: var(--color-text);
}
.field {
  margin-bottom: 0.5rem;
}
.url-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}
.url-btn:hover {
  text-decoration: none;
}
.photo-gallery {
  margin-bottom: 1.5rem;
}
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.5rem;
}
.photo-item {
  cursor: pointer;
  overflow: hidden;
  border-radius: 8px;
  transition: transform 0.2s;
}
.photo-item:hover {
  transform: scale(1.05);
}
.photo-thumbnail {
  width: 100%;
  height: auto;
  display: block;
}
.tags-section {
  margin-bottom: 1.5rem;
}
.tag-cloud-badge {
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
}
.dark-tag {
  background-color: #333;
  color: #fff;
}
.urls-section {
  margin-top: 2rem;
}

.urls-section h3 {
  color: var(--color-heading);
}
.url-list {
  list-style: none;
  padding: 0;
}
.url-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}
.url-title {
  font-weight: 500;
  color: var(--color-text);
}
.url-complete {
  font-size: 0.875rem;
  color: var(--color-text);
}
.btn {
  min-width: 100px;
}
.project-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: var(--color-heading);
}

.project-description {
  font-size: 1rem;
  color: var(--color-text);
  margin-bottom: 1.5rem;
}
.company-link-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: var(--color-background);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  color: white;
}
.company-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.company-details {
  flex: 1;
  margin-right: 1rem;
}


.url-title-btn:hover {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  text-decoration: underline;
}
</style>
