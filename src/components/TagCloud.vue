<template>
  <div class="d-flex flex-wrap align-items-center gap-2">
    <span
      v-for="tag in tags"
      :key="tag.name"
      :class="['badge', isSelected(tag.name) ? 'bg-primary' : 'dark-tag', 'tag-cloud-badge']"
      :style="{
        cursor: 'pointer',
        fontSize: `${0.75 + (tag.count / maxTagCount) * 0.5}rem`
      }"
      @click="toggleTag(tag.name)"
    >
      {{ tag.name }}
      <span v-if="isSelected(tag.name)" class="ms-1" style="font-size: 0.8em;">✕</span>
    </span>
    <span v-if="selectedTags.length > 0" class="ms-2 text-danger fw-bold" style="cursor:pointer;" @click="clearAllTags">Remove all tags</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  tags: Array,
  selectedTags: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:selectedTags']);

// Calculate the maximum number of occurrences to normalize sizes
const maxTagCount = computed(() => {
  if (!props.tags || props.tags.length === 0) return 1;
  return Math.max(...props.tags.map(tag => tag.count));
});

function isSelected(tagName) {
  return props.selectedTags.includes(tagName);
}

function toggleTag(tagName) {
  const newSelectedTags = [...props.selectedTags];
  const index = newSelectedTags.indexOf(tagName);

  if (index > -1) {
    // Tag already selected, remove it
    newSelectedTags.splice(index, 1);
  } else {
    // Tag not yet selected, add it
    newSelectedTags.push(tagName);
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
  transition: all 0.2s ease;
}
.tag-cloud-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>

<!-- No more custom styles, everything uses Bootstrap -->
