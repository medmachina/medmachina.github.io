<script setup>
import { ref, computed, onMounted } from 'vue'
import RobotList from './RobotList.vue'
import TagCloud from './TagCloud.vue'
import UsageCloud from './UsageCloud.vue'
import RegulatoryStatusCloud from './RegulatoryStatusCloud.vue'
import { shuffleArray } from '../utils/array.js'

const items = ref([])
const originalItems = ref([])
const companies = ref([])
const search = ref('')
const selectedTags = ref([])
const selectedUsages = ref([])
const selectedStatuses = ref([])
const sortMode = ref('random') // 'random' or 'alphabetical'

onMounted(async () => {
  const response = await fetch('/robots.json')
  const robots = await response.json()
  // Store original data
  originalItems.value = robots
  // Randomize robots order using Fisher-Yates algorithm
  items.value = shuffleArray(robots)

  // Load companies data to pass to RobotList
  try {
    const resCompanies = await fetch('/companies.json')
    companies.value = await resCompanies.json()
  } catch (err) {
    console.error('Failed to load companies.json', err)
  }
})

function sortAlphabetically() {
  sortMode.value = 'alphabetical'
  items.value = [...originalItems.value].sort((a, b) => {
    const nameCompare = a.name.localeCompare(b.name)
    if (nameCompare !== 0) return nameCompare
    return a.id.localeCompare(b.id) // Use id as tiebreaker for duplicate names
  })
}

function sortRandomly() {
  sortMode.value = 'random'
  items.value = shuffleArray(originalItems.value)
}

const allTags = computed(() => {
  // Count the frequency of each tag
  const tagCount = {}
  items.value.forEach(item => {
    (item.tags || []).forEach(tag => {
      tagCount[tag] = (tagCount[tag] || 0) + 1
    })
  })

  // Convert to array of objects with tag and frequency
  return Object.keys(tagCount)
    .map(tag => ({ name: tag, count: tagCount[tag] }))
    .sort((a, b) => b.count - a.count) // Sort by descending frequency
})

const allUsages = computed(() => {
  // Count the frequency of each usage
  const usageCount = {}
  items.value.forEach(item => {
    (item.usages || []).forEach(usage => {
      usageCount[usage] = (usageCount[usage] || 0) + 1
    })
  })

  // Convert to array of objects with usage and frequency
  return Object.keys(usageCount)
    .map(usage => ({ name: usage, count: usageCount[usage] }))
    .sort((a, b) => b.count - a.count) // Sort by descending frequency
})

const allStatuses = computed(() => {
  // Count the frequency of each regulatory status
  const statusCount = {}
  items.value.forEach(item => {
    (item.regulatory || []).forEach(status => {
      // Add the original status
      statusCount[status] = (statusCount[status] || 0) + 1

      // If status starts with FDA or CE, split it
      if (status.startsWith('FDA') || status.startsWith('CE')) {
        // Extract the prefix (FDA or CE)
        const prefix = status.startsWith('FDA') ? 'FDA' : 'CE'
        statusCount[prefix] = (statusCount[prefix] || 0) + 1

        // Extract the year or remainder (what follows FDA or CE)
        const remainder = status.substring(prefix.length).trim()
        if (remainder) {
          statusCount[remainder] = (statusCount[remainder] || 0) + 1
        }
      }
    })
  })

  // Convert to array of objects with status and frequency
  return Object.keys(statusCount)
    .map(status => ({ name: status, count: statusCount[status] }))
    .sort((a, b) => b.count - a.count) // Sort by descending frequency
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    // If no search term, or no tag/usage/status selected, return all items
    if (!search.value &&
        selectedTags.value.length === 0 &&
        selectedUsages.value.length === 0 &&
        selectedStatuses.value.length === 0) return true;

    // Function that checks if a search term is present in a value
    const checkValue = (value, term) => {
      if (!value) return false;

      // Case of arrays (urls, tags, photo_urls, etc.)
      if (Array.isArray(value)) {
        return value.some(val => checkValue(val, term));
      }

      // Case of objects
      if (typeof value === 'object') {
        return Object.values(value).some(val => checkValue(val, term));
      }

      // Case of strings or values convertible to string
      return String(value).toLowerCase().includes(term.toLowerCase());
    };

    // Check if the search term is present in any field
    const matchSearch = !search.value ||
      Object.values(item).some(value => checkValue(value, search.value));

    const matchTags = selectedTags.value.length === 0 ||
      selectedTags.value.every(selectedTag => (item.tags || []).includes(selectedTag));

    const matchUsages = selectedUsages.value.length === 0 ||
      selectedUsages.value.every(selectedUsage => (item.usages || []).includes(selectedUsage));

    // Modification for regulatory status filtering
    const matchStatuses = selectedStatuses.value.length === 0 ||
      selectedStatuses.value.every(selectedStatus => {
        // Check if the exact status exists in the regulatory status array
        if ((item.regulatory || []).includes(selectedStatus)) {
          return true;
        }

        // Check if the status is part of a longer status (FDA in FDA 2023, or 2023 in FDA 2023)
        return (item.regulatory || []).some(status => status.includes(selectedStatus));
      });

    return matchSearch && matchTags && matchUsages && matchStatuses;
  });
})
</script>

<style scoped>
</style>

<template>
  <header class="d-flex align-items-center justify-content-between p-3 mb-4 border-bottom">
    <div class="d-flex align-items-center">
      <h1 class="mb-0 me-4">Robots</h1>
      <router-link to="/companies" class="btn btn-outline-primary">Companies</router-link>
    </div>
    <router-link to="/" style="display: flex; align-items: center; text-decoration: none;">
      <img src="/text-logo.svg" alt="medmachina" style="height:41px; width:auto;" />
    </router-link>
  </header>
  <main class="container-fluid py-4">
    <div class="row">
      <section class="col-md-9 mb-4">
        <div class="d-flex align-items-center mb-3">
          <input
              v-model="search"
              type="text"
              placeholder="Search ..."
              class="form-control me-2"
          />
          <button 
            @click="sortRandomly" 
            :class="['btn', sortMode === 'random' ? 'btn-primary' : 'btn-outline-secondary']"
            title="Random order"
            style="min-width: 50px;"
          >
            🎲
          </button>
          <button 
            @click="sortAlphabetically" 
            :class="['btn', 'ms-2', sortMode === 'alphabetical' ? 'btn-primary' : 'btn-outline-secondary']"
            title="Alphabetical order"
            style="min-width: 50px;"
          >
            🔤
          </button>
        </div>
  <RobotList :items="filteredItems" :companies="companies" />
      </section>
      <aside class="col-md-3">
        <h2 class="h5 mb-3">Usages</h2>
        <UsageCloud :usages="allUsages" v-model:selectedUsages="selectedUsages" />

        <h2 class="h5 mb-3 mt-5">Regulatory Status</h2>
        <RegulatoryStatusCloud :statuses="allStatuses" v-model:selectedStatuses="selectedStatuses" />

        <h2 class="h5 mb-3 mt-5">Tags</h2>
        <TagCloud :tags="allTags" v-model:selectedTags="selectedTags" />
      </aside>
    </div>
  </main>
</template>
