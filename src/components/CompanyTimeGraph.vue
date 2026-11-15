<template>
  <div class="time-graph-wrapper" ref="wrapperRef">
    <!-- Legend & Robot Dots Toggle -->
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-2">
      <div class="graph-legend d-flex flex-wrap align-items-center gap-3 small">
        <span class="legend-item">
          <span class="legend-bar active-bar"></span> Active
        </span>
        <span v-if="hasPredecessor" class="legend-item">
          <span class="legend-bar predecessor-bar"></span> Predecessor
        </span>
        <span v-if="hasEdgeCategory('ma')" class="legend-item">
          <span class="legend-line line-ma"></span> Merger / Acquisition
        </span>
        <span v-if="hasEdgeCategory('oem')" class="legend-item">
          <span class="legend-line line-oem"></span> OEM Supply
        </span>
        <span v-if="hasEdgeCategory('collab')" class="legend-item">
          <span class="legend-line line-collab"></span> Alliance / JV / IP
        </span>
        <span class="legend-item">
          <span class="legend-dot"></span> Robot launch
        </span>
      </div>

      <div class="form-check form-switch mb-0">
        <input
          id="toggleRobotDots"
          v-model="showRobotDots"
          class="form-check-input"
          type="checkbox"
        />
        <label class="form-check-label small" for="toggleRobotDots">
          Show robots
        </label>
      </div>
    </div>

    <!-- Scrollable SVG Container -->
    <div v-if="layout.rows.length > 0" class="svg-scroll-container card p-2" ref="scrollContainer">
      <svg
        :viewBox="`0 0 ${SVG_WIDTH} ${layout.totalHeight}`"
        class="company-time-svg"
        preserveAspectRatio="xMinYMin meet"
      >
        <defs>
          <marker id="arrow-ma" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#38bdf8" />
          </marker>
          <marker id="arrow-oem" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#f59e0b" />
          </marker>
          <marker id="dot-collab" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="4.5" markerHeight="4.5">
            <circle cx="4" cy="4" r="3" fill="#a855f7" />
          </marker>
        </defs>

        <!-- Vertical Year Grid Lines & Axis -->
        <g class="axis-layer">
          <!-- Pre-linear shaded band when any company in the group was founded before minLinearYear -->
          <template v-if="layout.hasPreEra">
            <rect
              :x="LEFT_MARGIN"
              :y="TOP_AXIS_HEIGHT"
              :width="layout.linearStartX - LEFT_MARGIN"
              :height="layout.totalHeight - TOP_AXIS_HEIGHT - BOTTOM_AXIS_HEIGHT"
              class="pre-era-band"
            />
            <text
              :x="(LEFT_MARGIN + layout.linearStartX) / 2"
              :y="TOP_AXIS_HEIGHT - 10"
              text-anchor="middle"
              class="axis-label"
            >
              &lt;{{ layout.minLinearYear }}
            </text>
            <line
              :x1="layout.linearStartX"
              :y1="TOP_AXIS_HEIGHT - 6"
              :x2="layout.linearStartX"
              :y2="layout.totalHeight - BOTTOM_AXIS_HEIGHT + 6"
              class="axis-break-line"
              stroke-dasharray="3,3"
            />
          </template>

          <!-- 5-Year Grid Ticks (no green 2026 line) -->
          <g v-for="yr in layout.axisYears" :key="yr">
            <line
              :x1="layout.yearToX(yr)"
              :y1="TOP_AXIS_HEIGHT"
              :x2="layout.yearToX(yr)"
              :y2="layout.totalHeight - BOTTOM_AXIS_HEIGHT"
              class="grid-line"
            />
            <text
              :x="layout.yearToX(yr)"
              :y="TOP_AXIS_HEIGHT - 10"
              text-anchor="middle"
              class="axis-label"
            >
              {{ yr }}
            </text>
            <text
              :x="layout.yearToX(yr)"
              :y="layout.totalHeight - 8"
              text-anchor="middle"
              class="axis-label"
            >
              {{ yr }}
            </text>
          </g>
        </g>

        <!-- Row Highlight Backgrounds (visual only, no hover pop-up on full row) -->
        <g class="rows-bg-layer">
          <g v-for="row in layout.rows" :key="`bg-${row.id}`">
            <rect
              :x="8"
              :y="row.y - ROW_HEIGHT / 2 + 2"
              :width="SVG_WIDTH - 16"
              :height="ROW_HEIGHT - 4"
              rx="5"
              class="row-bg"
              :class="{
                'row-focused': row.id === focusCompanyId,
                'row-highlighted': isRowHighlighted(row.id),
                'row-dimmed': isAnyHovered && !isRowHighlighted(row.id)
              }"
            />
          </g>
        </g>

        <!-- Branch / Relationship Connectors Layer (clean curves without bulky overlapping boxes) -->
        <g class="edges-layer">
          <g
            v-for="edge in layout.edges"
            :key="edge.id"
            class="edge-group"
            :class="{
              'edge-highlighted': isEdgeHighlighted(edge),
              'edge-dimmed': isAnyHovered && !isEdgeHighlighted(edge)
            }"
            @mouseenter="onHoverEdge(edge, $event)"
            @mouseleave="scheduleHideTooltip"
          >
            <path
              :d="edge.path"
              fill="none"
              stroke="transparent"
              stroke-width="14"
              class="edge-hit"
            />
            <path
              :d="edge.path"
              fill="none"
              :class="['edge-path', `edge-${edge.category}`]"
              :marker-end="edge.category === 'ma' ? 'url(#arrow-ma)' : edge.category === 'oem' ? 'url(#arrow-oem)' : 'url(#dot-collab)'"
              :marker-start="edge.category === 'collab' ? 'url(#dot-collab)' : undefined"
            />
            <!-- Subtle halo year label along the curve -->
            <text
              :x="edge.labelX"
              :y="edge.labelY"
              text-anchor="middle"
              :class="['edge-year-halo', `edge-year-${edge.category}`]"
            >
              {{ edge.year }}
            </text>
          </g>
        </g>

        <!-- Company Lifespan Bars, Left Column Labels, and Robot Dots -->
        <g class="rows-layer">
          <g
            v-for="row in layout.rows"
            :key="row.id"
            class="company-row-group"
            :class="{
              'row-dimmed': isAnyHovered && !isRowHighlighted(row.id)
            }"
          >
            <!-- Left column company label + relationship subtitle (click navigates, no hover pop-up) -->
            <g
              class="company-label-group"
              @click="onClickCompany(row)"
              :style="{ cursor: row.isPredecessor || row.id === focusCompanyId ? 'default' : 'pointer' }"
            >
              <text
                :x="row.isPredecessor ? 22 : 16"
                :y="row.relationSummary ? row.y - 2 : row.y + 4"
                class="company-name-text"
                :class="{
                  'predecessor-name-text': row.isPredecessor,
                  'focused-name-text': row.id === focusCompanyId
                }"
              >
                {{ row.isPredecessor ? '↳ ' + row.name : truncateText(row.name, 24) }}
              </text>
              <text
                v-if="row.relationSummary"
                :x="row.isPredecessor ? 32 : 16"
                :y="row.y + 11"
                class="company-rel-sub"
                :class="`rel-sub-${row.relationCategory}`"
              >
                {{ truncateText(row.relationSummary, 30) }}
              </text>
              <text
                :x="LEFT_MARGIN - 10"
                :y="row.y + 4"
                text-anchor="end"
                class="company-year-sub"
              >
                {{ row.foundedYear }}{{ row.endYear < CURRENT_YEAR ? `–${String(row.endYear).slice(-2)}` : '' }}
              </text>
            </g>

            <!-- Lifespan horizontal bar (only hovering the thick line triggers the company pop-up) -->
            <g
              class="bar-hit-group"
              @mouseenter="onHoverRow(row, $event)"
              @mouseleave="scheduleHideTooltip"
              @click="onClickCompany(row)"
            >
              <line
                :x1="row.startX"
                :y1="row.y"
                :x2="row.endX"
                :y2="row.y"
                stroke="transparent"
                stroke-width="12"
                stroke-linecap="round"
                style="cursor: pointer;"
              />
              <line
                :x1="row.startX"
                :y1="row.y"
                :x2="row.endX"
                :y2="row.y"
                :class="[
                  'lifespan-bar',
                  row.isPredecessor ? 'bar-predecessor' : `bar-${row.state}`
                ]"
              />

              <!-- Start cap & pre-era year label -->
              <circle
                :cx="row.startX"
                :cy="row.y"
                r="3.5"
                :class="['bar-cap-start', row.isPredecessor ? 'cap-predecessor' : `cap-${row.state}`]"
              />
              <text
                v-if="layout.hasPreEra && row.foundedYear < layout.minLinearYear"
                :x="row.startX + 6"
                :y="row.y - 6"
                class="pre-era-tag"
              >
                est. {{ row.foundedYear }}
              </text>

              <!-- End cap -->
              <g v-if="row.state === 'liquidated' || row.state === 'defunct' || row.state === 'restructuring'">
                <circle
                  :cx="row.endX"
                  :cy="row.y"
                  r="5.5"
                  :class="row.state === 'restructuring' ? 'exit-circle-warn' : 'exit-circle-danger'"
                />
                <text
                  :x="row.endX"
                  :y="row.y + 3"
                  text-anchor="middle"
                  class="exit-symbol"
                >
                  {{ row.state === 'restructuring' ? '!' : '✕' }}
                </text>
                <text
                  :x="row.endX + 9"
                  :y="row.y + 3.5"
                  class="exit-label"
                >
                  {{ row.endYear }} {{ row.state === 'restructuring' ? 'Insolvent' : row.state === 'defunct' ? 'Assets Sold' : 'Liquidated' }}
                </text>
              </g>
              <circle
                v-else
                :cx="row.endX"
                :cy="row.y"
                r="4"
                :class="['bar-cap-end', row.isPredecessor ? 'cap-predecessor' : `cap-${row.state}`]"
              />
            </g>

            <!-- Compact External Acquirer / Partner Label at end of bar -->
            <text
              v-for="(ext, eIdx) in row.externalBadges"
              :key="eIdx"
              :x="ext.x + 8"
              :y="row.y + 3.5"
              :class="['ext-inline-text', `ext-text-${ext.category}`]"
            >
              {{ ext.label }}
            </text>

            <!-- Robot Launch Dots along the company bar (clean markers, details in interactive popover) -->
            <template v-if="showRobotDots">
              <g
                v-for="rDot in row.robotDots"
                :key="rDot.id"
                class="robot-dot-group"
                :transform="`translate(${rDot.x}, ${row.y + rDot.yOffset})`"
                @mouseenter.stop="onHoverRobot(rDot, row, $event)"
                @mouseleave.stop="scheduleHideTooltip"
                @click.stop="onClickRobot(rDot.id)"
              >
                <circle r="4.2" class="robot-dot" />
              </g>
            </template>
          </g>
        </g>
      </svg>
    </div>

    <!-- Interactive Reachable Popover Card (outside scroll container so it never spawns a scrollbar) -->
    <div
      v-if="tooltip.visible"
      class="graph-tooltip shadow"
      :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
      @mouseenter="cancelHideTooltip"
      @mouseleave="scheduleHideTooltip"
    >
      <div class="fw-bold mb-1 d-flex align-items-center justify-content-between gap-2">
        <span>{{ tooltip.title }}</span>
        <span v-if="tooltip.badge" class="badge" :class="tooltip.badgeClass">{{ tooltip.badge }}</span>
      </div>
      <div v-if="tooltip.subtitle" class="small text-muted mb-1">{{ tooltip.subtitle }}</div>
      <div v-if="tooltip.body" class="small mb-2">{{ tooltip.body }}</div>

      <!-- Clickable robot pills inside company popover -->
      <div v-if="tooltip.robots && tooltip.robots.length" class="mb-2">
        <div class="small text-muted mb-1">Robots:</div>
        <div class="d-flex flex-wrap gap-1">
          <router-link
            v-for="r in tooltip.robots"
            :key="r.id"
            :to="`/robot/${r.id}`"
            class="badge bg-secondary text-decoration-none tooltip-robot-pill"
          >
            {{ r.shortName }} ({{ r.year }})
          </router-link>
        </div>
      </div>

      <!-- Source citation links -->
      <div v-if="tooltip.sources && tooltip.sources.length" class="small text-muted mb-2">
        sources:
        <a
          v-for="(srcUrl, sIdx) in tooltip.sources"
          :key="sIdx"
          :href="srcUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="ms-1 text-decoration-none fw-semibold tooltip-source-link"
          :title="srcUrl"
        >[{{ sIdx + 1 }}]</a>
      </div>

      <!-- Reachable router-link button & Edit on GitHub button -->
      <div v-if="tooltip.linkTo || tooltip.editGithubUrl" class="pt-1 border-top d-flex align-items-center justify-content-between gap-2 flex-wrap">
        <router-link v-if="tooltip.linkTo" :to="tooltip.linkTo" class="btn btn-sm btn-outline-primary py-0 px-2 small">
          {{ tooltip.linkLabel }} →
        </router-link>
        <a
          v-if="tooltip.editGithubUrl"
          :href="tooltip.editGithubUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="btn btn-sm btn-outline-secondary py-0 px-2 small d-inline-flex align-items-center"
          title="Edit this relationship on GitHub"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16" style="margin-right:4px;">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
          </svg>
          Edit on GitHub
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  companies: {
    type: Array,
    required: true
  },
  robots: {
    type: Array,
    default: () => []
  },
  relationships: {
    type: Array,
    default: () => []
  },
  focusCompanyId: {
    type: String,
    required: true
  }
});

