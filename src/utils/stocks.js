import { reactive } from 'vue';

// Shared reactive cache of live quotes keyed by cnbc_symbol
export const stockQuotes = reactive({});

const pendingSymbols = new Set();
const fetchedSymbols = new Set();
let batchTimer = null;

export function requestStockQuote(cnbcSymbol) {
  if (!cnbcSymbol || fetchedSymbols.has(cnbcSymbol) || pendingSymbols.has(cnbcSymbol)) {
    return;
  }
  pendingSymbols.add(cnbcSymbol);
  if (!batchTimer) {
    batchTimer = setTimeout(flushSymbolBatch, 40);
  }
}

async function flushSymbolBatch() {
  batchTimer = null;
  if (pendingSymbols.size === 0) return;

  const symbols = Array.from(pendingSymbols);
  pendingSymbols.clear();
  symbols.forEach(s => fetchedSymbols.add(s));

  try {
    const joined = encodeURIComponent(symbols.join('|'));
    const url = `https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols=${joined}&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json&events=1`;
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();
    let list = data?.FormattedQuoteResult?.FormattedQuote;
    if (!list) return;
    if (!Array.isArray(list)) list = [list];

    list.forEach(q => {
      if (!q || !q.symbol || !q.last) return;
      const rawChange = String(q.change || '0').trim();
      const rawPct = String(q.change_pct || '').trim();
      const numChange = parseFloat(rawChange.replace(/[^0-9.-]/g, '')) || 0;
      const direction = rawChange === 'UNCH' || numChange === 0
        ? 'flat'
        : numChange > 0
          ? 'up'
          : 'down';

      stockQuotes[q.symbol] = {
        last: q.last,
        change: rawChange,
        changePct: rawPct === 'UNCH' ? '0.00%' : rawPct,
        currency: q.currencyCode || '',
        direction
      };
    });
  } catch (err) {
    // Fail silently if offline or blocked by adblocker; static ticker link still works
  }
}
