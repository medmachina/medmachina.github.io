<template>
  <div class="row g-3">
    <div v-for="item in items" :key="item.project_name" class="col-12 col-md-6 col-lg-4">
      <div class="card h-100 shadow-sm card-clickable" @click="goToDetail(item)">
        <template v-if="getFirstPhotoUrl(item)">
          <img :src="getFirstPhotoUrl(item)" alt="photo" class="card-img-top rounded-top" style="object-fit:cover; max-height:180px; border-top-left-radius:1rem; border-top-right-radius:1rem;" />
        </template>
        <div class="card-body">
          <h5 class="card-title">{{ item.project_name }}</h5>
          <p class="card-text text-ellipsis">{{ item.description }}</p>
          <div class="mb-2">
            <span v-for="tag in item.tags" :key="tag" class="badge bg-secondary me-1">{{ tag }}</span>
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
function getFirstPhotoUrl(item) {
  return item.photoURL && item.photoURL.length > 0 ? item.photoURL[0] : null;
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