const router = useRouter();
const wrapperRef = ref(null);
const scrollContainer = ref(null);

const SVG_WIDTH = 1040;
const LEFT_MARGIN = 230;
const RIGHT_END_X = 910;
const CURRENT_YEAR = 2026;
const TOP_AXIS_HEIGHT = 28;
const BOTTOM_AXIS_HEIGHT = 22;
const ROW_HEIGHT = 46;

const showRobotDots = ref(true);
const hoveredRowId = ref(null);
const hoveredEdge = ref(null);
let hideTimer = null;

const tooltip = ref({
  visible: false,
  targetKey: '',
  x: 16,
  y: 16,
  title: '',
  subtitle: '',
  badge: '',
  badgeClass: 'bg-secondary',
  body: '',
  robots: [],
  sources: [],
  linkTo: '',
  linkLabel: '',
  editGithubUrl: ''
});

function edgeCategory(type) {
  if (type === 'merged' || type === 'acquired' || type === 'predecessor') return 'ma';
  if (type === 'oem') return 'oem';
  return 'collab';
}

const companyMap = computed(() => {
  const m = new Map();
  props.companies.forEach(c => {
    if (c && c.id) m.set(c.id, c);
  });
  return m;
});

const robotsByCompany = computed(() => {
  const map = new Map();
  const rMap = new Map();
  props.robots.forEach(r => {
    if (r && r.id) rMap.set(r.id, r);
  });
  props.companies.forEach(c => {
    if (!c || !c.id) return;
    const list = (c.robots || [])
      .map(rid => rMap.get(rid))
      .filter(r => r && r.introduction_year);
    list.sort((a, b) => a.introduction_year - b.introduction_year);
    map.set(c.id, list);
  });
  return map;
});

