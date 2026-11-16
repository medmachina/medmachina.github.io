<template>
  <div class="container">
    <!-- Header -->
    <div class="header-with-logo d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="mb-1 title">How to Contribute</h1>
        <p class="text-muted mb-0">Help build and refine the open-source medical and surgical robotics directory</p>
      </div>
      <router-link to="/" style="display: flex; align-items: center; text-decoration: none;">
        <img src="/text-logo.svg" alt="medmachina logo" class="global-logo" />
      </router-link>
    </div>

    <!-- Introduction Card -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Welcome to Med Machina</h2>
        <p class="card-text">
          Med Machina is an open-source, community-maintained database of medical and surgical robotics systems,
          manufacturers, corporate relationships, and regulatory filings worldwide. We welcome contributions from researchers,
          engineers, clinicians, and industry experts.
        </p>
        <div class="d-flex flex-wrap gap-2 mt-3">
          <a href="https://github.com/medmachina/medmachina.github.io" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary btn-sm">
            <i class="bi bi-github me-1"></i> GitHub Repository
          </a>
          <a href="https://github.com/medmachina/medmachina.github.io/issues/new" target="_blank" rel="noopener noreferrer" class="btn btn-outline-success btn-sm">
            <i class="bi bi-plus-circle me-1"></i> Submit Data via Issue
          </a>
          <a href="#schema-reference" class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-code-slash me-1"></i> View Schema Reference
          </a>
        </div>
      </div>
    </div>

    <!-- Three Contribution Paths -->
    <div class="row g-4 mb-4">
      <!-- Path 1: Edit on GitHub button -->
      <div class="col-md-4">
        <div class="card h-100 border-info-subtle">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="badge bg-info text-dark fs-6 me-2">Quickest</div>
              <h3 class="card-title h5 mb-0">"Edit on GitHub" Button</h3>
            </div>
            <p class="card-text text-muted">
              Fastest way to fix typos, add missing URLs, or update info for an existing robot, company, or relationship directly in your browser.
            </p>
            <ul class="small text-muted ps-3 mb-0">
              <li>Click <strong>"Edit on GitHub"</strong> at the bottom right of any detail page (or in Company Time Graph tooltips)</li>
              <li>GitHub automatically forks the repository into your account</li>
              <li>Edit the JSON file online &amp; click <strong>"Propose changes"</strong> to open a PR</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Path 2: Full Git Pull Request -->
      <div class="col-md-4">
        <div class="card h-100 border-primary-subtle">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="badge bg-primary fs-6 me-2">Developer</div>
              <h3 class="card-title h5 mb-0">Local Git &amp; PR Workflow</h3>
            </div>
            <p class="card-text text-muted">
              Best for adding new robot, company, or relationship entries, running automated FDA lookup scripts, and validating schemas locally.
            </p>
            <ul class="small text-muted ps-3 mb-0">
              <li>Clone your fork and edit <code>public/robots/</code>, <code>public/companies/</code>, or <code>public/relationships/</code></li>
              <li>Run Python build and schema validation tools</li>
              <li>Submit a Pull Request on GitHub</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Path 3: GitHub Issues -->
      <div class="col-md-4">
        <div class="card h-100 border-success-subtle">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="badge bg-success fs-6 me-2">No Code</div>
              <h3 class="card-title h5 mb-0">GitHub Issues</h3>
            </div>
            <p class="card-text text-muted">
              Ideal for clinicians, researchers, or anyone discovering missing systems who prefers not to edit code directly.
            </p>
            <ul class="small text-muted ps-3 mb-0">
              <li>Report inaccurate or outdated information</li>
              <li>Request adding a new surgical robot, manufacturer, or M&amp;A / OEM relationship</li>
              <li>Provide links to press releases or regulatory filings</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Web Editing Explainer -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Web-Based Quick Editing ("Edit on GitHub")</h2>
        <p class="card-text">
          Every robot and company detail page includes a floating <strong>"Edit on GitHub"</strong> button in the bottom-right corner,
          and Company Time Graph tooltips include links to edit individual relationship files. When you click it:
        </p>
        <ol class="card-text">
          <li>GitHub opens the exact raw JSON file (e.g. <code>public/robots/intuitive_da_vinci_5.json</code> or <code>public/relationships/mako_surgical_stryker.json</code>) in their online editor.</li>
          <li>If you do not have write permissions, GitHub automatically forks the repository to your GitHub account behind the scenes.</li>
          <li>Make your changes in the online editor, then click the green <strong>"Propose changes"</strong> button at the bottom.</li>
          <li>GitHub automatically creates a pull request to the main repository for maintainers to review!</li>
        </ol>
      </div>
    </div>

    <!-- Step 1: Fork and Clone -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 1: Fork &amp; Clone for Local Development</h2>
        <p class="card-text">
          For adding new entries or running local validation scripts, fork the <a href="https://github.com/medmachina/medmachina.github.io" target="_blank" rel="noopener noreferrer">MedMachina GitHub repository</a>
          and clone it locally:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code>git clone https://github.com/YOUR_USERNAME/medmachina.github.io.git
