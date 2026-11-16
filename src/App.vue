<template>
  <div class="top-utility-bar">
    <a
      href="https://github.com/medmachina/medmachina.github.io"
      target="_blank"
      rel="noopener noreferrer"
      class="github-star-link"
      title="Star Med Machina on GitHub"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" fill="currentColor" viewBox="0 0 16 16" class="star-icon" aria-hidden="true">
        <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>
      </svg>
      <span>Star on GitHub</span>
      <span v-if="starCount > 0" class="star-count">{{ starCount }}</span>
    </a>
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
const starCount = ref(0);

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

  try {
    const cached = sessionStorage.getItem('mm_gh_stars');
    if (cached !== null) {
      starCount.value = Number(cached) || 0;
    } else {
      const ghRes = await fetch('https://api.github.com/repos/medmachina/medmachina.github.io');
      if (ghRes.ok) {
        const ghData = await ghRes.json();
        const count = Number(ghData.stargazers_count) || 0;
        starCount.value = count;
        sessionStorage.setItem('mm_gh_stars', String(count));
      }
    }
  } catch {
    // Ignore GitHub API errors
  }
});

function openDisclaimer() {
  window.dispatchEvent(new Event('open-disclaimer'));
}
// TODO pop disclaimer back
</script>

<style>
.top-utility-bar {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.35rem;
  margin-bottom: -0.2rem;
}

.github-star-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  line-height: 1.2;
  color: var(--color-text);
  opacity: 0.65;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background-color: var(--color-background-soft);
  text-decoration: none;
  transition: opacity 0.2s ease, border-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.github-star-link:hover {
  opacity: 1;
  color: var(--color-heading);
  border-color: var(--color-border-hover);
  background-color: var(--color-background-mute);
}

.github-star-link .star-icon {
  color: #f59e0b;
}

.github-star-link .star-count {
  padding-left: 0.25rem;
  border-left: 1px solid var(--color-border);
  font-weight: 600;
}

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