// Build focused 1-degree per-company ego-graph layout
const layout = computed(() => {
  const focusId = props.focusCompanyId;
  const focusCompany = companyMap.value.get(focusId);
  if (!focusCompany) {
    return { rows: [], edges: [], axisYears: [], totalHeight: 0, hasPreEra: false, minLinearYear: 1990, linearStartX: LEFT_MARGIN, yearToX: () => LEFT_MARGIN };
  }

  const incomingIds = new Set();
  const outgoingIds = new Set();
  const predecessorRels = [];
  const relevantEdges = [];
  const relationByRowId = new Map();

  // Read from standalone props.relationships (public/relationships/*.json)
  (props.relationships || []).forEach(rel => {
    if (!rel) return;
    const cat = edgeCategory(rel.type);

    if (rel.target === focusId) {
      if (companyMap.value.has(rel.source)) {
        incomingIds.add(rel.source);
        relevantEdges.push(rel);
        relationByRowId.set(rel.source, {
          relId: rel.id || `${rel.source}_${rel.target}`,
          summary: `${rel.subtype || rel.type} (${rel.year})`,
          category: cat,
          sources: Array.isArray(rel.sources) ? rel.sources : []
        });
      } else {
        // Acquired predecessor without a standalone company page
        predecessorRels.push(rel);
        relevantEdges.push(rel);
        relationByRowId.set(rel.source, {
          relId: rel.id || `${rel.source}_${rel.target}`,
          summary: `${rel.subtype || 'Acquired'} (${rel.year})`,
          category: 'ma',
          sources: Array.isArray(rel.sources) ? rel.sources : []
        });
      }
    } else if (rel.source === focusId) {
      if (companyMap.value.has(rel.target)) {
        outgoingIds.add(rel.target);
        relevantEdges.push(rel);
        relationByRowId.set(rel.target, {
          relId: rel.id || `${rel.source}_${rel.target}`,
          summary: `${rel.subtype || rel.type} (${rel.year})`,
          category: cat,
          sources: Array.isArray(rel.sources) ? rel.sources : []
        });
      }
    }
  });

  // Build candidate row descriptors and reorder to minimize edge/bar crossings
  const initialDescriptors = [];
  Array.from(incomingIds)
    .map(id => companyMap.value.get(id))
    .filter(Boolean)
    .sort((a, b) => (Number(a.founded_year) || 2000) - (Number(b.founded_year) || 2000))
    .forEach(c => initialDescriptors.push({ type: 'company', role: 'in', company: c }));

  predecessorRels
    .sort((a, b) => (Number(a.source_founded_year) || 2000) - (Number(b.source_founded_year) || 2000))
    .forEach(pred => {
      initialDescriptors.push({
        type: 'predecessor',
        role: 'pred',
        parentId: focusId,
        company: {
          id: pred.source,
          name: pred.source_name || pred.source,
          country: focusCompany.country,
          founded_year: pred.source_founded_year || (pred.year - 6),
          status: {
            state: 'acquired',
            year: pred.year,
            successor: focusCompany.name,
            note: pred.note
          },
          robots: []
        }
      });
    });

  initialDescriptors.push({ type: 'company', role: 'focus', company: focusCompany });

  Array.from(outgoingIds)
    .filter(id => !incomingIds.has(id))
    .map(id => companyMap.value.get(id))
    .filter(Boolean)
    .sort((a, b) => (Number(a.founded_year) || 2000) - (Number(b.founded_year) || 2000))
    .forEach(c => initialDescriptors.push({ type: 'company', role: 'out', company: c }));

  function getDescSpan(d) {
    const start = Number(d.company.founded_year) || 2010;
    const st = d.company.status?.state || 'active';
    const end = (st !== 'active' && d.company.status?.year) ? Number(d.company.status.year) : CURRENT_YEAR;
    return { start, end };
  }

  let orderedDescriptors = initialDescriptors;
  if (initialDescriptors.length > 2 && initialDescriptors.length <= 8) {
    const spans = new Map();
    initialDescriptors.forEach(d => spans.set(d.company.id, getDescSpan(d)));
    const nLen = initialDescriptors.length;
    const center = (nLen - 1) / 2.0;
    let bestPerm = initialDescriptors;
    let bestScore = Infinity;

    function permute(arr, l) {
      if (l === arr.length - 1) {
        const pos = new Map();
        for (let i = 0; i < arr.length; i++) {
          pos.set(arr[i].company.id, i);
        }
        const fIdx = pos.get(focusId);
        let barCrossings = 0;
        let spanPenalty = 0;

        for (let eIdx = 0; eIdx < relevantEdges.length; eIdx++) {
          const e = relevantEdges[eIdx];
          const sIdx = pos.get(e.source);
          const tIdx = pos.get(e.target);
          if (sIdx === undefined || tIdx === undefined) continue;
          const lo = Math.min(sIdx, tIdx);
          const hi = Math.max(sIdx, tIdx);
          const yr = Number(e.year) || 2020;
          spanPenalty += (hi - lo - 1) * 100;
          const sSpan = spans.get(e.source);
          const xMin = e.type === 'oem' ? yr - 1 : Math.min(yr, sSpan ? sSpan.end : yr);
          const xMax = yr;

          for (let midIdx = lo + 1; midIdx < hi; midIdx++) {
            const midSpan = spans.get(arr[midIdx].company.id);
            if (midSpan && midSpan.start <= xMax && midSpan.end >= xMin) {
              barCrossings += 1;
            }
          }
        }

        const centerDist = Math.abs(fIdx - center) * 50;
        let dirPenalty = 0;
        for (let i = 0; i < arr.length; i++) {
          const r = arr[i].role;
          if ((r === 'in' || r === 'pred') && i > fIdx) dirPenalty += 10;
          else if (r === 'out' && i < fIdx) dirPenalty += 10;
        }

        const score = barCrossings * 10000 + spanPenalty + centerDist + dirPenalty;
        if (score < bestScore) {
          bestScore = score;
          bestPerm = arr.slice();
        }
        return;
      }
      for (let i = l; i < arr.length; i++) {
        const tmp = arr[l];
        arr[l] = arr[i];
        arr[i] = tmp;
        permute(arr, l + 1);
        arr[i] = arr[l];
        arr[l] = tmp;
      }
    }

    permute(initialDescriptors.slice(), 0);
    orderedDescriptors = bestPerm;
  }

  // Compute adaptive linear start year for this subgraph
  const allFoundedYears = orderedDescriptors.map(d => Number(d.company.founded_year) || 2000);
  const modernYears = allFoundedYears.filter(y => y >= 1988);
  const earliestModern = modernYears.length ? Math.min(...modernYears) : 1995;
  const minLinearYear = Math.max(1988, Math.floor((earliestModern - 2) / 5) * 5);
  const hasPreEra = allFoundedYears.some(y => y < minLinearYear);
  const linearStartX = hasPreEra ? LEFT_MARGIN + 65 : LEFT_MARGIN + 12;

  function yearToX(year) {
    const y = Number(year) || 2000;
    if (hasPreEra && y < minLinearYear) {
      const clamped = Math.max(1885, Math.min(minLinearYear - 1, y));
      const ratio = (clamped - 1885) / Math.max(1, (minLinearYear - 1 - 1885));
      return Math.round(LEFT_MARGIN + 10 + ratio * (linearStartX - LEFT_MARGIN - 20));
    }
    const clamped = Math.min(CURRENT_YEAR, Math.max(minLinearYear, y));
    const ratio = (clamped - minLinearYear) / Math.max(1, (CURRENT_YEAR - minLinearYear));
    return Math.round(linearStartX + ratio * (RIGHT_END_X - linearStartX));
  }

  // Only 5-year axis ticks (1990..2025), no 2026 vertical line
  const axisYears = [];
  const firstTick = Math.ceil(minLinearYear / 5) * 5;
  for (let yr = firstTick; yr <= 2025; yr += 5) {
    axisYears.push(yr);
  }

  const rows = [];
  const rowById = new Map();
  let currentY = TOP_AXIS_HEIGHT + ROW_HEIGHT / 2 + 4;

  orderedDescriptors.forEach(desc => {
    const company = desc.company;
    const isPredecessor = desc.type === 'predecessor';
    const foundedYear = Number(company.founded_year) || 2010;
    const state = company.status?.state || 'active';
    const endYear = (state !== 'active' && company.status?.year) ? Number(company.status.year) : CURRENT_YEAR;
    const startX = yearToX(foundedYear);
    const endX = Math.max(startX + 8, yearToX(endYear));

    const cRobots = isPredecessor ? [] : (robotsByCompany.value.get(company.id) || []);
    const yearCounts = {};
    const robotDots = cRobots.map(r => {
      const yr = Number(r.introduction_year);
      const clampedYr = Math.max(foundedYear, Math.min(endYear, yr));
      const x = yearToX(clampedYr);
      const count = yearCounts[clampedYr] || 0;
      yearCounts[clampedYr] = count + 1;
      const yOffset = count === 0 ? 0 : (count % 2 === 1 ? -5 : 5);
      let shortName = r.name;
      if (shortName.toLowerCase().startsWith(company.name.toLowerCase() + ' ')) {
        shortName = shortName.slice(company.name.length + 1);
      }
      const rSources = (r.urls || [])
        .map(u => u.url)
        .filter(u => u && !u.includes('medmachina.github.io'));
      return { id: r.id, name: r.name, shortName, year: yr, x, yOffset, sources: rSources };
    });

    const externalBadges = [];
    if (!isPredecessor) {
      if ((state === 'acquired' || state === 'merged') && company.status?.successor) {
        const succSlug = company.status.successor.toLowerCase().replace(/[^a-z0-9]+/g, '_');
        const hasTargetInSubgraph = orderedDescriptors.some(d => d.company.id === succSlug) ||
          relevantEdges.some(rel => rel.source === company.id && (rel.type === 'acquired' || rel.type === 'merged') && orderedDescriptors.some(d => d.company.id === rel.target));
        if (!hasTargetInSubgraph) {
          externalBadges.push({
            x: endX,
            label: `→ ${company.status.successor} (${endYear})`,
            category: 'ma'
          });
        }
      }
      (props.relationships || []).forEach(rel => {
        if (rel && rel.source === company.id && !companyMap.value.has(rel.target) && rel.target_name) {
          externalBadges.push({
            x: yearToX(rel.year),
            label: `⇄ ${rel.target_name} (${rel.year})`,
            category: edgeCategory(rel.type)
          });
        }
      });
    }

    const relInfo = relationByRowId.get(company.id);
    const rowSourcesSet = new Set(relInfo?.sources || []);
    if (company.status?.source_url) {
      rowSourcesSet.add(company.status.source_url);
    }

    const rowObj = {
      id: company.id,
      name: company.name,
      country: company.country || '',
      foundedYear,
      endYear,
      state,
      statusNote: company.status?.note || '',
      relId: relInfo?.relId || '',
      relationSummary: relInfo?.summary || '',
      relationCategory: relInfo?.category || 'collab',
      sources: Array.from(rowSourcesSet),
      startX,
      endX,
      y: currentY,
      isPredecessor,
      parentId: desc.parentId || null,
      robotDots,
      externalBadges
    };
    rows.push(rowObj);
    rowById.set(company.id, rowObj);
    currentY += ROW_HEIGHT;
  });

  // Build edges
  const edges = [];
  let edgeIdx = 0;
  relevantEdges.forEach(rel => {
    const cat = edgeCategory(rel.type);
    const sourceRow = rowById.get(rel.source);
    const targetRow = rowById.get(rel.target);
    if (!sourceRow || !targetRow) return;

    const eventX = yearToX(rel.year);
    const y1 = sourceRow.y;
    const y2 = targetRow.y;

    let path = '';
    let labelX = eventX;
    let labelY = (y1 + y2) / 2 + 3;

    if (cat === 'ma') {
      const x1 = Math.min(sourceRow.endX, eventX);
      const x2 = eventX;
      const dx = Math.max(24, Math.abs(x2 - x1));
      path = `M ${x1} ${y1} C ${x1 + dx * 0.45} ${y1}, ${x2 - dx * 0.35} ${y2}, ${x2} ${y2}`;
      labelX = (x1 + x2) / 2;
    } else if (cat === 'oem') {
      const x1 = Math.max(sourceRow.startX, eventX - 22);
      const x2 = eventX;
      path = `M ${x1} ${y1} C ${x1 + 14} ${y1}, ${x2 - 14} ${y2}, ${x2} ${y2}`;
      labelX = (x1 + x2) / 2;
    } else {
      const offset = (edgeIdx % 2 === 0) ? 14 : -14;
      path = `M ${eventX} ${y1} Q ${eventX + offset} ${(y1 + y2) / 2} ${eventX} ${y2}`;
      labelX = eventX + offset * 0.65;
    }

    const relFileId = rel.id || `${rel.source}_${rel.target}`;
    edges.push({
      id: `edge-${edgeIdx++}`,
      relId: relFileId,
      sourceId: sourceRow.id,
      targetId: targetRow.id,
      sourceName: sourceRow.name,
      targetName: targetRow.name,
      year: rel.year,
      type: rel.type,
      subtype: rel.subtype || rel.type,
      category: cat,
      note: rel.note || '',
      sources: Array.isArray(rel.sources) ? rel.sources : [],
      path,
      labelX,
      labelY
    });
  });

  const totalHeight = Math.max(110, currentY - ROW_HEIGHT / 2 + BOTTOM_AXIS_HEIGHT + 8);
  return {
    rows,
    edges,
    axisYears,
    totalHeight,
    hasPreEra,
    minLinearYear,
    linearStartX,
    yearToX
  };
});