cd medmachina.github.io
npm install</code></pre>
        <div class="alert alert-info custom-alert mt-3 mb-0">
          <i class="bi bi-info-circle me-2"></i>
          Requires Python 3.9+ for dataset build/validation scripts (install optional verification dependencies with <code>pip install -r requirements.txt</code>) and Node.js for <code>npm run build</code>.
        </div>
      </div>
    </div>

    <!-- Step 2: Edit Data Files -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 2: Create or Modify Individual JSON Files</h2>
        <p class="card-text">
          Data entries are maintained as individual JSON files under the <code>/public/</code> directory:
        </p>
        <ul>
          <li><code>public/robots/&lt;robot_id&gt;.json</code> — Contains specifications, categories, tags, anatomical usages, media, URLs, lifecycle status, and regulatory history for a surgical robot.</li>
          <li><code>public/companies/&lt;company_id&gt;.json</code> — Contains details, headquarters, website, stock ticker, patents, status, and associated robot IDs for a manufacturer.</li>
          <li><code>public/relationships/&lt;source&gt;_&lt;target&gt;.json</code> — Contains corporate M&amp;A, OEM component supply, and collaboration/JV/licensing relationships between companies (visualized in the Company Time Graph), with mandatory source URLs.</li>
        </ul>
        <div class="alert alert-warning custom-alert mb-0">
          <i class="bi bi-exclamation-triangle me-2"></i>
          <strong>Important:</strong> Do <em>not</em> edit <code>public/robots.json</code>, <code>public/companies.json</code>, or <code>public/relationships.json</code> manually. These aggregated files are gitignored and automatically generated by build scripts.
        </div>
      </div>
    </div>

    <!-- Step 3: Run Build & Automation Scripts -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 3: Build &amp; Enrich Datasets</h2>
        <p class="card-text">
          After adding or modifying files in <code>public/robots/</code>, <code>public/companies/</code>, or <code>public/relationships/</code>, aggregate them into the compiled dataset files:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code># Compile individual JSON files into public/robots.json, public/companies.json, and public/relationships.json
python3 scripts/build_robots.py
python3 scripts/build_companies.py
python3 scripts/build_relationships.py

