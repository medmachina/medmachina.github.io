<template>
  <router-view />
  <footer class="footer">
    <p>made by the Deguet brothers</p>
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
  border-top: 1px solid #eee;
  color: #666;
  font-size: 0.875rem;
}

.footer p {
  margin: 0;
}
</style>