const hasPredecessor = computed(() => layout.value.rows.some(r => r.isPredecessor));
function hasEdgeCategory(cat) {
  return layout.value.edges.some(e => e.category === cat);
}

const isAnyHovered = computed(() => Boolean(hoveredRowId.value || hoveredEdge.value));

const highlightedRowIds = computed(() => {
  const set = new Set();
  if (hoveredRowId.value) {
    set.add(hoveredRowId.value);
    layout.value.edges.forEach(e => {
      if (e.sourceId === hoveredRowId.value) set.add(e.targetId);
      if (e.targetId === hoveredRowId.value) set.add(e.sourceId);
    });
  } else if (hoveredEdge.value) {
    set.add(hoveredEdge.value.sourceId);
    set.add(hoveredEdge.value.targetId);
  }
  return set;
});

function isRowHighlighted(rowId) {
  return highlightedRowIds.value.has(rowId);
}

function isEdgeHighlighted(edge) {
  if (hoveredEdge.value) return hoveredEdge.value.id === edge.id;
  if (hoveredRowId.value) {
    return edge.sourceId === hoveredRowId.value || edge.targetId === hoveredRowId.value;
  }
  return false;
}

function cancelHideTooltip() {
  if (hideTimer) {
    clearTimeout(hideTimer);
    hideTimer = null;
  }
}

