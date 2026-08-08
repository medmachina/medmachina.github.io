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
          manufacturers, and regulatory filings worldwide. We welcome contributions from researchers, engineers,
          clinicians, and industry experts.
        </p>
        <div class="d-flex flex-wrap gap-2 mt-3">
          <a href="https://github.com/medmachina/medmachina.github.io" target="_blank" class="btn btn-outline-primary btn-sm">
            <i class="bi bi-github me-1"></i> GitHub Repository
          </a>
          <a href="https://github.com/medmachina/medmachina.github.io/issues/new" target="_blank" class="btn btn-outline-success btn-sm">
            <i class="bi bi-plus-circle me-1"></i> Submit Data via Issue
          </a>
          <a href="#schema-reference" class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-code-slash me-1"></i> View Schema Reference
          </a>
        </div>
      </div>
    </div>

    <!-- Two Contribution Paths -->
    <div class="row g-4 mb-4">
      <div class="col-md-6">
        <div class="card h-100 border-primary-subtle">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="badge bg-primary fs-6 me-2">Path 1</div>
              <h3 class="card-title h5 mb-0">Git Pull Requests</h3>
            </div>
            <p class="card-text text-muted">
              Best for developers and data contributors comfortable with Git and JSON files. Add or modify individual robot and company JSON files directly.
            </p>
            <ul class="small text-muted ps-3 mb-0">
              <li>Edit standalone JSON files in <code>public/robots/</code> and <code>public/companies/</code></li>
              <li>Validate schema &amp; URLs with Python CLI tools</li>
              <li>Submit a GitHub Pull Request for review</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card h-100 border-success-subtle">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="badge bg-success fs-6 me-2">Path 2</div>
              <h3 class="card-title h5 mb-0">GitHub Issues (No Code Required)</h3>
            </div>
            <p class="card-text text-muted">
              Ideal for clinicians, researchers, or anyone discovering missing systems or incorrect information who prefers not to edit code.
            </p>
            <ul class="small text-muted ps-3 mb-0">
              <li>Report inaccurate or outdated information</li>
              <li>Request adding a new surgical robot or manufacturer</li>
              <li>Provide links to press releases or regulatory filings</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 1: Fork and Clone -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 1: Fork &amp; Clone the Repository</h2>
        <p class="card-text">
          Fork the <a href="https://github.com/medmachina/medmachina.github.io" target="_blank">MedMachina GitHub repository</a>
          to your GitHub account and clone it locally:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code>git clone https://github.com/YOUR_USERNAME/medmachina.github.io.git
cd medmachina.github.io</code></pre>
        <div class="alert alert-info custom-alert mt-3 mb-0">
          <i class="bi bi-info-circle me-2"></i>
          Requires Python 3.9+ for dataset build and verification scripts.
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
          <li><code>public/robots/&lt;robot_id&gt;.json</code> — Contains specifications, tags, URLs, and regulatory history for a surgical robot.</li>
          <li><code>public/companies/&lt;company_id&gt;.json</code> — Contains details, headquarters, website, and associated robot IDs for a manufacturer.</li>
        </ul>
        <div class="alert alert-warning custom-alert mb-0">
          <i class="bi bi-exclamation-triangle me-2"></i>
          <strong>Important:</strong> Do <em>not</em> edit <code>public/robots.json</code> or <code>public/companies.json</code> manually. These aggregated files are automatically generated by build scripts.
        </div>
      </div>
    </div>

    <!-- Step 3: Run Build & Automation Scripts -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 3: Build &amp; Enrich Datasets</h2>
        <p class="card-text">
          After adding or modifying files in <code>public/robots/</code> or <code>public/companies/</code>, aggregate them into the main dataset files:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code># Compile individual JSON files into public/robots.json and public/companies.json
python3 scripts/build_robots.py
python3 scripts/build_companies.py</code></pre>
        <p class="card-text text-muted mt-2">
          Note: <code>build_robots.py</code> automatically populates the <code>db_added</code> field (YYYY-MM-DD) from Git commit dates.
        </p>

        <h5 class="mt-4">Automated Regulatory Lookup (FDA Data)</h5>
        <p class="card-text">
          You can automatically query OpenFDA to pull 510(k) and PMA clearances for a robot using its ID:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code>python3 scripts/download_fda_data.py --robot &lt;ROBOT_ID&gt; --yes</code></pre>
      </div>
    </div>

    <!-- Step 4: Validate Data & Links -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 4: Verify Schema &amp; Link Validity</h2>
        <p class="card-text">
          Run verification scripts to test your JSON files against official schemas and check that all HTTP URLs and photo links are accessible:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code># Validate robot JSON schema conformance and URL accessibility
python3 scripts/update_robots.py --verify-only

# Validate company JSON schema conformance and URLs
python3 scripts/update_companies.py --verify-only</code></pre>
      </div>
    </div>

    <!-- Step 5: Commit & PR -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Step 5: Commit &amp; Submit Pull Request</h2>
        <p class="card-text">
          Stage your new standalone JSON files along with the re-compiled aggregate datasets:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code>git checkout -b add-new-robot