# Or run the full production build (runs all three builders, builds Vite assets, and updates SEO/sitemap)
npm run build</code></pre>
        <p class="card-text text-muted mt-2">
          Note: <code>build_robots.py</code> automatically populates the <code>db_added</code> field (<code>YYYY-MM-DD</code>) from Git commit dates.
        </p>

        <h5 class="mt-4">Automated Regulatory Lookup (FDA Data)</h5>
        <p class="card-text">
          You can automatically query OpenFDA to pull 510(k) and PMA clearances for a robot using its ID:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code>python3 scripts/download_fda_data.py --robot &lt;ROBOT_ID&gt; --yes</code></pre>
        <p class="small text-muted mb-0">
          When adding FDA De Novo records manually, always use the <code>?ID=DENxxxxxx</code> query parameter format
          (e.g. <code>https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/denovo.cfm?ID=DENxxxxxx</code>).
        </p>
      </div>
    </div>

    <!-- Step 4: Validate Data & Links -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 4: Verify Schema &amp; Link Validity</h2>
        <p class="card-text">
          Run the verification scripts to test your JSON files against all official JSON Schemas
          (<a href="/robots.schema.json" target="_blank" rel="noopener noreferrer"><code>robots.schema.json</code></a>,
          <a href="/companies.schema.json" target="_blank" rel="noopener noreferrer"><code>companies.schema.json</code></a>, and
          <a href="/relationships.schema.json" target="_blank" rel="noopener noreferrer"><code>relationships.schema.json</code></a>),
          verify URL accessibility, and check prose cross-link consistency:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code># Validate robot JSON against public/robots.schema.json and check URL accessibility
python3 scripts/update_robots.py --verify-only

# Validate company JSON against public/companies.schema.json and check URLs
python3 scripts/update_companies.py --verify-only