function scheduleHideTooltip() {
  cancelHideTooltip();
  hideTimer = setTimeout(() => {
    hoveredRowId.value = null;
    hoveredEdge.value = null;
    tooltip.value.visible = false;
    tooltip.value.targetKey = '';
  }, 220);
}

function computeAnchoredPos(evt, svgY) {
  if (!wrapperRef.value || !scrollContainer.value) return { x: 20, y: 20 };
  const wrapperRect = wrapperRef.value.getBoundingClientRect();
  const scrollRect = scrollContainer.value.getBoundingClientRect();
  const offsetTop = scrollRect.top - wrapperRect.top;
  const relX = evt ? (evt.clientX - wrapperRect.left) : 260;
  const svgEl = scrollContainer.value.querySelector('svg');
  const scaleY = svgEl ? (svgEl.clientHeight / layout.value.totalHeight) : 1;
  const pixelY = offsetTop + (svgY || 40) * scaleY;
  return {
    x: Math.min(Math.max(12, relX - 50), Math.max(12, wrapperRect.width - 330)),
    y: Math.max(8, pixelY + 12)
  };
}

function onHoverRow(row, evt) {
  cancelHideTooltip();
  hoveredRowId.value = row.id;
  hoveredEdge.value = null;

  const key = `row-${row.id}`;
  // Only recompute position when switching to a different row so the popover stays stationary and reachable
  const pos = tooltip.value.targetKey === key
    ? { x: tooltip.value.x, y: tooltip.value.y }
    : computeAnchoredPos(evt, row.y);

  const stateMap = {
    active: { label: 'Active', cls: 'bg-success' },
    acquired: { label: `Acquired (${row.endYear})`, cls: 'bg-info text-dark' },
    merged: { label: `Merged (${row.endYear})`, cls: 'bg-info text-dark' },
    liquidated: { label: `Liquidated (${row.endYear})`, cls: 'bg-danger' },
    defunct: { label: `Assets Sold (${row.endYear})`, cls: 'bg-danger' },
    restructuring: { label: `Insolvent (${row.endYear})`, cls: 'bg-warning text-dark' }
  };
  const badgeInfo = stateMap[row.state] || { label: row.state, cls: 'bg-secondary' };

  tooltip.value = {
    visible: true,
    targetKey: key,
    x: pos.x,
    y: pos.y,
    title: row.name,
    subtitle: `${row.country ? row.country + ' · ' : ''}Founded ${row.foundedYear}`,
    badge: badgeInfo.label,
    badgeClass: badgeInfo.cls,
    body: row.statusNote || row.relationSummary || '',
    robots: row.robotDots || [],
    sources: row.sources || [],
    linkTo: (!row.isPredecessor && row.id !== props.focusCompanyId) ? `/company/${row.id}` : '',
    linkLabel: `View ${row.name}`,
    editGithubUrl: (row.isPredecessor && row.relId) ? `https://github.com/medmachina/medmachina.github.io/edit/main/public/relationships/${row.relId}.json` : ''
  };
}

