<template>
  <div class="global-header">
    <router-link to="/">
      <img src="/text-logo.svg" alt="medmachina logo" class="global-logo" />
    </router-link>
  </div>
  <router-view />
  <DisclaimerModal />
  <footer class="footer">
    <p>
      <a href="#" @click.prevent="openDisclaimer">Disclaimer</a> |
      <router-link to="/contribute">How to Contribute</router-link> |
      <router-link to="/links">Links</router-link>
      <br />
      Joris Deguet, Anton Deguet, Aravind S. Kumar
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

.global-header {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  padding: 1.2rem 2.2rem 0 0;
  box-sizing: border-box;
}
.global-logo {
  height: 48px;
  width: auto;
}
</style>
