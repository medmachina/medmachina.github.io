<template>
  <div v-if="showModal" class="modal-overlay">
    <div class="modal-content">
      <h2 class="modal-title">Disclaimer</h2>
      <div class="modal-body">
        <p>The information provided by Med Machina is made available for general information purposes only.</p>
        <p>While we strive to keep the information up-to-date and correct, we make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability of the information.</p>
        <p>Through this website, you can access other websites via links. We have no control over the nature, content, and availability of those sites, and the inclusion of any links does not necessarily imply a recommendation or endorsement of the views expressed within them.</p>
      </div>
      <div class="modal-footer">
        <button @click="acceptDisclaimer" class="btn btn-primary">I understand</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const showModal = ref(false);

onMounted(() => {
  const hasSeenDisclaimer = localStorage.getItem('hasSeenDisclaimer');
  if (!hasSeenDisclaimer) {
    showModal.value = true;
  }
});

function acceptDisclaimer() {
  localStorage.setItem('hasSeenDisclaimer', 'true');
  showModal.value = false;
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  padding: 2rem;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-title {
  color: var(--color-heading);
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.modal-body {
  margin-bottom: 1.5rem;
}

.modal-body p {
  margin-bottom: 1rem;
  line-height: 1.5;
  color: var(--color-text);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}

.btn-primary {
  background-color: var(--color-primary, #3490dc);
  border-color: var(--color-primary, #3490dc);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark, #0056b3);
  border-color: var(--color-primary-dark, #0056b3);
  opacity: 0.9;
}
</style>
