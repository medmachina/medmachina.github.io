<template>
  <div>
    <header class="d-flex align-items-center justify-content-between px-0 py-2 mb-3 border-bottom">
      <div class="d-flex align-items-center">
        <h1 class="mb-0 me-4">Companies</h1>
        <router-link to="/" class="btn btn-outline-primary">Robots</router-link>
      </div>
      <router-link to="/" style="display: flex; align-items: center; text-decoration: none;">
        <img src="/text-logo.svg" alt="medmachina logo" class="global-logo" />
      </router-link>
    </header>

    <main class="container-fluid pt-2 pb-4">
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
          <CompanyList :companies="filteredCompanies" />
        </section>
        <aside class="col-md-3">
          <h2 class="h5 mb-3">Countries</h2>
          <ul class="list-group">
            <li
              v-for="country in allCountries"
              :key="country"
              class="list-group-item d-flex justify-content-between align-items-center"
              @click="toggleCountry(country)"
              :class="{ 'active': selectedCountries.includes(country) }"
              style="cursor: pointer"
            >
              {{ country }}
              <span class="badge bg-primary rounded-pill">
                {{ countCompaniesByCountry(country) }}
              </span>
            </li>
          </ul>
        </aside>
      </div>
    </main>

  <!-- Edit on GitHub: fixed bottom-right -->
  <a
    href="https://github.com/medmachina/medmachina.github.io/edit/main/public/companies.json"
    target="_blank"
    rel="noopener noreferrer"
    class="btn btn-outline-secondary edit-github-fixed"
    title="Edit companies on GitHub"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16" style="margin-right:4px;">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
    </svg>
    Edit on GitHub
  </a>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CompanyList from './CompanyList.vue'
import { shuffleArray } from '../utils/array.js'

const companies = ref([])
const originalCompanies = ref([])
const search = ref('')
const selectedCountries = ref([])
const sortMode = ref('random') // 'random' or 'alphabetical'

onMounted(async () => {
  const response = await fetch('/companies.json')
  const data = await response.json()
  // Store original data
  originalCompanies.value = data
  // Randomize companies order on load
  companies.value = shuffleArray(data)
})

function sortAlphabetically() {
  sortMode.value = 'alphabetical'
  companies.value = [...originalCompanies.value].sort((a, b) => {
    const nameCompare = a.name.localeCompare(b.name)
    if (nameCompare !== 0) return nameCompare
    // Use first robot id as tiebreaker if names are identical
    const aId = a.robots?.[0] || ''
    const bId = b.robots?.[0] || ''
    return aId.localeCompare(bId)
  })
}

function sortRandomly() {
  sortMode.value = 'random'
  companies.value = shuffleArray(originalCompanies.value)
}

const allCountries = computed(() => {
  const countries = new Set()
  companies.value.forEach(company => {
    if (company.country) {
      countries.add(company.country)
    }
  })

  // Transform Set to array and sort by number of companies (descending order)
  return Array.from(countries)
    .sort((a, b) => {
      const countA = countCompaniesByCountry(a);
      const countB = countCompaniesByCountry(b);
      return countB - countA; // Descending sort (largest to smallest)
    });
})

function countCompaniesByCountry(country) {
  return companies.value.filter(company => company.country === country).length
}

function toggleCountry(country) {
  const index = selectedCountries.value.indexOf(country)
  if (index === -1) {
    selectedCountries.value.push(country)
  } else {
    selectedCountries.value.splice(index, 1)
  }
}

const filteredCompanies = computed(() => {
  return companies.value.filter(company => {
    // Recursive function to search in all fields
    const checkValue = (value, term) => {
      if (!value) return false

      // For arrays
      if (Array.isArray(value)) {
        return value.some(val => checkValue(val, term))
      }

      // For objects
      if (typeof value === 'object') {
        return Object.values(value).some(val => checkValue(val, term))
      }

      // For other values
      return String(value).toLowerCase().includes(term.toLowerCase())
    }

    // Check if search matches
    const matchSearch = !search.value ||
      Object.values(company).some(value => checkValue(value, search.value))

    // Check if country matches selected filters
    const matchCountry = selectedCountries.value.length === 0 ||
      selectedCountries.value.includes(company.country)

    return matchSearch && matchCountry
  })
})
</script>

<style scoped>
</style>
