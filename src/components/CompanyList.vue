<template>
  <div class="row g-3">
    <div v-for="company in companies" :key="company.name" class="col-12 col-md-6 col-lg-4">
      <div class="card h-100 shadow-sm card-clickable" @click="goToDetail(company)">
        <div class="card-body">
          <h5 class="card-title">{{ company.name }}</h5>
          <h6 class="card-subtitle mb-2 text-muted">{{ company.country }}</h6>
          <p class="card-text text-ellipsis">{{ company.description }}</p>
          <div class="mb-2" v-if="company.robots && company.robots.length">
            <span class="badge bg-info me-1">{{ company.robots.length }} robots</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const props = defineProps({
  companies: {
    type: Array,
    required: true
  }
});

const router = useRouter();

function goToDetail(company) {
  router.push(`/company/${company.name}`);
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
.card-subtitle {
  color: var(--color-text-light, #aaa);
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
