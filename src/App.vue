<template>
  <router-view />
  <DisclaimerModal />
  <footer class="footer">
    <p>
      By Joris Deguet, Anton Deguet, Aravind S. Kumar |
      <a href="#" @click.prevent="openDisclaimer">Disclaimer</a> |
      <router-link to="/contribute">How to Contribute</router-link> |
      <router-link to="/contact">Contact Us</router-link>
    </p>
  </footer>
</template>

<script setup>
import DisclaimerModal from './components/DisclaimerModal.vue';
function openDisclaimer() {
  window.dispatchEvent(new Event('open-disclaimer'));
}
// TODO pop disclaimer back
</script>

<style>
.footer {
  text-align: center;
  padding: 2rem 0;
  margin-top: 3rem;
  border-top: 1px solid var(--color-border);
  color: var(--color-text);
  font-size: 0.875rem;
}

.footer p {
  margin: 0;
}
</style>
