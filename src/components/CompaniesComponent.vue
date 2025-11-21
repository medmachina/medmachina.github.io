<template>
  <div>
    <header class="d-flex align-items-center justify-content-between p-3 mb-4 border-bottom">
      <div class="d-flex align-items-center">
        <h1 class="mb-0 me-4">Companies</h1>
        <router-link to="/" class="btn btn-outline-primary">Robots</router-link>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CompanyList from './CompanyList.vue'

const companies = ref([])
const search = ref('')
const selectedCountries = ref([])
const sortMode = ref('random') // 'random' or 'alphabetical'

onMounted(async () => {
  const response = await fetch('/companies.json')
  const data = await response.json()
  // Randomize companies order on load
  companies.value = shuffleArray(data)
})

// Fisher-Yates shuffle used to randomize order
function shuffleArray(array) {
  const newArray = [...array]
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]]
  }
  return newArray
}

function sortAlphabetically() {
  sortMode.value = 'alphabetical'
  companies.value = [...companies.value].sort((a, b) => {
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
  companies.value = shuffleArray(companies.value)
}

const allCountries = computed(() => {
  const countries = new Set()
  companies.value.forEach(company => {
    if (company.country) {
      countries.add(company.country)
    }
  })

  // Transformer le Set en tableau et trier par nombre d'entreprises (ordre décroissant)
  return Array.from(countries)
    .sort((a, b) => {
      const countA = countCompaniesByCountry(a);
      const countB = countCompaniesByCountry(b);
      return countB - countA; // Tri décroissant (du plus grand au plus petit)
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
    // Fonction récursive pour rechercher dans tous les champs
    const checkValue = (value, term) => {
      if (!value) return false

      // Pour les tableaux
      if (Array.isArray(value)) {
        return value.some(val => checkValue(val, term))
      }

      // Pour les objets
      if (typeof value === 'object') {
        return Object.values(value).some(val => checkValue(val, term))
      }

      // Pour les autres valeurs
      return String(value).toLowerCase().includes(term.toLowerCase())
    }

    // Vérifier si la recherche correspond
    const matchSearch = !search.value ||
      Object.values(company).some(value => checkValue(value, search.value))

    // Vérifier si le pays correspond aux filtres sélectionnés
    const matchCountry = selectedCountries.value.length === 0 ||
      selectedCountries.value.includes(company.country)

    return matchSearch && matchCountry
  })
})
</script>

<style scoped>
@import 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css';

/* Dark theme overrides */
header {
  border-color: var(--color-border) !important;
}

h1, h2 {
  color: var(--color-heading) !important;
}

.form-control {
  background-color: var(--color-background-soft);
  border-color: var(--color-border);
  color: var(--color-text);
}

.form-control:focus {
  background-color: var(--color-background-soft);
  border-color: var(--color-border-hover);
  color: var(--color-text);
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.1);
}

.form-control::placeholder {
  color: var(--color-text);
  opacity: 0.6;
}

.list-group-item {
  background-color: var(--color-background-soft);
  border-color: var(--color-border);
  color: var(--color-text);
}

.list-group-item.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}
</style>
