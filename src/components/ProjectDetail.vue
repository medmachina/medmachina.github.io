<template>
  <div class="project-detail">
    <button class="home-btn" @click="goHome" title="Accueil">
      <svg width="24" height="24" viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
    </button>
    <h1>{{ project?.name }}</h1>
    <div v-if="project">
      <div v-for="(value, key) in project" :key="key" class="field">
        <strong>{{ key }}:</strong> {{ value }}
      </div>
    </div>
    <div v-else>
      <p>Projet introuvable.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const project = ref(null);

onMounted(async () => {
  console.log("Fetching project data for ID:", route.params.id);
  const res = await fetch('/data.json');
  const data = await res.json();
  project.value = data.find(p => String(p.id) === route.params.id);
});

function goHome() {
  router.push('/');
}
</script>

<style scoped>
.project-detail {
  max-width: 600px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.home-btn {
  background: none;
  border: none;
  cursor: pointer;
  margin-bottom: 1rem;
}
.field {
  margin-bottom: 0.5rem;
}
</style>

