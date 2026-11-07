<template>
  <div class="d-flex flex-wrap align-items-center gap-2">
    <span
      v-for="cat in categories"
      :key="cat.name"
      :class="['badge', isSelected(cat.name) ? 'bg-primary' : 'dark-category', 'category-cloud-badge']"
      :style="{
        cursor: 'pointer',
        fontSize: `${0.75 + (cat.count / maxCategoryCount) * 0.2}rem`
      }"
      @click="toggleCategory(cat.name)"
      :title="`${getCategoryDescription(cat.name)} (${cat.count})`"
    >
      {{ cat.name }}
      <span v-if="isSelected(cat.name)" class="ms-1" style="font-size: 0.8em;">✕</span>
    </span>
    <span
      v-if="selectedCategories.length > 0"
      class="ms-2 text-danger fw-bold"
      style="cursor:pointer;"
      @click="clearAllCategories"
    >Remove all</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { getCategoryDescription } from '../utils/tagDescriptions.js';

const props = defineProps({
  categories: Array,
  selectedCategories: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:selectedCategories']);

const maxCategoryCount = computed(() => {
  if (!props.categories || props.categories.length === 0) return 1;
  return Math.max(...props.categories.map(cat => cat.count));
});

function isSelected(catName) {
  return props.selectedCategories.includes(catName);
}

function toggleCategory(catName) {
  const updated = [...props.selectedCategories];
  const index = updated.indexOf(catName);
  if (index > -1) {
    updated.splice(index, 1);
  } else {
    updated.push(catName);
  }
  emit('update:selectedCategories', updated);
}

function clearAllCategories() {
  emit('update:selectedCategories', []);
}
</script>

<style scoped>
.dark-category {
  background-color: #4c3575;
  color: #fff;
}
.category-cloud-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 1rem;
  transition: all 0.2s ease;
}
.category-cloud-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>

