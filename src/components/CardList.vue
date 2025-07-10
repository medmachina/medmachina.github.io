<template>
  <div class="row g-3">
    <div v-for="item in items" :key="item.project_name" class="col-12 col-md-6 col-lg-4">
      <div class="card h-100 shadow-sm card-clickable" @click="goToDetail(item)">
        <template v-if="getFirstPhotoUrl(item)">
          <img
            :src="getFirstPhotoUrl(item)"
            alt="photo"
            class="card-img-top rounded-top"
            style="object-fit:cover; max-height:180px; border-top-left-radius:1rem; border-top-right-radius:1rem;"
            @error="handleImageError(item, $event)"
          />
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
import { ref } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    required: true
  }
});

// Garder une trace des URLs d'images invalides
const invalidImageUrls = ref(new Set());

const router = useRouter();

function goToDetail(item) {
  // On suppose que chaque item a un champ 'id' unique
  router.push(`/robot/${item.id}`);
}

function getFirstPhotoUrl(item) {
  if (!item.photoURL || !item.photoURL.length) {
    return null;
  }

  // Vérifier si la première URL est déjà connue comme invalide
  if (invalidImageUrls.value.has(item.photoURL[0])) {
    return null;
  }

  // Essayer la première URL
  return item.photoURL[0];
}

function handleImageError(item, event) {
  const url = event.target.src;
  console.warn(`Image non disponible pour ${item.project_name}: ${url}`);

  // Marquer cette URL comme invalide
  invalidImageUrls.value.add(url);

  // Essayer la prochaine URL d'image si disponible
  if (item.photoURL && item.photoURL.length > 1) {
    const currentIndex = item.photoURL.indexOf(url);
    if (currentIndex >= 0 && currentIndex + 1 < item.photoURL.length) {
      // Essayer l'URL suivante qui n'est pas déjà connue comme invalide
      for (let i = currentIndex + 1; i < item.photoURL.length; i++) {
        if (!invalidImageUrls.value.has(item.photoURL[i])) {
          event.target.src = item.photoURL[i];
          return;
        }
      }
    }
  }

  // Si aucune URL valide n'est trouvée, cacher l'image
  event.target.style.display = 'none';
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
