<template>
  <div class="row g-3">
    <div v-for="item in items" :key="item.project_name" class="col-12 col-md-6 col-lg-4">
      <div class="card h-100 shadow-sm card-clickable" @click="goToDetail(item)">
        <template v-if="item.photoURL">
          <img :src="item.photoURL" alt="photo" class="card-img-top rounded-top" style="object-fit:cover; max-height:180px; border-top-left-radius:1rem; border-top-right-radius:1rem;" />
        </template>
        <div class="card-body">
          <h5 class="card-title">{{ item.project_name }}</h5>
          <p class="card-text">{{ item.description }}</p>
          <div class="mb-2">
            <span v-for="tag in item.tags" :key="tag" class="badge bg-secondary me-1">{{ tag }}</span>
          </div>
          <div v-if="item.urls && item.urls.length" class="mb-2">
            <a v-for="(url, idx) in item.urls" :key="url" :href="url" target="_blank" class="btn btn-primary btn-sm me-1" @click.stop>{{ item.urls.length > 1 ? 'Lien ' + (idx + 1) : 'Lien' }}</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const props = defineProps({
  items: {
    type: Array,
    required: true
  }
});
const router = useRouter();
function goToDetail(item) {
  // On suppose que chaque item a un champ 'id' unique
  router.push(`/robot/${item.id}`);
}
</script>

<style scoped>
.card-clickable {
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.card-clickable:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
</style>
