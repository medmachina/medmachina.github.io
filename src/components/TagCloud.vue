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
      :title="getTagDescription(tag.name)"
    >
      {{ tag.name }}
      <span v-if="isSelected(tag.name)" class="ms-1" style="font-size: 0.8em;">✕</span>
    </span>
    <span v-if="selectedTags.length > 0" class="ms-2 text-danger fw-bold" style="cursor:pointer;" @click="clearAllTags">Remove all tags</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// Tag descriptions from robots.schema.json
const tagDescriptions = {
  "RAMIS": "Robot-assisted minimally invasive surgery systems.",
  "Commercial": "Available as a marketed, regulatory-cleared product.",
  "Teleoperated": "Surgeon controls instruments remotely via master console.",
  "Multiple ports": "Uses several trocar access points into the patient.",
  "3+ instruments": "Supports at least three concurrently mountable instruments.",
  "Stereo endoscope": "Provides stereoscopic intraoperative imaging.",
  "Mechanical Cartesian manipulation": "Arm kinematics primarily based on Cartesian/linkage design.",
  "Stereo viewer": "Dedicated binocular display for depth perception.",
  "Single patient cart": "All arms mounted on one mobile patient-side base.",
  "Haptic": "Provides tactile or force cues to the operator, doesn't assume full force feedback.",
  "Wristed instruments": "End effector instruments include distal articulation (wrist).",
  "Open surgery": "Intended for non-endoscopic (open) surgical approaches.",
  "Mechanical RCM": "Hardware geometry enforces a remote center of motion pivot.",
  "Retired": "No longer produced or clinically supported.",
  "Orthopedic": "Focused on bone and joint related procedures.",
  "Multiple patient carts": "System separates arms across multiple bases.",
  "Stereo display": "Stereoscopic display (flat screen).",
  "Haptic device": "Provides an haptic interface.",
  "Motorized table": "Includes integrated powered patient positioning table.",
  "Single port": "Access via one incision using multi-channel port.",
  "2 instruments": "Supports a maximum of two concurrent instruments.",
  "Collaborative control": "Shares task execution between human and automation.",
  "Force feedback": "Returns quantitative force/torque data to operator.",
  "Mono endoscope": "Monocular endoscopic imaging only.",
  "Mechanical manipulation": "User input is captured mechanically, with or without actuation.",
  "Open console": "Operator interface without enclosed immersive hood.",
  "Research system": "Primarily for laboratory or academic research use.",
  "Software RCM": "Remote center of motion enforced algorithmically, not by hardware.",
  "Semi-autonomous": "Performs subtasks automatically with human supervision.",
  "Open source": "Provides source code openly for modification.",
  "Open architecture": "Designed for extensibility via documented interfaces.",
  "Free hand manipulation": "User input is captured wirelessly or without mechanical linkage.  Doesn't support haptic feedback.",
  "Autonomous": "Capable of executing tasks without direct real-time human input.",
  "Simulation": "Used chiefly for training or procedural rehearsal.",
  "Flexible robot": "Employs flexible continuum or snake-like mechanisms.",
  "Open microsurgery": "Designed for delicate open microsurgical procedures.",
  "Biopsy": "Supports tissue sampling guidance or extraction.",
  "TRUS": "Transrectal ultrasound guidance or manipulation.",
  "Dental": "Focused on dental or oral implant procedures.",
  "Autonomous motion": "Capable of moving independently without human control."
};

function getTagDescription(tagName) {
  return tagDescriptions[tagName] || '';
}

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
