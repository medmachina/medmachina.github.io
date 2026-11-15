<template>
  <a
    v-if="stock && stock.ticker"
    :href="stock.url"
    target="_blank"
    rel="noopener noreferrer"
    class="stock-sticker text-decoration-none"
    :class="quote ? `stock-${quote.direction}` : 'stock-neutral'"
    :title="tooltipText"
    @click.stop
  >
    <span class="stock-ticker">{{ stock.ticker }}</span>
    <template v-if="quote">
      <span class="stock-price">{{ formatPrice(quote.last, quote.currency) }}</span>
      <span class="stock-change" :class="`change-${quote.direction}`">
        <span v-if="quote.direction === 'up'">▲</span>
        <span v-else-if="quote.direction === 'down'">▼</span>
        {{ quote.changePct }}
      </span>
    </template>
    <span v-else class="stock-ext-arrow">↗</span>
  </a>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue';
import { stockQuotes, requestStockQuote } from '../utils/stocks.js';

const props = defineProps({
  stock: {
    type: Object,
    default: null
  }
});

const quote = computed(() => {
  const sym = props.stock?.cnbc_symbol;
  return sym ? stockQuotes[sym] || null : null;
});

const tooltipText = computed(() => {
  if (!props.stock) return '';
  if (!quote.value) return `View ${props.stock.ticker} stock quote`;
  const q = quote.value;
  return `${props.stock.ticker}: ${q.last} ${q.currency} (${q.change} / ${q.changePct} today) — click for chart`;
});

function formatPrice(last, currency) {
  const symMap = {
    USD: '$',
    EUR: '€',
    HKD: 'HK$',
    JPY: '¥',
    CNY: '¥',
    GBP: '£',
    GBp: 'p',
    SEK: 'kr '
  };
  const prefix = symMap[currency] || '';
  if (currency === 'GBp') return `${last}p`;
  return `${prefix}${last}`;
}

onMounted(() => {
  if (props.stock?.cnbc_symbol) {
    requestStockQuote(props.stock.cnbc_symbol);
  }
});

watch(
  () => props.stock?.cnbc_symbol,
  newSym => {
    if (newSym) requestStockQuote(newSym);
  }
);
</script>

<style scoped>
.stock-sticker {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.76rem;
  font-weight: 600;
  padding: 0.16rem 0.5rem;
  border-radius: 0.45rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-background-mute);
  color: var(--color-text);
  vertical-align: middle;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stock-sticker:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
  color: var(--color-heading);
}

.stock-ticker {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  letter-spacing: 0.01em;
}

.stock-price {
  font-weight: 700;
  color: var(--color-heading);
}

.stock-change {
  font-size: 0.72rem;
  padding: 0.05rem 0.32rem;
  border-radius: 0.3rem;
  font-weight: 700;
}

.change-up {
  background-color: rgba(25, 135, 84, 0.16);
  color: #198754;
}

.change-down {
  background-color: rgba(220, 53, 69, 0.16);
  color: #dc3545;
}

.change-flat {
  background-color: rgba(108, 117, 125, 0.16);
  color: #6c757d;
}

:global([data-bs-theme="dark"]) .change-up {
  background-color: rgba(40, 199, 111, 0.2);
  color: #4bd88a;
}

:global([data-bs-theme="dark"]) .change-down {
  background-color: rgba(234, 84, 85, 0.22);
  color: #ff6b6b;
}

.stock-ext-arrow {
  font-size: 0.7rem;
  opacity: 0.75;
}
</style>