git add public/robots/company_robot.json public/companies/company.json public/robots.json public/companies.json
git commit -m "feat(robot): add [Robot Name] entry"
git push origin add-new-robot</code></pre>
        <p class="card-text mt-3">
          Open a <a href="https://github.com/medmachina/medmachina.github.io/pulls" target="_blank">Pull Request</a> on GitHub, referencing primary sources (manufacturer website, press release, FDA clearance) in the PR description.
        </p>
      </div>
    </div>

    <!-- Schema Reference Section -->
    <div id="schema-reference" class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4 mb-3">Dataset Schema Reference</h2>

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
        </ul>

        <!-- Robot Schema Tab -->
        <div v-if="activeTab === 'robot'">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="text-muted small">Target path: <code>public/robots/&lt;robot_id&gt;.json</code></span>
            <button @click="copyRobotSnippet" class="btn btn-outline-secondary btn-sm">
              <i class="bi bi-clipboard me-1"></i> {{ copiedRobot ? 'Copied!' : 'Copy JSON' }}
            </button>
          </div>
          <pre class="bg-dark text-light p-3 rounded"><code>{{ robotSampleJson }}</code></pre>

          <h5 class="mt-4">Supported Robot Tags</h5>
          <p class="small text-muted">Assign tags from the defined schema definitions:</p>
          <div class="d-flex flex-wrap gap-1 mb-3">
            <span v-for="t in tagList" :key="t" class="badge bg-secondary me-1 mb-1">{{ t }}</span>
          </div>

          <h5 class="mt-3">Supported Anatomical Usages</h5>
          <div class="d-flex flex-wrap gap-1 mb-3">
            <span v-for="u in usageList" :key="u" class="badge bg-info text-dark me-1 mb-1">{{ u }}</span>
          </div>
        </div>

        <!-- Company Schema Tab -->
        <div v-if="activeTab === 'company'">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="text-muted small">Target path: <code>public/companies/&lt;company_id&gt;.json</code></span>
            <button @click="copyCompanySnippet" class="btn btn-outline-secondary btn-sm">
              <i class="bi bi-clipboard me-1"></i> {{ copiedCompany ? 'Copied!' : 'Copy JSON' }}
            </button>
          </div>
          <pre class="bg-dark text-light p-3 rounded"><code>{{ companySampleJson }}</code></pre>
        </div>
      </div>
    </div>

    <!-- Contribution Guidelines -->
    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title h4">Quality Guidelines</h2>
        <ul class="card-text mb-0">
          <li><strong>Unique IDs:</strong> Use lowercase alphanumeric characters and underscores (e.g. <code>company_robotname</code>).</li>
          <li><strong>Direct Image URLs:</strong> Provide direct high-resolution image URLs in <code>photos</code>, referencing the source webpage in <code>site</code>.</li>
          <li><strong>Bi-directional References:</strong> When adding a new robot, ensure the manufacturer entry in <code>public/companies/</code> includes the robot's ID in its <code>robots</code> array.</li>
          <li><strong>Accurate Sources:</strong> Include official manufacturer URLs, press releases, or regulatory registration links.</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref<'robot' | 'company'>('robot')
const copiedRobot = ref(false)
const copiedCompany = ref(false)

const tagList = [
  'RAMIS', 'Commercial', 'Teleoperated', 'Multiple ports', '3+ instruments',
  'Stereo endoscope', 'Mechanical Cartesian manipulation', 'Stereo viewer',
  'Single patient cart', 'Haptic', 'Wristed instruments', 'Snake-like instruments',
  'Open surgery', 'Mechanical RCM', 'Retired', 'Orthopedic', 'Multiple patient carts',
  'Stereo display', 'Haptic device', 'Motorized table', 'Single port', '2 instruments',
  'Collaborative control', 'Force feedback', 'Mono endoscope', 'Mechanical manipulation',
  'Open console', 'Research system', 'Software RCM', 'Semi-autonomous', 'Open source',
  'Open architecture', 'Free hand manipulation', 'Autonomous', 'Simulation',
  'Flexible robot', 'Open microsurgery', 'Biopsy', 'TRUS', 'Dental', 'Autonomous motion', 'OEM component'
]

const usageList = [
  'Abdominal', 'Urological', 'Gynecological', 'Transoral', 'Knee', 'Hip', 'Shoulder',
  'Lung', 'Bronchoscopy', 'Thoracic', 'Spine', 'Eye', 'Prostate', 'Dental implant',
  'Neurological', 'Microsurgery'
]

const robotSampleJson = JSON.stringify({
  id: "company_robotname",
  name: "Example Surgical Robot",
  introduction_year: 2024,
  description: "Detailed summary of system kinematics, patient side cart, and clinical focus.",
  urls: [
    { caption: "Manufacturer Page", url: "https://example.com/robot" }
  ],
  photos: [
    { url: "https://example.com/images/robot.jpg", site: "https://example.com/robot" }
  ],
  videos: [
    { title: "System Overview", url: "https://www.youtube.com/watch?v=EXAMPLE" }
  ],
  tags: ["RAMIS", "Teleoperated", "Commercial"],
  usages: ["Abdominal", "Urological"],
  regulatory: [
    { body: "FDA", year: 2024, url: "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K123456" }
  ]
}, null, 2)

const companySampleJson = JSON.stringify({
  id: "company_name",
  name: "Example Robotics Inc",
  country: "United States",
  founded_year: "2015",
  company_type: "Public",
  employee_count: "50-200",
  description: "Company background and headquarters location.",
  urls: [
    { caption: "Official Website", url: "https://example.com" }
  ],
  linkedin_url: "https://www.linkedin.com/company/example-robotics",
  robots: ["company_robotname"]
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