# Validate relationship JSON against public/relationships.schema.json, source URLs, and prose cross-links
python3 scripts/build_relationships.py</code></pre>
      </div>
    </div>

    <!-- Step 5: Commit & PR -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 5: Commit &amp; Submit Pull Request</h2>
        <p class="card-text">
          Stage your new or modified standalone JSON files (do not stage the gitignored aggregate files <code>robots.json</code>, <code>companies.json</code>, or <code>relationships.json</code>):
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code>git checkout -b add-new-robot
git add public/robots/company_robot.json public/companies/company.json public/relationships/partner_company_company.json
git commit -m "feat(robot): add [Robot Name] entry"
git push origin add-new-robot</code></pre>
        <p class="card-text mt-3">
          Open a <a href="https://github.com/medmachina/medmachina.github.io/pulls" target="_blank" rel="noopener noreferrer">Pull Request</a> on GitHub, referencing primary sources (manufacturer website, press release, FDA clearance) in the PR description.
        </p>
      </div>
    </div>

    <!-- Schema Reference Section -->
    <div id="schema-reference" class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4 mb-2">Dataset Schema Reference</h2>
        <p class="text-muted small mb-3">
          All dataset entries conform to JSON Schema Draft 2020-12 definitions stored in <code>public/</code>:
        </p>
        <div class="d-flex flex-wrap gap-2 mb-4">
          <a href="/robots.schema.json" target="_blank" rel="noopener noreferrer" class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-file-earmark-code me-1"></i> robots.schema.json
          </a>
          <a href="/companies.schema.json" target="_blank" rel="noopener noreferrer" class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-file-earmark-code me-1"></i> companies.schema.json
          </a>
          <a href="/relationships.schema.json" target="_blank" rel="noopener noreferrer" class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-file-earmark-code me-1"></i> relationships.schema.json
          </a>
        </div>

        <!-- Tabs -->
        <ul class="nav nav-tabs mb-3">
          <li class="nav-item">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'robot' }"
              @click="activeTab = 'robot'"
            >
              Robot JSON Format
            </button>
          </li>
          <li class="nav-item">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'company' }"
              @click="activeTab = 'company'"
            >
              Company JSON Format
            </button>
          </li>
          <li class="nav-item">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'relationship' }"
              @click="activeTab = 'relationship'"
            >
              Relationship JSON Format
            </button>
          </li>
        </ul>

        <!-- Robot Schema Tab -->
        <div v-if="activeTab === 'robot'">
          <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
            <span class="text-muted small">
              Target path: <code>public/robots/&lt;robot_id&gt;.json</code> &middot;
              Schema: <a href="/robots.schema.json" target="_blank" rel="noopener noreferrer"><code>public/robots.schema.json</code></a>
              (<a href="https://github.com/medmachina/medmachina.github.io/blob/main/public/robots.schema.json" target="_blank" rel="noopener noreferrer">GitHub</a>)
            </span>
            <button @click="copyRobotSnippet" class="btn btn-outline-secondary btn-sm">
              <i class="bi bi-clipboard me-1"></i> {{ copiedRobot ? 'Copied!' : 'Copy JSON' }}
            </button>
          </div>
          <pre class="bg-dark text-light p-3 rounded"><code>{{ robotSampleJson }}</code></pre>
          <p class="small text-muted mb-3">
            Note: <code>db_added</code> is automatically injected by <code>scripts/build_robots.py</code> from the file's Git commit date.
            <code>publications</code> is optional—only include peer-reviewed papers that directly use or evaluate the specific system.
          </p>

          <h5 class="mt-4">Supported Robot Categories</h5>
          <p class="small text-muted">Assign one or more categories from <code>robots.schema.json</code> (hover for descriptions):</p>
          <div class="d-flex flex-wrap gap-1 mb-3">
            <span v-for="c in categoryList" :key="c.name" class="badge me-1 mb-1" style="background-color: #4c3575; color: #fff; border-radius: 1rem; padding: 0.25rem 0.6rem; cursor: help;" :title="c.description">{{ c.name }}</span>
          </div>

          <h5 class="mt-3">Supported Robot Tags</h5>
          <p class="small text-muted">Assign tags from <code>robots.schema.json</code> (hover for descriptions):</p>
          <div class="d-flex flex-wrap gap-1 mb-3">
            <span v-for="t in tagList" :key="t.name" class="badge bg-secondary me-1 mb-1" :title="t.description" style="cursor: help;">{{ t.name }}</span>
          </div>

          <h5 class="mt-3">Supported Anatomical Usages</h5>
          <p class="small text-muted">Assign anatomical or clinical applications from <code>robots.schema.json</code> (hover for descriptions):</p>
          <div class="d-flex flex-wrap gap-1 mb-3">
            <span v-for="u in usageList" :key="u.name" class="badge bg-info text-dark me-1 mb-1" :title="u.description" style="cursor: help;">{{ u.name }}</span>
          </div>

          <h5 class="mt-3">Supported Lifecycle Statuses</h5>
          <p class="small text-muted">Values allowed for <code>lifecycle.status</code> in <code>robots.schema.json</code>:</p>
          <div class="d-flex flex-wrap gap-1 mb-1">
            <span v-for="s in lifecycleStatusList" :key="s" class="badge bg-light text-dark border me-1 mb-1">{{ s }}</span>
          </div>
        </div>

        <!-- Company Schema Tab -->
        <div v-if="activeTab === 'company'">
          <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
            <span class="text-muted small">
              Target path: <code>public/companies/&lt;company_id&gt;.json</code> &middot;
              Schema: <a href="/companies.schema.json" target="_blank" rel="noopener noreferrer"><code>public/companies.schema.json</code></a>
              (<a href="https://github.com/medmachina/medmachina.github.io/blob/main/public/companies.schema.json" target="_blank" rel="noopener noreferrer">GitHub</a>)
            </span>
            <button @click="copyCompanySnippet" class="btn btn-outline-secondary btn-sm">
              <i class="bi bi-clipboard me-1"></i> {{ copiedCompany ? 'Copied!' : 'Copy JSON' }}
            </button>
          </div>
          <pre class="bg-dark text-light p-3 rounded"><code>{{ companySampleJson }}</code></pre>
          <p class="small text-muted mb-3">
            Note: <code>founded_year</code> is an integer (e.g. <code>2015</code>) and <code>country</code> uses the full English country name (e.g. <code>"United States"</code>, <code>"South Korea"</code>).
            <code>stock</code>, <code>subsidiaries</code>, <code>opencorporates_url</code>, and <code>patents</code> are optional.
            For <code>acquired</code> or <code>merged</code> companies, include <code>status.successor</code> and a corresponding entry in <code>public/relationships/</code>.
          </p>

          <h5 class="mt-3">Supported Company Status States</h5>
          <p class="small text-muted">Values allowed for <code>status.state</code> in <code>companies.schema.json</code>:</p>
          <div class="d-flex flex-wrap gap-1 mb-1">
            <span v-for="st in companyStatusList" :key="st" class="badge bg-light text-dark border me-1 mb-1">{{ st }}</span>
          </div>
        </div>

        <!-- Relationship Schema Tab -->
        <div v-if="activeTab === 'relationship'">
          <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
            <span class="text-muted small">
              Target path: <code>public/relationships/&lt;source&gt;_&lt;target&gt;.json</code> &middot;
              Schema: <a href="/relationships.schema.json" target="_blank" rel="noopener noreferrer"><code>public/relationships.schema.json</code></a>
              (<a href="https://github.com/medmachina/medmachina.github.io/blob/main/public/relationships.schema.json" target="_blank" rel="noopener noreferrer">GitHub</a>)
            </span>
            <button @click="copyRelationshipSnippet" class="btn btn-outline-secondary btn-sm">
              <i class="bi bi-clipboard me-1"></i> {{ copiedRelationship ? 'Copied!' : 'Copy JSON' }}
            </button>
          </div>
          <pre class="bg-dark text-light p-3 rounded"><code>{{ relationshipSampleJson }}</code></pre>

          <h5 class="mt-4">Predecessor or External Entity Example</h5>
          <p class="small text-muted">
            When <code>source</code> or <code>target</code> does not have its own file in <code>public/companies/</code> (e.g. an acquired predecessor or external distribution partner),
            provide <code>source_name</code> (and optionally <code>source_founded_year</code>) or <code>target_name</code>:
          </p>
          <div class="d-flex justify-content-end mb-2">
            <button @click="copyRelationshipExternalSnippet" class="btn btn-outline-secondary btn-sm">
              <i class="bi bi-clipboard me-1"></i> {{ copiedRelationshipExternal ? 'Copied!' : 'Copy JSON' }}
            </button>
          </div>
          <pre class="bg-dark text-light p-3 rounded"><code>{{ relationshipExternalSampleJson }}</code></pre>

          <h5 class="mt-4">Supported Relationship Types</h5>
          <p class="small text-muted">Allowed values for <code>type</code> in <code>relationships.schema.json</code>:</p>
          <ul class="small mb-0">
            <li v-for="rt in relationshipTypeList" :key="rt.name" class="mb-1">
              <code>{{ rt.name }}</code> — {{ rt.description }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Contribution Guidelines -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Quality &amp; Editorial Guidelines</h2>
        <ul class="card-text mb-0">
          <li><strong>Unique IDs:</strong> Use lowercase snake_case identifiers (e.g. <code>company_robotname</code>, <code>company_name</code>, <code>source_target</code>).</li>
          <li><strong>Neutral, Technical Style:</strong> Write concise, objective descriptions highlighting kinematics, degrees of freedom, optics, console layout, and regulatory milestones without marketing superlatives.</li>
          <li><strong>Full Source URLs Required:</strong> Every factual entry must include full <code>https://...</code> URLs in <code>urls</code>, <code>regulatory[].url</code>, <code>lifecycle.source_url</code>, <code>units_deployed.source_url</code>, <code>status.source_url</code>, and <code>sources</code> (for relationships).</li>
          <li><strong>Bi-directional &amp; Prose Cross-Links:</strong> List each robot ID in its manufacturer's <code>robots</code> array, link first mentions of companies (<code>[Name](/company/company_id)</code>) and robots (<code>[Name](/robot/robot_id)</code>) in <code>description</code> text, and keep prose mentions of M&amp;A, OEM hardware, or partnerships synchronized with <code>public/relationships/</code>.</li>
          <li><strong>Direct Image URLs:</strong> Provide direct high-resolution image URLs in <code>photos</code>, referencing the source webpage in <code>site</code>.</li>
          <li><strong>Standardized Countries:</strong> Always use full English country names (e.g. <code>"United States"</code>, <code>"South Korea"</code>).</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import robotsSchema from '../../public/robots.schema.json'
import companiesSchema from '../../public/companies.schema.json'
import relationshipsSchema from '../../public/relationships.schema.json'

const activeTab = ref<'robot' | 'company' | 'relationship'>('robot')
const copiedRobot = ref(false)
const copiedCompany = ref(false)
const copiedRelationship = ref(false)
const copiedRelationshipExternal = ref(false)

interface SchemaItem {
  name: string
  description?: string
}

const categoryList: SchemaItem[] = (robotsSchema.$defs?.Category?.oneOf || []).map((c: any) => ({
  name: c.const,
  description: c.description
}))

const tagList: SchemaItem[] = (robotsSchema.$defs?.Tag?.oneOf || []).map((t: any) => ({
  name: t.const,
  description: t.description
}))

const usageList: SchemaItem[] = (robotsSchema.$defs?.Usage?.oneOf || []).map((u: any) => ({
  name: u.const,
  description: u.description
}))

const lifecycleStatusList: string[] = robotsSchema.$defs?.LifecycleEntry?.properties?.status?.enum || []

const companyStatusList: string[] = companiesSchema.$defs?.CompanyStatusEntry?.properties?.state?.enum || []

const relationshipTypeList: SchemaItem[] = (relationshipsSchema.$defs?.RelationshipType?.oneOf || []).map((r: any) => ({
  name: r.const,
  description: r.description
}))

const robotSampleJson = JSON.stringify({
  id: "company_robotname",
  name: "Example Surgical Robot",
  categories: ["RAMIS"],
  also_known_as: ["EX-1000"],
  introduction_year: 2024,
  description: "Multiport teleoperated surgical system developed by [Example Robotics Inc](/company/company_name) featuring a single patient-side cart, four articulated arms with mechanical RCM, and 7-DOF wristed instruments.",
  urls: [
    { caption: "Manufacturer Product Page", url: "https://example.com/robot" }
  ],
  photos: [
    { url: "https://example.com/images/robot.jpg", site: "https://example.com/robot" }
  ],
  videos: [
    { title: "System Overview", url: "https://www.youtube.com/watch?v=EXAMPLE" }
  ],
  tags: ["Teleoperated", "Single patient cart", "Multiple ports", "3+ instruments", "Wristed instruments", "Commercial"],
  usages: ["Abdominal", "Urological"],
  regulatory: [
    {
      body: "FDA 510k",
      year: 2024,
      url: "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K123456",
      product_code: "NAY",
      panel: "SU"
    }
  ],
  units_deployed: {
    count: 120,
    source_url: "https://example.com/press-release"
  },
  publications: [
    {
      title: "Initial clinical evaluation of the Example Surgical Robot in urological procedures",
      url: "https://doi.org/10.1000/example",
      year: 2025,
      journal: "Journal of Robotic Surgery",
      doi: "10.1000/example"
    }
  ],
  lifecycle: {
    status: "active",
    year: 2024,
    note: "Commercial release in cleared markets.",
    source_url: "https://example.com/press-release"
  }
}, null, 2)

const companySampleJson = JSON.stringify({
  id: "company_name",
  name: "Example Robotics Inc",
  country: "United States",
  founded_year: 2015,
  company_type: "Public",
  employee_count: "50-200",
  description: "Example Robotics Inc develops the [Example Surgical Robot](/robot/company_robotname) multiport laparoscopic system from its headquarters in Boston, Massachusetts, integrating haptic master controllers from [Partner Robotics](/company/partner_company).",
  status: {
    state: "active",
    year: 2015,
    note: "Operating headquarters in Boston, MA.",
    source_url: "https://example.com/about"
  },
  stock: {
    ticker: "NASDAQ: EXMP",
    cnbc_symbol: "EXMP",
    url: "https://finance.yahoo.com/quote/EXMP/"
  },
  urls: [
    { caption: "Official Website", url: "https://example.com" }
  ],
  linkedin_url: "https://www.linkedin.com/company/example-robotics/",
  opencorporates_url: "https://opencorporates.com/companies/us_de/1234567",
  robots: ["company_robotname"],
  subsidiaries: ["Example Robotics Corp."],
  patents: {
    assignee_names: ["Example Robotics Inc"],
    google_patents_url: "https://patents.google.com/?assignee=%22Example+Robotics+Inc%22",
    lens_url: "https://www.lens.org/lens/search/patent/list?q=applicant%3A%22Example%20Robotics%20Inc%22"
  }
}, null, 2)

const relationshipSampleJson = JSON.stringify({
  id: "partner_company_company_name",
  source: "partner_company",
  target: "company_name",
  type: "oem",
  subtype: "Haptic Master OEM",
  year: 2024,
  note: "Supplies dual 7-DOF haptic master controllers integrated into the Example Surgical Robot surgeon console.",
  sources: [
    "https://partner.example.com/products/haptic-master",
    "https://example.com/robot"
  ]
}, null, 2)

const relationshipExternalSampleJson = JSON.stringify({
  id: "predecessor_co_company_name",
  source: "predecessor_co",
  source_name: "Predecessor Robotics",
  source_founded_year: 2008,
  target: "company_name",
  type: "acquired",
  subtype: "Asset Acquisition",
  year: 2021,
  note: "Acquired intellectual property and platform assets of Predecessor Robotics (founded 2008) in 2021.",
  sources: [
    "https://example.com/press-release-acquisition"
  ]
}, null, 2)

function copyRobotSnippet() {
  navigator.clipboard.writeText(robotSampleJson).then(() => {
    copiedRobot.value = true
    setTimeout(() => { copiedRobot.value = false }, 2000)
  })
}

function copyCompanySnippet() {
  navigator.clipboard.writeText(companySampleJson).then(() => {
    copiedCompany.value = true
    setTimeout(() => { copiedCompany.value = false }, 2000)
  })
}

function copyRelationshipSnippet() {
  navigator.clipboard.writeText(relationshipSampleJson).then(() => {
    copiedRelationship.value = true
    setTimeout(() => { copiedRelationship.value = false }, 2000)
  })
}

function copyRelationshipExternalSnippet() {
  navigator.clipboard.writeText(relationshipExternalSampleJson).then(() => {
    copiedRelationshipExternal.value = true
    setTimeout(() => { copiedRelationshipExternal.value = false }, 2000)
  })
}
</script>

<style scoped>
.card {
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 8px;
}

.title {
  color: var(--color-heading);
}

a {
  color: var(--color-primary, #0d6efd);
}

pre {
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.875rem;
}

code {
  font-family: monospace;
}

.alert {
  background-color: rgba(var(--color-primary-rgb, 13, 110, 253), 0.1);
  border-left: 4px solid var(--color-primary, #0d6efd);
  padding: 0.85rem 1rem;
  border-radius: 4px;
}

.custom-alert {
  background-color: var(--color-background-soft);
  color: var(--color-text);
  border-left: 4px solid var(--color-primary, #0d6efd);
  border-radius: 4px;
}

.nav-tabs {
  border-bottom-color: var(--color-border);
}

.nav-tabs .nav-link {
  color: var(--color-text);
  border: 1px solid transparent;
}

.nav-tabs .nav-link.active {
  background-color: var(--color-background-soft);
  color: var(--color-heading);
  border-color: var(--color-border) var(--color-border) transparent;
  font-weight: 600;
}
</style>
