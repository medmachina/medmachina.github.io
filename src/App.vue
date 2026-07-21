<template>
  <router-view />
  <DisclaimerModal />
  <footer class="footer">
    <p>
      <a href="#" @click.prevent="openDisclaimer">Disclaimer</a> |
      <router-link to="/contribute">How to Contribute</router-link> |
      <router-link to="/links">Links</router-link>
      <br />
      Joris Deguet, Anton Deguet, Aravind S. Kumar
      <br />
      Last updated {{ commitDate }}
      <br />
      {{ nbCompanies }} companies, {{ nbSystems }} systems
    </p>
  </footer>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DisclaimerModal from './components/DisclaimerModal.vue';

const commitDate = __COMMIT_DATE__;
const nbCompanies = ref('…');
const nbSystems = ref('…');

onMounted(async () => {
  try {
    const [companiesRes, robotsRes] = await Promise.all([
      fetch('/companies.json'),
      fetch('/robots.json'),
    ]);
    const companies = await companiesRes.json();
    const robots = await robotsRes.json();
    nbCompanies.value = companies.length;
    nbSystems.value = robots.length;
  } catch (e) {
    nbCompanies.value = '?';
    nbSystems.value = '?';
  }
});

function openDisclaimer() {
  window.dispatchEvent(new Event('open-disclaimer'));
}
// TODO pop disclaimer back
</script>

<style>
.footer {
  text-align: center;
  padding: 1rem 0;
  margin-top: 1.5rem;
  border-top: 1px solid var(--color-border);
  color: var(--color-text);
  font-size: 0.875rem;
}

.footer p {
  margin: 0;
}

.global-logo {
  height: 48px;
  width: auto;
  opacity: 0.9;
  transition: opacity 0.2s;
}
.global-logo:hover {
  opacity: 1;
}

</style>
