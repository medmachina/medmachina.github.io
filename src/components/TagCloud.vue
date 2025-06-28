<template>
  <div class="d-flex flex-wrap align-items-center gap-2">
    <span
      v-for="tag in tags"
      :key="tag"
      :class="['badge', isSelected(tag) ? 'bg-primary' : 'dark-tag', 'tag-cloud-badge']"
      style="cursor:pointer;"
      @click="toggleTag(tag)"
    >
      {{ tag }}
      <span v-if="isSelected(tag)" class="ms-1" style="font-size: 0.8em;">✕</span>
    </span>
    <span v-if="selectedTags.length > 0" class="ms-2 text-danger fw-bold" style="cursor:pointer;" @click="clearAllTags">Remove all tags</span>
  </div>
</template>

<script setup>
const props = defineProps({
  tags: Array,
  selectedTags: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:selectedTags']);

function isSelected(tag) {
  return props.selectedTags.includes(tag);
}

function toggleTag(tag) {
  const newSelectedTags = [...props.selectedTags];
  const index = newSelectedTags.indexOf(tag);

  if (index > -1) {
    // Tag déjà sélectionné, le retirer
    newSelectedTags.splice(index, 1);
  } else {
    // Tag pas encore sélectionné, l'ajouter
    newSelectedTags.push(tag);
  }

  emit('update:selectedTags', newSelectedTags);
}

function clearAllTags() {
  emit('update:selectedTags', []);
}
</script>

<style scoped>
.dark-tag {
  background-color: #333;
  color: #fff;
}
.tag-cloud-badge {
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
}
</style>

<!-- Plus de style custom, tout est Bootstrap -->
