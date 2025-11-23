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
      :title="getUsageDescription(usage.name)"
    >
      {{ usage.name }}
      <span v-if="isSelected(usage.name)" class="ms-1" style="font-size: 0.8em;">✕</span>
    </span>
    <span v-if="selectedUsages.length > 0" class="ms-2 text-danger fw-bold" style="cursor:pointer;" @click="clearAllUsages">Remove all</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// Usage descriptions from robots.schema.json
const usageDescriptions = {
  "Abdominal": "Procedures within the abdominal cavity (e.g., general, colorectal).",
  "Urological": "Procedures involving urinary tract or male reproductive organs.",
  "Gynecological": "Procedures involving female reproductive system.",
  "Transoral": "Access through the mouth for head and neck or airway surgery.",
  "Knee": "Orthopedic interventions focused on the knee joint.",
  "Hip": "Orthopedic procedures involving the hip joint (e.g., replacement).",
  "Lung": "Pulmonary surgical or interventional procedures.",
  "Bronchoscopy": "Endoscopic examination or intervention in bronchial airways.",
  "Thoracic": "Procedures within the chest excluding the heart.",
  "Spine": "Spinal column or vertebral interventions.",
  "Eye": "Ophthalmic microsurgery or ocular interventions.",
  "Prostate": "Procedures targeting the prostate gland.",
  "Dental implant": "Placement or guidance for dental implants."
};

function getUsageDescription(usageName) {
  return usageDescriptions[usageName] || '';
}

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
