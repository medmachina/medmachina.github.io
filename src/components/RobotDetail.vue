<template>
  <div class="project-detail">
    <div class="header d-flex align-items-center justify-content-between mb-4">
      <h1 class="project-title mb-0">
        <router-link to="/" class="btn btn-outline-primary btn-lg" style="vertical-align:middle;">Robots</router-link>
        {{ filteredProject["name"] }}
        <span v-if="companyInfo" style="font-size:.85em;">(<router-link :to="`/company/${companyInfo.name}`">{{ companyInfo.name }}</router-link>)</span>
      </h1>
      <router-link to="/" style="display: flex; align-items: center; text-decoration: none; margin-left: 1rem;">
        <img src="/text-logo.svg" alt="medmachina" style="height:41px; width:auto;" />
      </router-link>
    </div>

    <div class="project-description">
      <template v-if="descriptionParagraphs.length">
        <p v-for="(para, idx) in descriptionParagraphs" :key="idx">{{ para }}</p>
      </template>
      <template v-else>
        {{ filteredProject["description"] }}
      </template>
    </div>

    <h3 class="mt-4 mb-4">Images from the web</h3>
    <!-- Photo Gallery Section -->
    <div v-if="validPhotoUrls.length > 0" class="photo-gallery">
      <div class="gallery-grid">
        <div
          v-for="(photo, index) in validPhotoUrls"
          :key="index"
          class="photo-item"
        >
          <a :href="photo.site" target="_blank" rel="noopener noreferrer" class="photo-link">
            <img
              :src="photo.url"
              :alt="`Photo ${index + 1}`"
              class="photo-thumbnail"
              @error="handleImageError(photo)"
            />
            <div class="photo-source">visit site</div>
          </a>
        </div>
      </div>
    </div>

    <h3 class="mt-4 mb-4">Tags</h3>
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

    <h3 class="mt-2">Links</h3>
    <!-- URLs Section -->
    <div v-if="projectUrls.length > 0" class="urls-section">
      <div class="url-list">
        <div v-for="(url, index) in projectUrls" :key="index" class="url-item">
          <div class="url-info">
            <a :href="url.url" target="_blank" rel="noopener noreferrer">{{ url.caption }}</a>
          </div>
        </div>
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

function openPhoto(photo) {
  window.open(photo.url, '_blank');
}

function handleImageError(photo) {
  console.warn('Image non disponible:', photo.url);

  // Ajouter l'URL à la liste des URLs invalides
  invalidPhotoUrls.value.add(photo.url);
}

// Computed property pour trouver l'entreprise associée au robot
const companyInfo = computed(() => {
  if (!project.value || !companies.value.length) return null;

  return companies.value.find(company =>
    company.robots && company.robots.includes(project.value.id)
  );
});

function goToCompany(companyName) {
  router.push(`/company/${companyName}`);
}

// Computed properties pour extraire les photos et filtrer le projet
const photoUrls = computed(() => {
  if (!project.value?.photos) return [];

  // Si photos est un array d'objets photo
  if (Array.isArray(project.value.photos)) {
    return project.value.photos.filter(photo => photo && photo.url);
  }

  return [];
});

// Filtrer les URLs des photos valides (celles qui ne sont pas cassées)
const validPhotoUrls = computed(() => {
  return photoUrls.value.filter(photo => {
    // Vérifier si l'URL de l'image est valide et n'est pas dans la liste des URLs invalides
    return isUrl(photo.url) && !invalidPhotoUrls.value.has(photo.url);
  });
});

const filteredProject = computed(() => {
  if (!project.value) return {};

  const filtered = { ...project.value };
  delete filtered.photo_urls; // Supprimer photo_urls car affiché séparément
  delete filtered.tags; // Supprimer tags car affiché séparément
  delete filtered.urls; // Supprimer urls car affiché séparément
  return filtered;
});

// Split description into paragraphs by double newlines. Keeps text escaped (no v-html).
const descriptionParagraphs = computed(() => {
  const desc = filteredProject.value?.description;
  if (!desc) return [];

  // Normalize CRLF and CR to LF
  const text = String(desc).replace(/\r\n/g, '\n').replace(/\r/g, '\n');

  // Split on two or more newlines to create paragraphs, trim each
  return text.split(/\n{2,}/).map(s => s.trim()).filter(s => s.length > 0);
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
  /* display: flex; */
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
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
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
  height: 400px;
  display: block;
  object-fit: contain;
  background-color: rgba(0, 0, 0, 0.05);
}

.photo-link {
  display: block;
  position: relative;
  text-decoration: none;
  color: inherit;
}

.photo-source {
  position: absolute;
  bottom: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  font-size: 0.8rem;
  border-top-left-radius: 4px;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
}

.photo-link:hover .photo-source {
  opacity: 1;
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

h3 {
  color: white;
}

.url-title-btn:hover {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  text-decoration: underline;
}
</style>
