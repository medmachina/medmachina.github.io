<template>
  <div class="d-flex flex-wrap align-items-center gap-2">
    <span
      v-for="usage in usages"
      :key="usage"
      :class="['badge', isSelected(usage) ? 'bg-success' : 'dark-usage', 'usage-cloud-badge']"
      style="cursor:pointer;"
      @click="toggleUsage(usage)"
    >
      {{ usage }}
      <span v-if="isSelected(usage)" class="ms-1" style="font-size: 0.8em;">✕</span>
    </span>
    <span v-if="selectedUsages.length > 0" class="ms-2 text-danger fw-bold" style="cursor:pointer;" @click="clearAllUsages">Remove all</span>
  </div>
</template>

<script setup>
const props = defineProps({
  usages: Array,
  selectedUsages: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:selectedUsages']);

function isSelected(usage) {
  return props.selectedUsages.includes(usage);
}

function toggleUsage(usage) {
  const newSelectedUsages = [...props.selectedUsages];
  const index = newSelectedUsages.indexOf(usage);

  if (index > -1) {
    // Usage déjà sélectionné, le retirer
    newSelectedUsages.splice(index, 1);
  } else {
    // Usage pas encore sélectionné, l'ajouter
    newSelectedUsages.push(usage);
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
  font-size: 0.875rem;
}
</style>
