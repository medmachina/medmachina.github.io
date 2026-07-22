/**
 * Utility for dynamically updating head meta tags, document title, canonical URLs,
 * Open Graph tags, and Schema.org JSON-LD structured data.
 */

const BASE_URL = 'https://medmachina.github.io';
const DEFAULT_IMAGE = `${BASE_URL}/og/og-home.png`;

export function updateSeo({
  title = 'Medical Robots Directory | Med Machina',
  description = 'A comprehensive directory of medical and surgical robots, companies, and regulatory statuses.',
  path = '/',
  image = DEFAULT_IMAGE,
  type = 'website',
  jsonLd = null
} = {}) {
  // 1. Update Title
  document.title = title;

  // 2. Canonical URL
  const canonicalUrl = `${BASE_URL}${path.startsWith('/') ? path : '/' + path}`;
  let canonicalEl = document.querySelector('link[rel="canonical"]');
  if (!canonicalEl) {
    canonicalEl = document.createElement('link');
    canonicalEl.setAttribute('rel', 'canonical');
    document.head.appendChild(canonicalEl);
  }
  canonicalEl.setAttribute('href', canonicalUrl);

  // Helper for setting meta tags
  const setMeta = (selector, attr, val) => {
    let el = document.querySelector(selector);
    if (!el) {
      el = document.createElement('meta');
      if (selector.startsWith('meta[name=')) {
        const nameVal = selector.match(/name="([^"]+)"/)[1];
        el.setAttribute('name', nameVal);
      } else if (selector.startsWith('meta[property=')) {
        const propVal = selector.match(/property="([^"]+)"/)[1];
        el.setAttribute('property', propVal);
      }
      document.head.appendChild(el);
    }
    el.setAttribute(attr, val);
  };

  // 3. Meta Description
  setMeta('meta[name="description"]', 'content', description);

  // 4. Open Graph Tags
  setMeta('meta[property="og:title"]', 'content', title);
  setMeta('meta[property="og:description"]', 'content', description);
  setMeta('meta[property="og:url"]', 'content', canonicalUrl);
  setMeta('meta[property="og:type"]', 'content', type);
  setMeta('meta[property="og:image"]', 'content', image.startsWith('http') ? image : `${BASE_URL}${image}`);

  // 5. JSON-LD Structured Data
  let jsonLdEl = document.getElementById('seo-jsonld');
  if (jsonLd) {
    if (!jsonLdEl) {
      jsonLdEl = document.createElement('script');
      jsonLdEl.setAttribute('type', 'application/ld+json');
      jsonLdEl.setAttribute('id', 'seo-jsonld');
      document.head.appendChild(jsonLdEl);
    }
    jsonLdEl.textContent = JSON.stringify(jsonLd, null, 2);
  } else if (jsonLdEl) {
    jsonLdEl.remove();
  }
}
