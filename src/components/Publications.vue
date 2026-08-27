<template>
  <div>
    <header class="d-flex align-items-center justify-content-between px-0 py-2 mb-3 border-bottom">
      <div class="d-flex align-items-center">
        <h1 class="mb-0 me-4">Publications</h1>
        <router-link to="/" class="btn btn-outline-primary me-2">Robots</router-link>
        <router-link to="/companies" class="btn btn-outline-primary">Companies</router-link>
      </div>
      <router-link to="/" style="display: flex; align-items: center; text-decoration: none;">
        <img src="/text-logo.svg" alt="medmachina logo" class="global-logo" />
      </router-link>
    </header>

    <main class="container-fluid pt-2 pb-4">
      <p class="text-muted mb-3">
        Articles covering the field of medical and surgical robotics.
      </p>

      <!-- Search & Filter Controls -->
      <div class="d-flex align-items-center mb-4">
        <input
          v-model="searchQuery"
          type="text"
          class="form-control me-2"
          placeholder="Search by title, journal, keyword, or system name..."
        />
        <button
          class="btn me-2"
          :class="sortBy === 'citations' ? 'btn-primary' : 'btn-outline-secondary'"
          @click="sortBy = 'citations'"
          style="white-space: nowrap;"
        >
          Most Cited
        </button>
        <button
          class="btn"
          :class="sortBy === 'year' ? 'btn-primary' : 'btn-outline-secondary'"
          @click="sortBy = 'year'"
          style="white-space: nowrap;"
        >
          Newest First
        </button>
      </div>

    <!-- Publications List -->
    <div v-if="filteredPublications.length === 0" class="card p-4 text-center text-muted">
      No publications found matching your search.
    </div>

    <div v-for="(pub, idx) in filteredPublications" :key="idx" class="card mb-3 pub-card">
      <div class="card-body">
        <!-- Title -->
        <h2 class="h5 card-title mb-2">
          <a :href="pub.url" target="_blank" rel="noopener noreferrer" class="text-decoration-none pub-title-link">
            {{ pub.title }}
          </a>
        </h2>

        <!-- Metadata Bar (Journal, Year, Citations, Robot Tag, DOI, PMID) -->
        <div class="d-flex flex-wrap align-items-center gap-2 mb-3 small">
          <!-- Journal -->
          <span v-if="pub.journal" class="fw-semibold text-light-emphasis">
            <em>{{ pub.journal }}</em>
          </span>

          <!-- Year Badge -->
          <span v-if="pub.year" class="badge bg-secondary">
            {{ pub.year }}
          </span>

          <!-- Citations Badge -->
          <span v-if="pub.citations" class="badge bg-success">
            {{ pub.citations.toLocaleString() }} citations
          </span>

          <!-- External Links -->
          <span v-if="pub.doi" class="text-muted ms-1">
            • DOI: <a :href="`https://doi.org/${pub.doi}`" target="_blank" rel="noopener" class="text-muted text-decoration-underline">{{ pub.doi }}</a>
          </span>
          <span v-if="pub.pmid" class="text-muted ms-1">
            • PMID: <a :href="`https://pubmed.ncbi.nlm.nih.gov/${pub.pmid}/`" target="_blank" rel="noopener" class="text-muted text-decoration-underline">{{ pub.pmid }}</a>
          </span>
        </div>

        <!-- Abstract Box -->
        <div v-if="pub.abstract" class="abstract-box p-3 rounded">
          <p class="card-text text-secondary small mb-0">
            {{ pub.abstract }}
          </p>
        </div>
      </div>
    </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const publications = ref([]);
const searchQuery = ref('');
const sortBy = ref('citations'); // 'citations' or 'year'

onMounted(async () => {
  try {
    const res = await fetch('/publications.json');
    if (res.ok) {
      publications.value = await res.json();
    }
  } catch (e) {
    console.error('Error fetching publications.json:', e);
  }
});

const filteredPublications = computed(() => {
  let list = publications.value.filter(pub => {
    if (!searchQuery.value.trim()) return true;
    const q = searchQuery.value.toLowerCase().trim();
    const titleMatch = pub.title?.toLowerCase().includes(q);
    const journalMatch = pub.journal?.toLowerCase().includes(q);
    const abstractMatch = pub.abstract?.toLowerCase().includes(q);
    return titleMatch || journalMatch || abstractMatch;
  });

  return list.sort((a, b) => {
    if (sortBy.value === 'citations') {
      return (b.citations || 0) - (a.citations || 0);
    } else {
      return (b.year || 0) - (a.year || 0);
    }
  });
});
</script>

<style scoped>
.title {
  color: #fff;
}
.pub-card {
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 8px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.pub-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.pub-title-link {
  color: #4da3ff;
}
.pub-title-link:hover {
  text-decoration: underline !important;
}
.abstract-box {
  background-color: var(--color-background-mute, rgba(255, 255, 255, 0.03));
  border-left: 3px solid var(--color-primary, #4da3ff);
}
.abstract-text {
  line-height: 1.5;
}
</style>
