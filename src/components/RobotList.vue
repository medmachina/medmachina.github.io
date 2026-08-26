<template>
  <div class="row g-3">
    <div v-for="item in items" :key="item.id" class="col-12 col-md-6 col-lg-4">
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
            <span v-for="(tag, idx) in (item.tags || []).slice(0,5)" :key="tag" class="badge bg-secondary me-1" :title="getTagDescription(tag)">{{ tag }}</span>
            <span v-if="(item.tags || []).length > 5">...</span>
            <span v-for="(usage, idx) in (item.usages || [])" :key="usage" class="badge bg-success me-1" :title="getUsageDescription(usage)">{{ usage }}</span>
            <!-- Regulatory bodies (show body and year) -->
            <template v-for="reg in getUniqueRegulatory(item)" :key="'reg-'+reg.body">
              <span
                class="badge bg-info text-dark ms-1"
                v-if="reg.body"
              >{{ reg.body }}</span>
            </template>
            <!-- Units Deployed Badge -->
            <span
              v-if="getUnitsDeployed(item.id)"
              class="badge bg-primary ms-1"
              :title="getUnitsDeployedTooltip(item.id)"
            >{{ getUnitsDeployed(item.id).category }}</span>
            <!-- NEW badge for recently added robots -->
            <span
              v-if="isRecentlyAdded(item)"
              class="badge ms-1"
              style="background-color: #e8650a;"
              title="Recently added to the database"
            >★ NEW</span>
          </div>
<!-- ...existing template code... -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { getTagDescription, getUsageDescription } from '../utils/tagDescriptions.js';

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  companies: {
    type: Array,
    default: () => []
  },
  regulatoryData: {
    type: Object,
    default: () => ({})
  },
  unitsDeployedData: {
    type: Object,
    default: () => ({})
  }
});

const invalidImageUrls = ref(new Set());
const router = useRouter();

function goToDetail(item) {
  router.push(`/robot/${item.id}`);
}

function getFirstPhotoUrl(item) {
  if (!item.photos || !item.photos.length) {
    return null;
  }
  if (invalidImageUrls.value.has(item.photos[0].url)) {
    return null;
  }
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


function getUniqueRegulatory(item) {
  const regulatory = (typeof item === 'object' ? item?.regulatory : props.regulatoryData[item]) || props.regulatoryData[item?.id] || [];
  if (!regulatory) return [];
  const seen = new Set();
  return regulatory.filter(reg => {
    if (!reg.body) return false;
    if (seen.has(reg.body)) return false;
    seen.add(reg.body);
    return true;
  });
}

function getUnitsDeployed(robotId) {
  return props.unitsDeployedData?.[robotId] || null;
}

function getUnitsDeployedTooltip(robotId) {
  const data = getUnitsDeployed(robotId);
  if (!data) return '';
  if (data.count) {
    return `${data.category} (~${data.count.toLocaleString()} units deployed)`;
  }
  return `${data.category} units deployed`;
}

const SIX_MONTHS_MS = 6 * 30 * 24 * 60 * 60 * 1000;
function isRecentlyAdded(item) {
  if (!item.db_added) return false;
  const addedDate = new Date(item.db_added);
  return (Date.now() - addedDate.getTime()) < SIX_MONTHS_MS;
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
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
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
