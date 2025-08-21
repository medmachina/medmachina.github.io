<template>
  <div class="row g-3">
    <div v-for="company in companies" :key="company.name" class="col-12 col-md-6 col-lg-4">
      <div class="card h-100 shadow-sm card-clickable" @click="goToDetail(company)">
        <div class="card-body">
          <h5 class="card-title">{{ company.name }}</h5>
          <h6 class="card-subtitle mb-2">{{ company.country }}</h6>
          <div class="mb-2" v-if="company.robots && company.robots.length">
<!--            <span class="badge bg-info me-1">{{ company.robots.length }} robots</span>-->
            <span v-for="robotId in company.robots" :key="robotId" class="badge bg-secondary me-1 robot-link robot-badge-ellipsis" @click.stop="goToRobot(robotId)" :title="getRobotName(robotId)">
              {{ getRobotName(robotId) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';

const props = defineProps({
  companies: {
    type: Array,
    required: true
  }
});

const router = useRouter();
const robotsData = ref([]);

onMounted(async () => {
  try {
    const response = await fetch('/robots.json');
    if (response.ok) {
      robotsData.value = await response.json();
    } else {
      console.error('Failed to fetch robots data');
    }
  } catch (error) {
    console.error('Error fetching robots data:', error);
  }
});

function getRobotName(robotId) {
  const robot = robotsData.value.find(r => r.id === robotId);
  return robot ? robot.name : robotId;
}

function goToDetail(company) {
  router.push(`/company/${company.name}`);
}

function goToRobot(robotId) {
  router.push(`/robot/${robotId}`);
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
.card-subtitle {
  color: var(--color-text-light, #aaa);
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
.robot-link {
  cursor: pointer;
  transition: background-color 0.2s;
  max-width: 200px;
  display: inline-block;
}
.robot-badge-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.robot-link:hover {
  background-color: var(--color-primary);
}
</style>