function onHoverEdge(edge, evt) {
  cancelHideTooltip();
  hoveredEdge.value = edge;
  hoveredRowId.value = null;

  const key = `edge-${edge.id}`;
  const pos = tooltip.value.targetKey === key
    ? { x: tooltip.value.x, y: tooltip.value.y }
    : computeAnchoredPos(evt, edge.labelY);

  const catBadge = edge.category === 'ma'
    ? { label: edge.subtype, cls: 'bg-info text-dark' }
    : edge.category === 'oem'
      ? { label: edge.subtype, cls: 'bg-warning text-dark' }
      : { label: edge.subtype, cls: 'bg-primary' };

  const otherId = edge.sourceId === props.focusCompanyId ? edge.targetId : edge.sourceId;
  const otherRow = layout.value.rows.find(r => r.id === otherId);

  tooltip.value = {
    visible: true,
    targetKey: key,
    x: pos.x,
    y: pos.y,
    title: `${edge.sourceName} → ${edge.targetName}`,
    subtitle: `Year: ${edge.year}`,
    badge: catBadge.label,
    badgeClass: catBadge.cls,
    body: edge.note,
    robots: [],
    sources: edge.sources || [],
    linkTo: (otherRow && !otherRow.isPredecessor) ? `/company/${otherRow.id}` : '',
    linkLabel: otherRow ? `View ${otherRow.name}` : '',
    editGithubUrl: edge.relId ? `https://github.com/medmachina/medmachina.github.io/edit/main/public/relationships/${edge.relId}.json` : ''
  };
}

