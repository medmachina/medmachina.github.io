<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import RobotList from './RobotList.vue'
import TagCloud from './TagCloud.vue'
import UsageCloud from './UsageCloud.vue'
import RegulatoryStatusCloud from './RegulatoryStatusCloud.vue'
import { shuffleArray } from '../utils/array.js'


const route = useRoute()
const items = ref([])
const originalItems = ref([])
const companies = ref([])
const robotsError = ref('')
const companiesError = ref('')
const search = ref('')
const selectedTags = ref([])
const selectedUsages = ref([])
const selectedStatuses = ref([])
const sortMode = ref('random') // 'random', 'alphabetical', or 'year'
const yearSortAscending = ref(true) // true for oldest-first, false for newest-first

function updateFiltersFromQuery() {
  selectedTags.value = route.query.tag ? [route.query.tag] : []
  selectedUsages.value = route.query.usage ? [route.query.usage] : []
}

watch(() => route.query, () => {
  updateFiltersFromQuery()
})

onMounted(async () => {
  updateFiltersFromQuery()
  try {
    const response = await fetch('/robots.json')
    if (!response.ok) {
      robotsError.value = `Failed to load robots.json: ${response.status} ${response.statusText}`
      return
    }
    const robots = await response.json()
    if (!Array.isArray(robots)) {
      robotsError.value = 'robots.json did not return an array.'
      return
    }
    originalItems.value = robots
    items.value = shuffleArray(robots)
  } catch (err) {
    robotsError.value = `Error loading robots.json: ${err}`
  }

  try {
    const resCompanies = await fetch('/companies.json')
    if (!resCompanies.ok) {
      companiesError.value = `Failed to load companies.json: ${resCompanies.status} ${resCompanies.statusText}`
      return
    }
    const companiesData = await resCompanies.json()
    if (!Array.isArray(companiesData)) {
      companiesError.value = 'companies.json did not return an array.'
      return
    }
    companies.value = companiesData
  } catch (err) {
    companiesError.value = `Error loading companies.json: ${err}`
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

function sortByYear() {
  if (sortMode.value === 'year') {
    // Already in year mode, toggle the order
    yearSortAscending.value = !yearSortAscending.value
  } else {
    // Switching to year mode, default to ascending (oldest first)
    sortMode.value = 'year'
    yearSortAscending.value = true
  }
  
  items.value = [...originalItems.value].sort((a, b) => {
    // Handle null introduction_year values - push them to the end
    if (a.introduction_year === null && b.introduction_year === null) return 0
    if (a.introduction_year === null) return 1
    if (b.introduction_year === null) return -1
    // Sort by year
    const diff = a.introduction_year - b.introduction_year
    return yearSortAscending.value ? diff : -diff
  })
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
  // Extract regulatory bodies from array of objects
  const statusCount = {}
  items.value.forEach(item => {
    (item.regulatory || []).forEach(entry => {
      const body = entry.body || ''
      if (!body) return
      statusCount[body] = (statusCount[body] || 0) + 1
    })
  })
  return Object.keys(statusCount)
    .map(body => ({ name: body, count: statusCount[body] }))
    .sort((a, b) => b.count - a.count)
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    // If no tag or usage is selected, show all robots (ignore status filter)
    if (selectedTags.value.length === 0 && selectedUsages.value.length === 0 && !search.value) {
      return true;
    }

    // Improved search: match robot name, tags, usages, and company name
    const term = (search.value || '').toLowerCase().trim();
    let matchSearch = true;
    if (term) {
      // Check robot name
      matchSearch = (item.name && item.name.toLowerCase().includes(term));
      // Check tags
      matchSearch = matchSearch || (item.tags && item.tags.some(tag => tag.toLowerCase().includes(term)));
      // Check usages
      matchSearch = matchSearch || (item.usages && item.usages.some(usage => usage.toLowerCase().includes(term)));
      // Check company name
      if (companies.value && companies.value.length) {
        const company = companies.value.find(c => c.robots && c.robots.includes(item.id));
        if (company && company.name && company.name.toLowerCase().includes(term)) {
          matchSearch = true;
        }
      }
    }

    // Only show robots that have all selected tags and all selected usages
    const hasAllSelectedTags = selectedTags.value.length === 0 || selectedTags.value.every(tag => (item.tags || []).includes(tag));
    const hasAllSelectedUsages = selectedUsages.value.length === 0 || selectedUsages.value.every(usage => (item.usages || []).includes(usage));

    // Regulatory status filter only applies if tag or usage is selected
    const matchStatuses = selectedStatuses.value.length === 0 ||
      selectedStatuses.value.every(selectedStatus => {
        return (item.regulatory || []).some(entry => {
          return entry.body === selectedStatus
        })
      })

    return matchSearch && hasAllSelectedTags && hasAllSelectedUsages && matchStatuses;
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
      <!-- Logo now shown globally in App.vue header -->
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
          <button 
            @click="sortByYear" 
            :class="['btn', 'ms-2', sortMode === 'year' ? 'btn-primary' : 'btn-outline-secondary']"
            title="Sort by introduction year"
            style="min-width: 50px;"
          >
            📅
          </button>
        </div>
        <div v-if="robotsError" class="alert alert-danger my-3">{{ robotsError }}</div>
        <div v-if="companiesError" class="alert alert-danger my-3">{{ companiesError }}</div>
        <RobotList v-if="!robotsError" :items="filteredItems" :companies="companies" />
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
