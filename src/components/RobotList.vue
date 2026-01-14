<template>
  <div class="row g-3">
    <div v-for="item in items" :key="item.id" class="col-12 col-md-6 col-lg-4">
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
          <h5 class="card-title">
            {{ item.name }}
            <span v-if="getCompanyForItem(item)" style="font-size:0.9em; color:var(--color-text-muted);">(<router-link :to="`/company/${getCompanyForItem(item).name}`" @click.stop>{{ getCompanyForItem(item).name }}</router-link>)</span>
          </h5>
          <div class="mb-2">
            <span v-for="(tag, idx) in (item.tags || []).slice(0,5)" :key="tag" class="badge bg-secondary me-1" :title="getTagDescription(tag)">{{ tag }}</span>
            <span v-if="(item.tags || []).length > 5">...</span>
            <span v-for="(usage, idx) in (item.usages || [])" :key="usage" class="badge bg-success me-1" :title="getUsageDescription(usage)">{{ usage }}</span>
            <!-- Regulatory bodies (show body and year) -->
            <template v-for="reg in getUniqueRegulatory(item.id)" :key="'reg-'+reg.body">
              <span
                class="badge bg-info text-dark ms-1"
                v-if="reg.body"
              >{{ reg.body }}</span>
            </template>
          </div>
<!-- ...existing template code... -->
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
  },
  companies: {
    type: Array,
    default: () => []
  },
  regulatoryData: {
    type: Object,
    default: () => ({})
  }
});

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

const invalidImageUrls = ref(new Set());
const router = useRouter();

function goToDetail(item) {
  router.push(`/robot/${item.id}`);
}

function getFirstPhotoUrl(item) {
  if (!item.photos || !item.photos.length) {
    return null;
  }
  if (invalidImageUrls.value.has(item.photos[0].url)) {
    return null;
  }
  return item.photos[0].url;
}

function handleImageError(item, event) {
  const url = event.target.src;
  console.warn(`Image not available for ${item.name}: ${url}`);

  // Mark this URL as invalid
  invalidImageUrls.value.add(url);

  // Try the next image URL if available
  if (item.photos && item.photos.length > 1) {
    const currentIndex = item.photos.findIndex(photo => photo.url === url);
    if (currentIndex >= 0 && currentIndex + 1 < item.photos.length) {
      // Try the next URL that is not already known to be invalid
      for (let i = currentIndex + 1; i < item.photos.length; i++) {
        if (!invalidImageUrls.value.has(item.photos[i].url)) {
          event.target.src = item.photos[i].url;
          return;
        }
      }
    }
  }

  // If no valid URL is found, hide the image
  event.target.style.display = 'none';
}

function getCompanyForItem(item) {
  if (!props.companies || !props.companies.length) return null;
  return props.companies.find(c => c.robots && c.robots.includes(item.id));
}

function getTagDescription(tagName) {
  return tagDescriptions[tagName] || '';
}
function getUsageDescription(usageName) {
  return usageDescriptions[usageName] || '';
}

function getUniqueRegulatory(robotId) {
  const regulatory = props.regulatoryData[robotId] || [];
  if (!regulatory) return [];
  const seen = new Set();
  return regulatory.filter(reg => {
    if (!reg.body) return false;
    if (seen.has(reg.body)) return false;
    seen.add(reg.body);
    return true;
  });
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
