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

    <!-- Edit on GitHub Section -->
    <div v-if="project" class="edit-section mt-4">
      <a 
        :href="`https://github.com/medmachina/medmachina.github.io/edit/main/public/robots.json`" 
        target="_blank" 
        rel="noopener noreferrer"
        class="btn btn-outline-secondary"
        title="Edit this robot on GitHub"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 4px;">
          <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
        </svg>
        Edit on GitHub
      </a>
    </div>

    <div v-if="!project">
      <p>Project not found.</p>
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
const invalidPhotoUrls = ref(new Set()); // Set to store invalid image URLs

onMounted(async () => {
  // Load robots data
  const resRobots = await fetch('/robots.json');
  const dataRobots = await resRobots.json();
  project.value = dataRobots.find(p => String(p.id) === route.params.id);

  // Load companies data
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
  console.warn('Image not available:', photo.url);

  // Add URL to the list of invalid URLs
  invalidPhotoUrls.value.add(photo.url);
}

// Computed property to find the company associated with the robot
const companyInfo = computed(() => {
  if (!project.value || !companies.value.length) return null;

  return companies.value.find(company =>
    company.robots && company.robots.includes(project.value.id)
  );
});

function goToCompany(companyName) {
  router.push(`/company/${companyName}`);
}

// Computed properties to extract photos and filter the project
const photoUrls = computed(() => {
  if (!project.value?.photos) return [];

  // If photos is an array of photo objects
  if (Array.isArray(project.value.photos)) {
    return project.value.photos.filter(photo => photo && photo.url);
  }

  return [];
});

// Filter valid photo URLs (those that are not broken)
const validPhotoUrls = computed(() => {
  return photoUrls.value.filter(photo => {
    // Check if the image URL is valid and not in the list of invalid URLs
    return isUrl(photo.url) && !invalidPhotoUrls.value.has(photo.url);
  });
});

const filteredProject = computed(() => {
  if (!project.value) return {};

  const filtered = { ...project.value };
  delete filtered.photo_urls; // Remove photo_urls as displayed separately
  delete filtered.tags; // Remove tags as displayed separately
  delete filtered.urls; // Remove urls as displayed separately
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

// Computed property for project tags
const projectTags = computed(() => {
  if (!project.value?.tags) return [];

  // If tags is an array (as in JSON data)
  if (Array.isArray(project.value.tags)) {
    return project.value.tags.filter(tag => tag);
  }

  // If tags is a comma-separated string
  if (typeof project.value.tags === 'string') {
    return project.value.tags.split(',').map(tag => tag.trim()).filter(tag => tag);
  }

  return [];
});

// Computed property for project URLs
const projectUrls = computed(() => {
  if (!project.value?.urls) return [];

  // If urls is an array (as in JSON data)
  if (Array.isArray(project.value.urls)) {
    return project.value.urls.filter(url => url);
  }

  // If urls is a comma-separated string
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