function onHoverRobot(rDot, row, evt) {
  cancelHideTooltip();
  hoveredRowId.value = row.id;

  const key = `robot-${rDot.id}`;
  const pos = tooltip.value.targetKey === key
    ? { x: tooltip.value.x, y: tooltip.value.y }
    : computeAnchoredPos(evt, row.y);

  tooltip.value = {
    visible: true,
    targetKey: key,
    x: pos.x,
    y: pos.y,
    title: rDot.name,
    subtitle: `${row.name} · Introduced ${rDot.year}`,
    badge: 'Robot System',
    badgeClass: 'bg-secondary',
    body: '',
    robots: [],
    sources: rDot.sources || [],
    linkTo: `/robot/${rDot.id}`,
    linkLabel: `View ${rDot.shortName}`,
    editGithubUrl: ''
  };
}

function onClickCompany(row) {
  if (row.isPredecessor || row.id === props.focusCompanyId) return;
  router.push(`/company/${row.id}`);
}

function onClickRobot(robotId) {
  router.push(`/robot/${robotId}`);
}

function truncateText(str, maxLen) {
  if (!str) return '';
  return str.length > maxLen ? str.slice(0, maxLen - 1) + '…' : str;
}
</script>

<style scoped>
.time-graph-wrapper {
  position: relative;
}

