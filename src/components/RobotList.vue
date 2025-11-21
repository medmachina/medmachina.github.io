<template>
  <div>
    <div class="d-flex justify-content-end mb-2">
      <button type="button" class="btn btn-sm btn-outline-secondary d-flex align-items-center" @click.stop="toggleSortByYear">
        <span class="me-1" aria-hidden="true">
          <svg v-if="sortByYear === 1" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="18 15 12 9 6 15"></polyline>
          </svg>
          <svg v-else-if="sortByYear === -1" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
          </svg>
        </span>
        <span>{{ sortByYearLabel }}</span>
      </button>
    </div>
    <div class="row g-3">
    <div v-for="item in displayItems" :key="item.id" class="col-12 col-md-6 col-lg-4">
      <div class="card h-100 shadow-sm card-clickable" @click="goToDetail(item)">
        <template v-if="getFirstPhotoUrl(item)">
          <img
            :src="getFirstPhotoUrl(item)"
            alt="photo"
            class="card-img-top rounded-top"
            style="object-fit:cover; max-height:180px; border-top-left-radius:1rem; border-top-right-radius:1rem;"
            @error="handleImageError(item, $event)"
          />
        </template>
        <div class="card-body">
          <h5 class="card-title">
            {{ item.name }}
            <span v-if="getCompanyForItem(item)" style="font-size:0.9em; color:var(--color-text-muted);">(<router-link :to="`/company/${getCompanyForItem(item).name}`" @click.stop>{{ getCompanyForItem(item).name }}</router-link>)</span>
          </h5>
          <div class="mb-2">
              <span v-for="(tag, idx) in item.tags.slice(0,5)" :key="tag" class="badge bg-secondary me-1">{{ tag }}</span>
              <span v-if="item.tags.length > 5">...</span>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, computed } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  companies: {
    type: Array,
    default: () => []
  }
});

// Sort-by-year state: 0 = off, 1 = ascending (old->new), -1 = descending (new->old)
const sortByYear = ref(0);

function toggleSortByYear() {
  // First click: ascending (old -> new). Subsequent clicks toggle sign.
  sortByYear.value = sortByYear.value === 1 ? -1 : 1;
}

const sortByYearLabel = computed(() => {
  if (sortByYear.value === 1) return 'Year ↑';
  if (sortByYear.value === -1) return 'Year ↓';
  return 'Sort: Year';
});

const displayItems = computed(() => {
  // Always operate on a shallow copy to avoid mutating props
  const list = Array.isArray(props.items) ? props.items.slice() : [];
  if (!sortByYear.value) return list;

  // Helper: treat null/undefined introduction_year as Infinity when sorting ascending
  const val = i => {
    const y = i && (i.introduction_year ?? i.introduced_year ?? null);
    return y == null ? Infinity : Number(y);
  };

  list.sort((a, b) => {
    const ay = val(a), by = val(b);
    if (ay === by) return (a.id || '').localeCompare(b.id || '');
    return sortByYear.value === 1 ? (ay - by) : (by - ay);
  });

  return list;
});

// Keep track of invalid image URLs
const invalidImageUrls = ref(new Set());

const router = useRouter();

function goToDetail(item) {
  // Assume each item has a unique 'id' field
  router.push(`/robot/${item.id}`);
}

function getFirstPhotoUrl(item) {
  if (!item.photos || !item.photos.length) {
    return null;
  }

  // Check if the first URL is already known to be invalid
  if (invalidImageUrls.value.has(item.photos[0].url)) {
    return null;
  }

  // Try the first URL
  return item.photos[0].url;
}

function handleImageError(item, event) {
  const url = event.target.src;
  console.warn(`Image not available for ${item.name}: ${url}`);

  // Mark this URL as invalid
  invalidImageUrls.value.add(url);

  // Try the next image URL if available
  if (item.photos && item.photos.length > 1) {
    const currentIndex = item.photos.findIndex(photo => photo.url === url);
    if (currentIndex >= 0 && currentIndex + 1 < item.photos.length) {
      // Try the next URL that is not already known to be invalid
      for (let i = currentIndex + 1; i < item.photos.length; i++) {
        if (!invalidImageUrls.value.has(item.photos[i].url)) {
          event.target.src = item.photos[i].url;
          return;
        }
      }
    }
  }

  // If no valid URL is found, hide the image
  event.target.style.display = 'none';
}

function getCompanyForItem(item) {
  if (!props.companies || !props.companies.length) return null;
  return props.companies.find(c => c.robots && c.robots.includes(item.id));
}
</script>

<style scoped>
.card-clickable {
  cursor: pointer;
  transition: box-shadow 0.2s;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}
.card-clickable:hover {
  box-shadow: 0 4px 16px rgba(255,255,255,0.1);
}
.card-body {
  background-color: var(--color-background-soft);
  color: var(--color-text);
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
</style>
