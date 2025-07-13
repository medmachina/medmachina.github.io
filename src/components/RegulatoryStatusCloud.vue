<template>
  <div class="d-flex flex-wrap align-items-center gap-2">
    <span
      v-for="status in statuses"
      :key="status.name"
      :class="['badge', isSelected(status.name) ? 'bg-primary' : 'dark-status', 'status-cloud-badge']"
      :style="{
        cursor: 'pointer',
        fontSize: `${0.75 + (status.count / maxStatusCount) * 0.5}rem`
      }"
      @click="toggleStatus(status.name)"
    >
      {{ status.name }}
      <span v-if="isSelected(status.name)" class="ms-1" style="font-size: 0.8em;">✕</span>
    </span>
    <span v-if="selectedStatuses.length > 0" class="ms-2 text-danger fw-bold" style="cursor:pointer;" @click="clearAllStatuses">Remove all</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  statuses: Array,
  selectedStatuses: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:selectedStatuses']);

// Calculer le nombre maximum d'occurrences pour normaliser les tailles
const maxStatusCount = computed(() => {
  if (!props.statuses || props.statuses.length === 0) return 1;
  return Math.max(...props.statuses.map(status => status.count));
});

function isSelected(statusName) {
  return props.selectedStatuses.includes(statusName);
}

function toggleStatus(statusName) {
  const newSelectedStatuses = [...props.selectedStatuses];
  const index = newSelectedStatuses.indexOf(statusName);

  if (index > -1) {
    // Status déjà sélectionné, le retirer
    newSelectedStatuses.splice(index, 1);
  } else {
    // Status pas encore sélectionné, l'ajouter
    newSelectedStatuses.push(statusName);
  }

  emit('update:selectedStatuses', newSelectedStatuses);
}

function clearAllStatuses() {
  emit('update:selectedStatuses', []);
}
</script>

<style scoped>
.dark-status {
  background-color: #385a86;
  color: #fff;
}
.status-cloud-badge {
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  transition: all 0.2s ease;
}
.status-cloud-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>