.svg-scroll-container {
  position: relative;
  overflow-x: auto;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.company-time-svg {
  width: 100%;
  min-width: 760px;
  height: auto;
  display: block;
  user-select: none;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.pre-era-band {
  fill: rgba(128, 128, 128, 0.06);
}

.axis-break-line {
  stroke: var(--color-border);
  stroke-width: 1.2;
}

.grid-line {
  stroke: var(--color-border);
  stroke-width: 1;
  stroke-dasharray: 2, 4;
  opacity: 0.5;
}

.axis-label {
  fill: var(--color-text);
  font-size: 10.5px;
  font-weight: 600;
  opacity: 0.7;
}

.row-bg {
  fill: transparent;
  pointer-events: none;
  transition: fill 0.15s ease, opacity 0.15s ease;
}

.row-highlighted {
  fill: rgba(56, 189, 248, 0.08);
}

.row-focused {
  fill: rgba(16, 185, 129, 0.1);
  stroke: rgba(16, 185, 129, 0.35);
  stroke-width: 1;
}

.row-dimmed {
  opacity: 0.28;
  transition: opacity 0.15s ease;
}

.company-name-text {
  fill: var(--color-heading);
  font-size: 11.5px;
  font-weight: 600;
}

.company-label-group:hover .company-name-text:not(.predecessor-name-text):not(.focused-name-text) {
  fill: #38bdf8;
  text-decoration: underline;
}

.predecessor-name-text {
  fill: var(--color-text);
  font-weight: 500;
  font-style: italic;
  font-size: 11px;
}

.focused-name-text {
  fill: #10b981;
  font-weight: 700;
}

.company-rel-sub {
  font-size: 9.5px;
  font-weight: 500;
  opacity: 0.85;
}

.rel-sub-ma {
  fill: #38bdf8;
}

.rel-sub-oem {
  fill: #f59e0b;
}

.rel-sub-collab {
  fill: #a855f7;
}

.company-year-sub {
  fill: var(--color-text);
  font-size: 10px;
  opacity: 0.65;
}

.lifespan-bar {
  stroke-width: 4;
  stroke-linecap: round;
  cursor: pointer;
  transition: stroke-width 0.15s ease;
}

.lifespan-bar:hover {
  stroke-width: 6;
}

.bar-active {
  stroke: #10b981;
}

.bar-acquired,
.bar-merged {
  stroke: #38bdf8;
}

.bar-predecessor {
  stroke: #38bdf8;
  stroke-dasharray: 5, 3;
  stroke-width: 3.2;
  opacity: 0.85;
}

.bar-liquidated,
.bar-defunct {
  stroke: #ef4444;
}

.bar-restructuring {
  stroke: #f59e0b;
}

.cap-active {
  fill: #10b981;
}

.cap-acquired,
.cap-merged,
.cap-predecessor {
  fill: #38bdf8;
}

.cap-liquidated,
.cap-defunct {
  fill: #ef4444;
}

.cap-restructuring {
  fill: #f59e0b;
}

.pre-era-tag {
  fill: var(--color-text);
  font-size: 9px;
  font-style: italic;
  opacity: 0.75;
}

.exit-circle-danger {
  fill: #ef4444;
}

.exit-circle-warn {
  fill: #f59e0b;
}

.exit-symbol {
  fill: #ffffff;
  font-size: 8.5px;
  font-weight: 800;
}

.exit-label {
  fill: #ef4444;
  font-size: 9.5px;
  font-weight: 600;
}

.ext-inline-text {
  font-size: 9.5px;
  font-weight: 600;
}

.ext-text-ma {
  fill: #38bdf8;
}

.ext-text-oem {
  fill: #f59e0b;
}

.ext-text-collab {
  fill: #a855f7;
}

.edge-group {
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.edge-dimmed {
  opacity: 0.18;
}

.edge-path {
  stroke-width: 2;
  transition: stroke-width 0.15s ease;
}

.edge-group:hover .edge-path,
.edge-highlighted .edge-path {
  stroke-width: 3.2;
}

.edge-ma {
  stroke: #38bdf8;
}

.edge-oem {
  stroke: #f59e0b;
  stroke-dasharray: 5, 3;
}

.edge-collab {
  stroke: #a855f7;
  stroke-dasharray: 2.5, 2.5;
}

.edge-year-halo {
  font-size: 9.5px;
  font-weight: 700;
  paint-order: stroke;
  stroke: var(--color-background-soft);
  stroke-width: 4px;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.edge-year-ma {
  fill: #38bdf8;
}

.edge-year-oem {
  fill: #f59e0b;
}

.edge-year-collab {
  fill: #a855f7;
}

.robot-dot-group {
  cursor: pointer;
}

.robot-dot {
  fill: var(--color-background);
  stroke: var(--color-heading);
  stroke-width: 1.8;
  transition: r 0.15s ease, fill 0.15s ease;
}

.robot-dot-group:hover .robot-dot {
  r: 5.8;
  fill: #38bdf8;
  stroke: #ffffff;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text);
}

.legend-bar {
  display: inline-block;
  width: 20px;
  height: 5px;
  border-radius: 3px;
}

.active-bar {
  background-color: #10b981;
}

.predecessor-bar {
  background: repeating-linear-gradient(90deg, #38bdf8 0, #38bdf8 5px, transparent 5px, transparent 8px);
}

.legend-line {
  display: inline-block;
  width: 22px;
  height: 0;
}

.line-ma {
  border-top: 2.5px solid #38bdf8;
}

.line-oem {
  border-top: 2.5px dashed #f59e0b;
}

.line-collab {
  border-top: 2.5px dotted #a855f7;
}

.legend-dot {
  display: inline-block;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background-color: var(--color-background);
  border: 2px solid var(--color-heading);
}

/* Interactive Reachable Tooltip */
.graph-tooltip {
  position: absolute;
  z-index: 40;
  max-width: 310px;
  pointer-events: auto;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 8px;
  padding: 0.65rem 0.8rem;
}

.tooltip-robot-pill:hover {
  background-color: #0d6efd !important;
  color: #fff !important;
}
</style>
