<template>
  <router-view />
  <footer class="footer">
    <p>
      Made by Joris Deguet, Anton Deguet, Aravind S. Kumar |
      <router-link to="/contribute">How to Contribute</router-link> |
      <router-link to="/contact">Contact Us</router-link>
    </p>
  </footer>
</template>

<script setup>
// Plus aucune logique ici, tout est géré par les composants de vue-router
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
