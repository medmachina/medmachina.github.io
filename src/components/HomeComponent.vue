<script setup>
import { ref, computed, onMounted } from 'vue'
import RobotList from './RobotList.vue'
import TagCloud from './TagCloud.vue'
import UsageCloud from './UsageCloud.vue'
import RegulatoryStatusCloud from './RegulatoryStatusCloud.vue'

const items = ref([])
const companies = ref([])
const search = ref('')
const selectedTags = ref([])
const selectedUsages = ref([])
const selectedStatuses = ref([])
const sortMode = ref('random') // 'random' or 'alphabetical'

onMounted(async () => {
  const response = await fetch('/robots.json')
  const robots = await response.json()
  // Randomiser l'ordre des robots avec l'algorithme de Fisher-Yates
  items.value = shuffleArray(robots)

  // Charger les données des entreprises pour transmettre à RobotList
  try {
    const resCompanies = await fetch('/companies.json')
    companies.value = await resCompanies.json()
  } catch (err) {
    console.error('Failed to load companies.json', err)
  }
})

// Fonction pour mélanger un tableau (algorithme de Fisher-Yates)
function shuffleArray(array) {
  const newArray = [...array] // Copie du tableau pour ne pas modifier l'original
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]] // Échange des éléments
  }
  return newArray
}

function sortAlphabetically() {
  sortMode.value = 'alphabetical'
  items.value = [...items.value].sort((a, b) => a.name.localeCompare(b.name))
}

function sortRandomly() {
  sortMode.value = 'random'
  items.value = shuffleArray(items.value)
}

const allTags = computed(() => {
  // Compter la fréquence de chaque tag
  const tagCount = {}
  items.value.forEach(item => {
    (item.tags || []).forEach(tag => {
      tagCount[tag] = (tagCount[tag] || 0) + 1
    })
  })

  // Convertir en tableau d'objets avec le tag et sa fréquence
  return Object.keys(tagCount)
    .map(tag => ({ name: tag, count: tagCount[tag] }))
    .sort((a, b) => b.count - a.count) // Trier par fréquence décroissante
})

const allUsages = computed(() => {
  // Compter la fréquence de chaque usage
  const usageCount = {}
  items.value.forEach(item => {
    (item.usages || []).forEach(usage => {
      usageCount[usage] = (usageCount[usage] || 0) + 1
    })
  })

  // Convertir en tableau d'objets avec l'usage et sa fréquence
  return Object.keys(usageCount)
    .map(usage => ({ name: usage, count: usageCount[usage] }))
    .sort((a, b) => b.count - a.count) // Trier par fréquence décroissante
})

const allStatuses = computed(() => {
  // Compter la fréquence de chaque statut réglementaire
  const statusCount = {}
  items.value.forEach(item => {
    (item.regulatory || []).forEach(status => {
      // Ajouter le statut original
      statusCount[status] = (statusCount[status] || 0) + 1

      // Si le statut commence par FDA ou CE, on le divise
      if (status.startsWith('FDA') || status.startsWith('CE')) {
        // Extraire le préfixe (FDA ou CE)
        const prefix = status.startsWith('FDA') ? 'FDA' : 'CE'
        statusCount[prefix] = (statusCount[prefix] || 0) + 1

        // Extraire l'année ou le reste (ce qui suit FDA ou CE)
        const remainder = status.substring(prefix.length).trim()
        if (remainder) {
          statusCount[remainder] = (statusCount[remainder] || 0) + 1
        }
      }
    })
  })

  // Convertir en tableau d'objets avec le statut et sa fréquence
  return Object.keys(statusCount)
    .map(status => ({ name: status, count: statusCount[status] }))
    .sort((a, b) => b.count - a.count) // Trier par fréquence décroissante
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    // Si aucun terme de recherche, ou aucun tag/usage/statut sélectionné, on retourne tous les éléments
    if (!search.value &&
        selectedTags.value.length === 0 &&
        selectedUsages.value.length === 0 &&
        selectedStatuses.value.length === 0) return true;

    // Fonction qui vérifie si un terme de recherche est présent dans une valeur
    const checkValue = (value, term) => {
      if (!value) return false;

      // Cas des tableaux (urls, tags, photo_urls, etc.)
      if (Array.isArray(value)) {
        return value.some(val => checkValue(val, term));
      }

      // Cas des objets
      if (typeof value === 'object') {
        return Object.values(value).some(val => checkValue(val, term));
      }

      // Cas des strings ou valeurs convertibles en string
      return String(value).toLowerCase().includes(term.toLowerCase());
    };

    // Vérification si le terme de recherche est présent dans n'importe quel champ
    const matchSearch = !search.value ||
      Object.values(item).some(value => checkValue(value, search.value));

    const matchTags = selectedTags.value.length === 0 ||
      selectedTags.value.every(selectedTag => (item.tags || []).includes(selectedTag));

    const matchUsages = selectedUsages.value.length === 0 ||
      selectedUsages.value.every(selectedUsage => (item.usages || []).includes(selectedUsage));

    // Modification pour le filtrage par statut réglementaire
    const matchStatuses = selectedStatuses.value.length === 0 ||
      selectedStatuses.value.every(selectedStatus => {
        // Vérifier si le statut exact existe dans le tableau des statuts réglementaires
        if ((item.regulatory || []).includes(selectedStatus)) {
          return true;
        }

        // Vérifier si le statut est une partie d'un statut plus long (FDA dans FDA 2023, ou 2023 dans FDA 2023)
        return (item.regulatory || []).some(status => status.includes(selectedStatus));
      });

    return matchSearch && matchTags && matchUsages && matchStatuses;
  });
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
