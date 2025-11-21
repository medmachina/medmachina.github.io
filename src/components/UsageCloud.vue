<template>
  <div class="d-flex flex-wrap align-items-center gap-2">
    <span
      v-for="usage in usages"
      :key="usage.name"
      :class="['badge', isSelected(usage.name) ? 'bg-success' : 'dark-usage', 'usage-cloud-badge']"
      :style="{
        cursor: 'pointer',
        fontSize: `${0.75 + (usage.count / maxUsageCount) * 0.5}rem`
      }"
      @click="toggleUsage(usage.name)"
    >
      {{ usage.name }}
      <span v-if="isSelected(usage.name)" class="ms-1" style="font-size: 0.8em;">✕</span>
    </span>
    <span v-if="selectedUsages.length > 0" class="ms-2 text-danger fw-bold" style="cursor:pointer;" @click="clearAllUsages">Remove all</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  usages: Array,
  selectedUsages: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:selectedUsages']);

// Calculate the maximum number of occurrences to normalize sizes
const maxUsageCount = computed(() => {
  if (!props.usages || props.usages.length === 0) return 1;
  return Math.max(...props.usages.map(usage => usage.count));
});

function isSelected(usageName) {
  return props.selectedUsages.includes(usageName);
}

function toggleUsage(usageName) {
  const newSelectedUsages = [...props.selectedUsages];
  const index = newSelectedUsages.indexOf(usageName);

  if (index > -1) {
    // Usage already selected, remove it
    newSelectedUsages.splice(index, 1);
  } else {
    // Usage not yet selected, add it
    newSelectedUsages.push(usageName);
  }

  emit('update:selectedUsages', newSelectedUsages);
}

function clearAllUsages() {
  emit('update:selectedUsages', []);
}
</script>

<style scoped>
.dark-usage {
  background-color: #1a5928;
  color: #fff;
}
.usage-cloud-badge {
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  transition: all 0.2s ease;
}
.usage-cloud-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>
