<template>
  <div class="container">
    <div class="header-with-logo d-flex align-items-center justify-content-between mb-4">
      <h1 class="mb-0 title">How to Contribute</h1>
      <router-link to="/" style="display: flex; align-items: center; text-decoration: none;">
        <img src="/text-logo.svg" alt="medmachina" style="height:41px; width:auto;" />
      </router-link>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Contributing to Med Machina</h2>
        <p class="card-text">
          We welcome contributions to Med Machina. This guide will help you understand
          how to contribute by adding or updating robot and company information in our database.
        </p>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Step 1: Fork the Repository</h2>
        <p class="card-text">
          Start by forking the <a href="https://github.com/medmachina/medmachina.github.io" target="_blank">MedMachina GitHub repository</a>
          to your own GitHub account.
        </p>
        <div class="alert alert-info custom-alert">
          <i class="bi bi-info-circle me-2"></i>
          You'll need a GitHub account to fork the repository and submit a pull request.
        </div>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Step 2: Clone Your Fork</h2>
        <p class="card-text">
          Clone your forked repository to your local machine:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code>git clone https://github.com/YOUR_USERNAME/medmachina.github.io.git
cd medmachina.github.io</code></pre>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Step 3: Edit the Data Files</h2>
        <p class="card-text">
          The main data files are located in the <code>/public/</code> folder:
        </p>
        <ul>
          <li><code>robots.json</code> - Contains information about medical robots</li>
          <li><code>companies.json</code> - Contains information about companies that manufacture robots</li>
        </ul>

        <h3>Robot Data Format</h3>
        <p>Each robot entry should follow this format:</p>
        <p class="card-text">Note: robots are linked to companies by including the robot's <code>id</code> in the company's <code>robots</code> array (see Company Data Format).</p>
        <pre class="bg-dark text-light p-3 rounded"><code>{
  "name": "Robot Name",
  "id": "unique_robot_id",
  "urls": [
    { "caption": "Manufacturer page", "url": "https://example.com/robot-page" },
    { "caption": "Additional info", "url": "https://example.com/additional-info" }
  ],
  "photo_urls": [
    "https://example.com/robot-image.jpg",
    "https://example.com/another-image.jpg"
  ],
  "tags": ["RAMIS", "teleoperated", "Commercial"],
  "usages": ["Abdominal", "Urological"],
  "description": "Detailed description of the robot and its capabilities.",
  "regulatory": ["CE 2025", "FDA 2024"]
}</code></pre>

        <h3>Company Data Format</h3>
        <p>Each company entry should follow this format:</p>
        <pre class="bg-dark text-light p-3 rounded"><code>{
  "name": "Company Name",
  "country": "Country Name",
  "urls": [
    { "caption": "Official site", "url": "https://company-website.com" },
    { "caption": "Company LinkedIn", "url": "https://linkedin.com/company/company-name" }
  ],
  "linkedin_url": "https://linkedin.com/company/company-name",
  "robots": [ "unique_robot_id_1", "unique_robot_id_2" ],
  "description": "Short description of the company and location."
}</code></pre>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Step 4: Commit and Push Your Changes</h2>
        <p class="card-text">
          After editing the data files, commit and push your changes:
        </p>
        <pre class="bg-dark text-light p-3 rounded"><code>git add public/robots.json public/companies.json
git commit -m "Add [Robot/Company Name] information"
git push origin main</code></pre>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Step 5: Create a Pull Request</h2>
        <p class="card-text">
          Go to the <a href="https://github.com/medmachina/medmachina.github.io/pulls" target="_blank">original repository</a>
          and create a new pull request from your fork. Provide a clear description of your changes and why they should be included.
        </p>
        <p>
          Please ensure all information is accurate and provide references where possible.
        </p>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <h2 class="card-title">Guidelines for Quality Contributions</h2>
        <ul class="card-text">
          <li>Ensure all URLs are valid</li>
          <li>Use freely usable images</li>
          <li>Provide accurate and up-to-date information</li>
          <li>Use consistent formatting and naming conventions</li>
          <li>For companies, specify at least one robot</li>
        </ul>
      </div>
    </div>

    <!-- Experimental Feature: Robot JSON Generator -->
    <div class="card mt-4 experimental">
      <div class="card-body">
        <h2 class="card-title">Experimental: Robot JSON Generator</h2>
        <p class="small text-muted mb-3">This sandbox helps you draft a robot entry matching <code>robots.schema.json</code>. Only <strong>name</strong> and <strong>id</strong> are required. When you click Generate, the JSON block below updates. (Not submitted automatically.)</p>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">Name *</label>
            <input v-model="form.name" :class="['form-control', fieldError('name') && 'is-invalid']" placeholder="Robot name" />
            <div v-if="fieldError('name')" class="invalid-feedback">{{ fieldError('name') }}</div>
          </div>
          <div class="col-md-6">
            <label class="form-label">ID *</label>
            <input v-model="form.id" :class="['form-control', form.id && !validId ? 'is-invalid' : '']" placeholder="unique_id" />
            <div class="d-flex justify-content-between align-items-center">
              <div class="form-text" :class="{ 'text-danger': (form.id && !validId) }">Pattern: ^[A-Za-z0-9_.&]+$</div>
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="suggestId" :disabled="!form.name">Suggest ID</button>
            </div>
            <div v-if="form.id && !validId" class="invalid-feedback d-block">Invalid ID pattern.</div>
          </div>
          <div class="col-md-4">
            <label class="form-label">Introduction Year</label>
            <input v-model.number="form.introduction_year" type="number" min="1900" max="2100" :class="['form-control', fieldError('introduction_year') && 'is-invalid']" placeholder="2024" />
            <div v-if="fieldError('introduction_year')" class="invalid-feedback">{{ fieldError('introduction_year') }}</div>
          </div>
          <div class="col-md-8">
            <label class="form-label">Description</label>
            <textarea v-model="form.description" rows="2" class="form-control" placeholder="Short description"></textarea>
          </div>
        </div>

        <!-- URLs -->
        <h5 class="mt-3">Reference URLs</h5>
        <div v-for="(u,i) in form.urls" :key="'url-'+i" class="row g-2 align-items-end mb-2">
          <div class="col-md-5"><input v-model="u.caption" :class="['form-control']" placeholder="Caption" /></div>
          <div class="col-md-6"><input v-model="u.url" type="url" :class="['form-control', urlError(i) && 'is-invalid']" placeholder="https://..." />
            <div v-if="urlError(i)" class="invalid-feedback">{{ urlError(i) }}</div>
          </div>
          <div class="col-md-1 text-end"><button @click="removeUrl(i)" class="btn btn-outline-danger btn-sm" title="Remove">×</button></div>
        </div>
        <button @click="addUrl" class="btn btn-outline-primary btn-sm mb-3">Add URL</button>

        <!-- Photos -->
        <h5 class="mt-3">Photos</h5>
        <div v-for="(p,i) in form.photos" :key="'photo-'+i" class="row g-2 align-items-end mb-2">
          <div class="col-md-6"><input v-model="p.url" type="url" :class="['form-control', photoError(i) && 'is-invalid']" placeholder="Image URL (direct)" />
            <div v-if="photoError(i)" class="invalid-feedback">{{ photoError(i) }}</div>
          </div>
          <div class="col-md-5"><input v-model="p.site" type="url" class="form-control" placeholder="Source page (optional)" /></div>
          <div class="col-md-1 text-end"><button @click="removePhoto(i)" class="btn btn-outline-danger btn-sm">×</button></div>
        </div>
        <button @click="addPhoto" class="btn btn-outline-primary btn-sm mb-3">Add Photo</button>

        <!-- Tags -->
        <h5 class="mt-3">Tags</h5>
        <div class="d-flex flex-wrap gap-2 mb-2 tag-list">
          <button v-for="t in tagOptions" :key="t" type="button" @click="toggleTag(t)" :class="['btn btn-sm', form.tags.includes(t) ? 'btn-primary' : 'btn-outline-secondary']">{{ t }}</button>
        </div>

        <!-- Usages -->
        <h5 class="mt-3">Usages</h5>
        <div class="d-flex flex-wrap gap-2 mb-2 usage-list">
          <button v-for="u in usageOptions" :key="u" type="button" @click="toggleUsage(u)" :class="['btn btn-sm', form.usages.includes(u) ? 'btn-primary' : 'btn-outline-secondary']">{{ u }}</button>
        </div>

        <!-- Regulatory -->
        <h5 class="mt-3">Regulatory Entries</h5>
        <div v-for="(r,i) in form.regulatory" :key="'reg-'+i" class="border rounded p-2 mb-2">
          <div class="row g-2 mb-2">
            <div class="col-md-3"><input v-model="r.body" :class="['form-control']" placeholder="Body (e.g. FDA)" /></div>
            <div class="col-md-2"><input v-model.number="r.year" type="number" min="1900" max="2100" :class="['form-control', regYearError(i) && 'is-invalid']" placeholder="Year" />
              <div v-if="regYearError(i)" class="invalid-feedback">{{ regYearError(i) }}</div>
            </div>
            <div class="col-md-2"><input v-model="r.region" type="text" class="form-control" placeholder="Region" /></div>
            <div class="col-md-2"><input v-model="r.type" type="text" class="form-control" placeholder="Type" /></div>
            <div class="col-md-2"><input v-model="r.sourceUrlInput" type="url" class="form-control" placeholder="Add source URL" /></div>
            <div class="col-md-1 text-end"><button @click="removeReg(i)" class="btn btn-outline-danger btn-sm">×</button></div>
          </div>
          <div class="mb-2">
            <button @click="addRegSource(i)" class="btn btn-outline-primary btn-sm me-2">Add Source</button>
            <small class="text-muted">Sources ({{ r.source_urls.length }}):</small>
          </div>
          <ul class="small mb-0">
            <li v-for="(s,si) in r.source_urls" :key="'src-'+si" class="d-flex justify-content-between align-items-center">
              <span style="word-break:break-all;">{{ s }}</span>
              <button @click="removeRegSource(i, si)" class="btn btn-outline-danger btn-sm" title="Remove">×</button>
            </li>
          </ul>
        </div>
        <button @click="addReg" class="btn btn-outline-primary btn-sm mb-3">Add Regulatory Entry</button>

        <div class="mt-4">
          <button @click="generate" :disabled="!canGenerate || validationIssues.length" class="btn btn-success">Generate JSON</button>
          <span v-if="(!canGenerate || validationIssues.length)" class="ms-2 text-warning small">Resolve validation issues to enable generation.</span>
        </div>

        <div v-if="validationIssues.length" class="mt-3">
          <div class="alert alert-warning p-2">
            <strong>Validation Issues:</strong>
            <ul class="mb-0 small">
              <li v-for="(v,i) in validationIssues" :key="'val-'+i">{{ v }}</li>
            </ul>
          </div>
        </div>

        <div v-if="generatedJson" class="mt-3">
          <h5 class="mb-2">Generated Robot JSON</h5>
          <pre class="bg-dark text-light p-3 rounded" style="max-height:400px;overflow:auto;"><code>{{ generatedJson }}</code></pre>
          <button @click="copyJson" class="btn btn-outline-secondary btn-sm">Copy to Clipboard</button>
          <span v-if="copied" class="text-success ms-2">Copied!</span>
          <button @click="buildPRInstructions" class="btn btn-outline-primary btn-sm ms-3">Show PR Helper</button>
        </div>

        <div v-if="prHelper" class="mt-3">
          <h5 class="mb-2">Pull Request Helper</h5>
          <p class="small text-muted">Use these steps after adding the JSON object to <code>public/robots.json</code>.</p>
          <pre class="bg-dark text-light p-3 rounded" style="max-height:300px;overflow:auto;"><code>{{ prHelper }}</code></pre>
          <button @click="copyPR" class="btn btn-outline-secondary btn-sm">Copy Instructions</button>
          <span v-if="copiedPR" class="text-success ms-2">Copied!</span>
        </div>
        <div v-if="robotSchemaErrors.length" class="mt-3">
          <div class="alert alert-warning p-2">
            <strong>Schema Errors:</strong>
            <ul class="mb-0 small">
              <li v-for="(e,i) in robotSchemaErrors" :key="'rse-'+i">{{ e }}</li>
            </ul>
          </div>
        </div>
        <div v-if="generatedJson" class="mt-3 border rounded p-3">
          <h6 class="mb-2">Direct GitHub Submission (Experimental)</h6>
          <div class="mb-2">
            <input v-model="githubToken" type="password" class="form-control" placeholder="GitHub Personal Access Token (repo scope)" />
            <small class="text-muted">Token is transient and not stored.</small>
          </div>
          <div class="row g-2 mb-2">
            <div class="col-md-6"><input v-model="robotBranch" class="form-control" placeholder="Branch name" /></div>
            <div class="col-md-6"><input v-model="robotCommitMsg" class="form-control" placeholder="Commit message" /></div>
          </div>
          <button @click="submitRobotToGitHub" :disabled="submittingRobot || !githubToken || anyRobotIssues" class="btn btn-outline-success btn-sm">Submit Robot Pull Request</button>
          <span v-if="submittingRobot" class="ms-2 small text-muted">Submitting…</span>
          <div v-if="robotSubmitResult" class="small mt-2" :class="robotSubmitResult.startsWith('Success') ? 'text-success' : 'text-danger'">{{ robotSubmitResult }}</div>
          <div v-if="anyRobotIssues" class="small text-warning mt-2">Resolve validation / schema issues before submitting.</div>
        </div>
      </div>
    </div>
    <!-- Experimental Feature: Company JSON Generator -->
    <div class="card mt-4 experimental">
      <div class="card-body">
        <h2 class="card-title">Experimental: Company JSON Generator</h2>
        <p class="small text-muted mb-3">Draft a company entry for <code>companies.json</code>. Required fields: name, country. Robots should list robot IDs present in <code>robots.json</code>.</p>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">Company Name *</label>
            <input v-model="companyForm.name" :class="['form-control', companyFieldError('name') && 'is-invalid']" placeholder="Company name" />
            <div v-if="companyFieldError('name')" class="invalid-feedback">{{ companyFieldError('name') }}</div>
          </div>
            <div class="col-md-6">
              <label class="form-label">Country *</label>
              <input v-model="companyForm.country" :class="['form-control', companyFieldError('country') && 'is-invalid']" placeholder="Country" />
              <div v-if="companyFieldError('country')" class="invalid-feedback">{{ companyFieldError('country') }}</div>
            </div>
            <div class="col-md-12">
              <label class="form-label">Description</label>
              <textarea v-model="companyForm.description" rows="2" class="form-control" placeholder="Short description"></textarea>
            </div>
        </div>
        <h5>Reference URLs</h5>
        <div v-for="(u,i) in companyForm.urls" :key="'c-url-'+i" class="row g-2 align-items-end mb-2">
          <div class="col-md-5"><input v-model="u.caption" class="form-control" placeholder="Caption" /></div>
          <div class="col-md-6"><input v-model="u.url" :class="['form-control', companyUrlError(i) && 'is-invalid']" placeholder="https://..." />
            <div v-if="companyUrlError(i)" class="invalid-feedback">{{ companyUrlError(i) }}</div>
          </div>
          <div class="col-md-1 text-end"><button @click="removeCompanyUrl(i)" class="btn btn-outline-danger btn-sm">×</button></div>
        </div>
        <button @click="addCompanyUrl" class="btn btn-outline-primary btn-sm mb-3">Add URL</button>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">LinkedIn URL</label>
            <input v-model="companyForm.linkedin_url" :class="['form-control', linkError && 'is-invalid']" placeholder="https://linkedin.com/company/..." />
            <div v-if="linkError" class="invalid-feedback">{{ linkError }}</div>
          </div>
          <div class="col-md-6">
            <label class="form-label">OpenCorporates URL</label>
            <input v-model="companyForm.opencorporates_url" :class="['form-control', ocError && 'is-invalid']" placeholder="https://opencorporates.com/companies/..." />
            <div v-if="ocError" class="invalid-feedback">{{ ocError }}</div>
          </div>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-md-4">
            <label class="form-label">Employee Count</label>
            <input v-model.number="companyForm.employee_count" type="number" min="1" class="form-control" placeholder="500" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Founded Year</label>
            <input v-model="companyForm.founded_year" class="form-control" placeholder="2008" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Company Type</label>
            <input v-model="companyForm.company_type" class="form-control" placeholder="Private" />
          </div>
        </div>
        <h5>Robots (IDs)</h5>
        <div class="d-flex flex-wrap gap-2 mb-2">
          <button v-for="r in allRobotIds" :key="r" @click="toggleCompanyRobot(r)" :class="['btn btn-sm', companyForm.robots.includes(r) ? 'btn-primary' : 'btn-outline-secondary']">{{ r }}</button>
        </div>
        <div v-for="(r,i) in companyForm.robots" :key="'cr-'+i" class="badge bg-secondary me-2">{{ r }}</div>
        <div class="mt-3">
          <button @click="generateCompany" :disabled="companyValidationIssues.length" class="btn btn-success">Generate Company JSON</button>
          <span v-if="companyValidationIssues.length" class="ms-2 text-warning small">Resolve issues before generation.</span>
        </div>
        <div v-if="generatedCompanyJson" class="mt-3">
          <h5 class="mb-2">Generated Company JSON</h5>
            <pre class="bg-dark text-light p-3 rounded" style="max-height:300px;overflow:auto;"><code>{{ generatedCompanyJson }}</code></pre>
            <button @click="copyCompanyJson" class="btn btn-outline-secondary btn-sm">Copy JSON</button>
            <span v-if="copiedCompany" class="text-success ms-2">Copied!</span>
            <button @click="buildCompanyPR" class="btn btn-outline-primary btn-sm ms-3">Show PR Helper</button>
        </div>
        <div v-if="companyPrHelper" class="mt-3">
          <h5 class="mb-2">Company PR Helper</h5>
          <pre class="bg-dark text-light p-3 rounded" style="max-height:300px;overflow:auto;"><code>{{ companyPrHelper }}</code></pre>
          <button @click="copyCompanyPR" class="btn btn-outline-secondary btn-sm">Copy Instructions</button>
          <span v-if="copiedCompanyPR" class="text-success ms-2">Copied!</span>
        </div>
        <div v-if="companyValidationIssues.length" class="mt-3">
          <div class="alert alert-warning p-2">
            <strong>Validation Issues:</strong>
            <ul class="mb-0 small">
              <li v-for="(v,i) in companyValidationIssues" :key="'cval-'+i">{{ v }}</li>
            </ul>
          </div>
        </div>
        <div v-if="companySchemaErrors.length" class="mt-3">
          <div class="alert alert-warning p-2">
            <strong>Schema Errors:</strong>
            <ul class="mb-0 small">
              <li v-for="(e,i) in companySchemaErrors" :key="'cse-'+i">{{ e }}</li>
            </ul>
          </div>
        </div>
        <div v-if="generatedCompanyJson" class="mt-3 border rounded p-3">
          <h6 class="mb-2">Direct GitHub Submission (Experimental)</h6>
          <div class="mb-2">
            <input v-model="githubToken" type="password" class="form-control" placeholder="GitHub Personal Access Token (repo scope)" />
            <small class="text-muted">Token is transient and not stored.</small>
          </div>
          <div class="row g-2 mb-2">
            <div class="col-md-6"><input v-model="companyBranch" class="form-control" placeholder="Branch name" /></div>
            <div class="col-md-6"><input v-model="companyCommitMsg" class="form-control" placeholder="Commit message" /></div>
          </div>
            <button @click="submitCompanyToGitHub" :disabled="submittingCompany || !githubToken || anyCompanyIssues" class="btn btn-outline-success btn-sm">Submit Company Pull Request</button>
            <span v-if="submittingCompany" class="ms-2 small text-muted">Submitting…</span>
            <div v-if="companySubmitResult" class="small mt-2" :class="companySubmitResult.startsWith('Success') ? 'text-success' : 'text-danger'">{{ companySubmitResult }}</div>
            <div v-if="anyCompanyIssues" class="small text-warning mt-2">Resolve validation / schema issues before submitting.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 8px;
}

.title {
  color: rgba(255, 255, 255);
}

a {
  color: var(--color-primary);
}

pre {
  border-radius: 6px;
  overflow-x: auto;
}

code {
  font-family: monospace;
}

.alert {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  border-left: 4px solid var(--color-primary);
  padding: 1rem;
  border-radius: 4px;
}

.alert-info {
  background-color: rgba(13, 202, 240, 0.1);
  border-left-color: rgba(13, 202, 240, 0.8);
}

.alert-warning {
  background-color: rgba(255, 193, 7, 0.1);
  border-left-color: rgba(255, 193, 7, 0.8);
}

.custom-alert {
  background-color: var(--color-background-soft);
  color: var(--color-text);
  border-left: 4px solid var(--color-primary);
  border-radius: 4px;
  padding: 1rem;
}

.custom-alert i {
  color: var(--color-primary);
}
.experimental {
  border-style: dashed;
}
.tag-list button, .usage-list button {
  white-space: nowrap;
}
</style>
<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import Ajv, { ValidateFunction } from 'ajv'

interface UrlEntry { caption: string; url: string }
interface PhotoEntry { url: string; site?: string }
interface RegulatoryEntry { body: string; year: number|null; region: string|null; type: string|null; source_urls: string[]; sourceUrlInput?: string }
interface CompanyUrl { caption:string; url:string }

const tagOptions = ref<string[]>([ 'RAMIS','Commercial','Teleoperated','Multiple ports','3+ instruments','Stereo endoscope','Mechanical Cartesian manipulation','Stereo viewer','Single patient cart','Haptic','Wristed instruments','Open surgery','Mechanical RCM','Retired','Orthopedic','Multiple patient carts','Stereo display','Haptic device','Motorized table','Single port','2 instruments','Collaborative control','Force feedback','Mono endoscope','Mechanical manipulation','Open console','Research system','Software RCM','Semi-autonomous','Open source','Open architecture','Free hand manipulation','Autonomous','Simulation','Flexible robot','Open microsurgery','Biopsy','TRUS','Dental' ])
const usageOptions = ref<string[]>([ 'Abdominal','Urological','Gynecological','Transoral','Knee','Hip','Lung','Bronchoscopy','Thoracic','Spine','Eye','Prostate','Dental implant' ])

// Robot form
const form = reactive({
  name: '',
  id: '',
  introduction_year: null as number|null,
  description: '',
  urls: [] as UrlEntry[],
  photos: [] as PhotoEntry[],
  tags: [] as string[],
  usages: [] as string[],
  regulatory: [] as RegulatoryEntry[]
})
const generatedJson = ref('')
const copied = ref(false)
const prHelper = ref('')
const copiedPR = ref(false)

// Company form
const companyForm = reactive({
  name:'', country:'', description:'', employee_count:null as number|null, founded_year:'', company_type:'', linkedin_url:'', opencorporates_url:'', urls:[] as CompanyUrl[], robots:[] as string[]
})
const generatedCompanyJson = ref('')
const copiedCompany = ref(false)
const companyPrHelper = ref('')
const copiedCompanyPR = ref(false)
const allRobotIds = ref<string[]>([])

// Basic validations
const idPattern = /^[A-Za-z0-9_.&]+$/
const validId = computed(() => idPattern.test(form.id))
const canGenerate = computed(() => !!form.name && !!form.id && validId.value)

const validationIssues = computed(() => {
  const issues:string[] = []
  if(!form.name) issues.push('Name is required.')
  if(!form.id) issues.push('ID is required.')
  else if(!validId.value) issues.push('ID must match ^[A-Za-z0-9_.&]+$.')
  if(form.introduction_year !== null) {
    if(form.introduction_year < 1900 || form.introduction_year > 2100) issues.push('Introduction year must be between 1900 and 2100.')
  }
  form.urls.forEach((u,idx)=>{ if(u.url && !/^https?:\/\//.test(u.url)) issues.push(`URL #${idx+1} must start with http or https.`) })
  form.photos.forEach((p,idx)=>{ if(p.url && !/^https?:\/\//.test(p.url)) issues.push(`Photo URL #${idx+1} must start with http or https.`) })
  form.regulatory.forEach((r,idx)=>{ if(r.year !== null && (r.year < 1900 || r.year > 2100)) issues.push(`Regulatory entry #${idx+1} year out of range.`) })
  return issues
})

const companyValidationIssues = computed(()=>{
  const issues:string[] = []
  if(!companyForm.name) issues.push('Company name required.')
  if(!companyForm.country) issues.push('Country required.')
  companyForm.urls.forEach((u,i)=>{ if(u.url && !/^https?:\/\//.test(u.url)) issues.push(`Company URL #${i+1} invalid.`) })
  if(companyForm.linkedin_url && !/^https?:\/\//.test(companyForm.linkedin_url)) issues.push('LinkedIn URL invalid.')
  if(companyForm.opencorporates_url && !/^https?:\/\//.test(companyForm.opencorporates_url)) issues.push('OpenCorporates URL invalid.')
  if(companyForm.employee_count !== null && companyForm.employee_count < 1) issues.push('Employee count must be >=1.')
  if(companyForm.founded_year && !/^(19|20)\d{2}$/.test(companyForm.founded_year)) issues.push('Founded year must be 19xx or 20xx.')
  companyForm.robots.forEach((r,i)=>{ if(!/^[A-Za-z0-9_.&]+$/.test(r)) issues.push(`Robot ID #${i+1} invalid pattern.`) })
  return issues
})

// Inline field error helpers
function fieldError(field:string){ if(field==='name' && !form.name) return 'Name required.'; if(field==='introduction_year' && form.introduction_year !== null && (form.introduction_year < 1900 || form.introduction_year > 2100)) return 'Year out of range.'; return '' }
function urlError(i:number){ const u=form.urls[i]; if(u?.url && !/^https?:\/\//.test(u.url)) return 'Invalid URL.'; return '' }
function photoError(i:number){ const p=form.photos[i]; if(p?.url && !/^https?:\/\//.test(p.url)) return 'Invalid image URL.'; return '' }
function regYearError(i:number){ const r=form.regulatory[i]; if(r && r.year!==null && (r.year<1900||r.year>2100)) return 'Year out of range.'; return '' }
function companyFieldError(field:string){ if(field==='name' && !companyForm.name) return 'Name required.'; if(field==='country' && !companyForm.country) return 'Country required.'; return '' }
function companyUrlError(i:number){ const u=companyForm.urls[i]; if(u?.url && !/^https?:\/\//.test(u.url)) return 'Invalid URL.'; return '' }
const linkError = computed(()=> companyForm.linkedin_url && !/^https?:\/\//.test(companyForm.linkedin_url) ? 'Invalid LinkedIn URL.' : '')
const ocError = computed(()=> companyForm.opencorporates_url && !/^https?:\/\//.test(companyForm.opencorporates_url) ? 'Invalid OpenCorporates URL.' : '')

// Form mutators
function addUrl(){ form.urls.push({ caption:'', url:'' }) }
function removeUrl(i:number){ form.urls.splice(i,1) }
function addPhoto(){ form.photos.push({ url:'', site:'' }) }
function removePhoto(i:number){ form.photos.splice(i,1) }
function toggleTag(t:string){ const idx=form.tags.indexOf(t); idx>=0?form.tags.splice(idx,1):form.tags.push(t) }
function toggleUsage(u:string){ const idx=form.usages.indexOf(u); idx>=0?form.usages.splice(idx,1):form.usages.push(u) }
function addReg(){ form.regulatory.push({ body:'', year:null, region:null, type:null, source_urls:[], sourceUrlInput:'' }) }
function removeReg(i:number){ form.regulatory.splice(i,1) }
function addRegSource(i:number){ const entry=form.regulatory[i]; if(entry.sourceUrlInput){ entry.source_urls.push(entry.sourceUrlInput); entry.sourceUrlInput='' } }
function removeRegSource(i:number,si:number){ form.regulatory[i].source_urls.splice(si,1) }
function suggestId(){ if(!form.name) return; const base=form.name.toLowerCase().replace(/\s+/g,'_').replace(/[^a-z0-9_.&]/g,''); if(!form.id) form.id=base.slice(0,50); else if(confirm('Replace existing ID with suggested?')) form.id=base.slice(0,50) }

function addCompanyUrl(){ companyForm.urls.push({ caption:'', url:'' }) }
function removeCompanyUrl(i:number){ companyForm.urls.splice(i,1) }
function toggleCompanyRobot(id:string){ const idx=companyForm.robots.indexOf(id); idx>=0?companyForm.robots.splice(idx,1):companyForm.robots.push(id) }

// Schema + Ajv
const robotSchema = ref<any>(null)
const companySchema = ref<any>(null)
const robotValidator = ref<ValidateFunction|null>(null)
const companyValidator = ref<ValidateFunction|null>(null)
const robotSchemaErrors = ref<string[]>([])
const companySchemaErrors = ref<string[]>([])

function validateRobotObject(obj:any){ robotSchemaErrors.value=[]; if(robotValidator.value){ const valid=robotValidator.value(obj); if(!valid && robotValidator.value.errors){ robotSchemaErrors.value=robotValidator.value.errors.map(e=>`${e.instancePath||'/'} ${e.message}`) } } }
function validateCompanyObject(obj:any){ companySchemaErrors.value=[]; if(companyValidator.value){ const valid=companyValidator.value(obj); if(!valid && companyValidator.value.errors){ companySchemaErrors.value=companyValidator.value.errors.map(e=>`${e.instancePath||'/'} ${e.message}`) } } }

// GitHub submission state
const githubToken = ref('')
// Robot submission
const robotBranch = ref('')
const robotCommitMsg = ref('')
const submittingRobot = ref(false)
const robotSubmitResult = ref('')
// Company submission
const companyBranch = ref('')
const companyCommitMsg = ref('')
const submittingCompany = ref(false)
const companySubmitResult = ref('')

const anyRobotIssues = computed(()=> validationIssues.value.length || robotSchemaErrors.value.length)
const anyCompanyIssues = computed(()=> companyValidationIssues.value.length || companySchemaErrors.value.length)

function generate(){
  if(!canGenerate.value || validationIssues.value.length) return
  const robot:any = { name:form.name, id:form.id }
  if(form.introduction_year) robot.introduction_year = form.introduction_year
  if(form.description) robot.description = form.description
  if(form.urls.length) robot.urls = form.urls.filter(u=>u.caption && u.url)
  if(form.photos.length) robot.photos = form.photos.filter(p=>p.url)
  if(form.tags.length) robot.tags=[...form.tags]
  if(form.usages.length) robot.usages=[...form.usages]
  const regFiltered=form.regulatory.filter(r=>r.body).map(r=>({ body:r.body, year:r.year, region:r.region, type:r.type, source_urls:r.source_urls }))
  if(regFiltered.length) robot.regulatory=regFiltered
  validateRobotObject(robot)
  generatedJson.value = JSON.stringify(robot,null,2)
  copied.value=false
  if(!robotBranch.value) robotBranch.value = `add-robot-${form.id}`.slice(0,60)
  if(!robotCommitMsg.value) robotCommitMsg.value = `feat(robot): add ${form.name} (${form.id})`
}

function generateCompany(){
  if(companyValidationIssues.value.length) return
  const c:any = { name:companyForm.name, country:companyForm.country }
  if(companyForm.description) c.description=companyForm.description
  if(companyForm.employee_count!==null) c.employee_count=companyForm.employee_count
  if(companyForm.founded_year) c.founded_year=companyForm.founded_year
  if(companyForm.company_type) c.company_type=companyForm.company_type
  if(companyForm.linkedin_url) c.linkedin_url=companyForm.linkedin_url
  if(companyForm.opencorporates_url) c.opencorporates_url=companyForm.opencorporates_url
  const urls=companyForm.urls.filter(u=>u.caption && u.url); if(urls.length) c.urls=urls
  if(companyForm.robots.length) c.robots=[...companyForm.robots]
  validateCompanyObject(c)
  generatedCompanyJson.value = JSON.stringify(c,null,2)
  copiedCompany.value=false
  if(!companyBranch.value) companyBranch.value = `add-company-${companyForm.name.toLowerCase().replace(/\s+/g,'-').replace(/[^a-z0-9-]/g,'')}`.slice(0,60)
  if(!companyCommitMsg.value) companyCommitMsg.value = `feat(company): add ${companyForm.name}`
}

function copyJson(){ if(!generatedJson.value) return; navigator.clipboard.writeText(generatedJson.value).then(()=>{ copied.value=true; setTimeout(()=>copied.value=false,2000) }) }
function copyCompanyJson(){ if(!generatedCompanyJson.value) return; navigator.clipboard.writeText(generatedCompanyJson.value).then(()=>{ copiedCompany.value=true; setTimeout(()=>copiedCompany.value=false,2000) }) }

function buildPRInstructions(){ if(!generatedJson.value) return; const branch=`add-robot-${form.id}`; const commitMsg=`feat(robot): add ${form.name} (${form.id})`; prHelper.value=[ '# 1. Open public/robots.json and insert the generated object (maintain JSON array formatting).', '# 2. Create a new branch:', `git checkout -b ${branch}`, '# 3. Stage and commit changes:', 'git add public/robots.json', `git commit -m "${commitMsg}"`, '# 4. Push branch:', `git push origin ${branch}`, '# 5. Open your browser to create the PR (replace YOUR_USERNAME):', `https://github.com/medmachina/medmachina.github.io/compare/main...YOUR_USERNAME:${branch}?expand=1`, '# 6. In PR description, include references supporting URLs and regulatory claims.' ].join('\n'); copiedPR.value=false }
function buildCompanyPR(){ if(!generatedCompanyJson.value) return; const branch=`add-company-${companyForm.name.toLowerCase().replace(/\s+/g,'-').replace(/[^a-z0-9-]/g,'')}`.slice(0,60); const commitMsg=`feat(company): add ${companyForm.name}`; companyPrHelper.value=[ '# 1. Open public/companies.json and insert the generated object (maintain array formatting).', '# 2. Create a new branch:', `git checkout -b ${branch}`, '# 3. Stage and commit changes:', 'git add public/companies.json', `git commit -m "${commitMsg}"`, '# 4. Push branch:', `git push origin ${branch}`, '# 5. Open PR URL (replace YOUR_USERNAME):', `https://github.com/medmachina/medmachina.github.io/compare/main...YOUR_USERNAME:${branch}?expand=1`, '# 6. Provide references supporting URLs / robots association.' ].join('\n'); copiedCompanyPR.value=false }

function copyPR(){ if(!prHelper.value) return; navigator.clipboard.writeText(prHelper.value).then(()=>{ copiedPR.value=true; setTimeout(()=>copiedPR.value=false,2000) }) }
function copyCompanyPR(){ if(!companyPrHelper.value) return; navigator.clipboard.writeText(companyPrHelper.value).then(()=>{ copiedCompanyPR.value=true; setTimeout(()=>copiedCompanyPR.value=false,2000) }) }

onMounted(async ()=>{
  // Load robot schema
  try { const res=await fetch('/robots.schema.json'); if(res.ok){ const schema=await res.json(); robotSchema.value=schema; try { const ajv=new Ajv({ allErrors:true, strict:false }); robotValidator.value=ajv.compile(schema) } catch(e){}; const tagDefs=schema?.$defs?.Tag?.oneOf?.map((d:any)=>d.const).filter((v:any)=>typeof v==='string'); if(tagDefs?.length) tagOptions.value=tagDefs; const usageDefs=schema?.$defs?.Usage?.oneOf?.map((d:any)=>d.const).filter((v:any)=>typeof v==='string'); if(usageDefs?.length) usageOptions.value=usageDefs } } catch(e){}
  // Load robots.json IDs
  try { const r=await fetch('/robots.json'); if(r.ok){ const robots=await r.json(); allRobotIds.value=robots.map((rb:any)=>rb.id).filter((id:any)=>typeof id==='string') } } catch(e){}
  // Load company schema
  try { const cr=await fetch('/companies.schema.json'); if(cr.ok){ const cSchema=await cr.json(); companySchema.value=cSchema; try { const ajv=new Ajv({ allErrors:true, strict:false }); companyValidator.value=ajv.compile(cSchema) } catch(e){} } } catch(e){}
})

async function submitRobotToGitHub(){
  robotSubmitResult.value=''
  if(!githubToken.value){ robotSubmitResult.value='GitHub token required.'; return }
  if(!generatedJson.value){ robotSubmitResult.value='Generate JSON first.'; return }
  if(anyRobotIssues.value){ robotSubmitResult.value='Fix validation/schema issues first.'; return }
  submittingRobot.value=true
  try {
    const owner='medmachina'; const repo='medmachina.github.io'
    const refResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/git/refs/heads/main`, { headers:{ Authorization:`Bearer ${githubToken.value}` } })
    if(!refResp.ok) throw new Error('Failed to fetch main ref')
    const refData=await refResp.json(); const mainSha=refData.object.sha
    const branchName=robotBranch.value || `add-robot-${form.id}`
    const createBranchResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/git/refs`, { method:'POST', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${githubToken.value}` }, body:JSON.stringify({ ref:`refs/heads/${branchName}`, sha:mainSha }) })
    if(createBranchResp.status!==422 && !createBranchResp.ok) throw new Error('Failed to create branch')
    const robotsResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/public/robots.json?ref=main`)
    if(!robotsResp.ok) throw new Error('Failed to fetch robots.json')
    const robotsData=await robotsResp.json(); const existingSha=robotsData.sha; const contentStr=atob(robotsData.content.replace(/\n/g,''))
    let arr:any[]; try { arr=JSON.parse(contentStr) } catch{ throw new Error('Parse robots.json failed') }
    const newObj=JSON.parse(generatedJson.value)
    if(arr.some(r=>r.id===newObj.id)){ robotSubmitResult.value=`Robot id ${newObj.id} already exists.`; submittingRobot.value=false; return }
    arr.push(newObj)
    const newContentB64=btoa(JSON.stringify(arr,null,2))
    const putResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/public/robots.json`, { method:'PUT', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${githubToken.value}` }, body:JSON.stringify({ message: robotCommitMsg.value || `feat(robot): add ${newObj.name} (${newObj.id})`, content:newContentB64, branch:branchName, sha:existingSha }) })
    if(!putResp.ok) throw new Error('Failed to update robots.json')
    const prResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/pulls`, { method:'POST', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${githubToken.value}` }, body:JSON.stringify({ title: robotCommitMsg.value || `feat(robot): add ${newObj.name} (${newObj.id})`, head:branchName, base:'main', body:'Add new robot entry via web form.' }) })
    if(!prResp.ok) throw new Error('Failed to create PR')
    const prData=await prResp.json(); robotSubmitResult.value=`Success! PR: ${prData.html_url}`
  } catch(e:any){ robotSubmitResult.value=`Error: ${e.message}` } finally { submittingRobot.value=false }
}

async function submitCompanyToGitHub(){
  companySubmitResult.value=''
  if(!githubToken.value){ companySubmitResult.value='GitHub token required.'; return }
  if(!generatedCompanyJson.value){ companySubmitResult.value='Generate company JSON first.'; return }
  if(anyCompanyIssues.value){ companySubmitResult.value='Fix validation/schema issues first.'; return }
  submittingCompany.value=true
  try {
    const owner='medmachina'; const repo='medmachina.github.io'
    const refResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/git/refs/heads/main`, { headers:{ Authorization:`Bearer ${githubToken.value}` } })
    if(!refResp.ok) throw new Error('Failed to fetch main ref')
    const refData=await refResp.json(); const mainSha=refData.object.sha
    const branchName=companyBranch.value || `add-company-${companyForm.name.toLowerCase().replace(/\s+/g,'-').replace(/[^a-z0-9-]/g,'')}`
    const createBranchResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/git/refs`, { method:'POST', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${githubToken.value}` }, body:JSON.stringify({ ref:`refs/heads/${branchName}`, sha:mainSha }) })
    if(createBranchResp.status!==422 && !createBranchResp.ok) throw new Error('Failed to create branch')
    const companiesResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/public/companies.json?ref=main`)
    if(!companiesResp.ok) throw new Error('Failed to fetch companies.json')
    const companiesData=await companiesResp.json(); const existingSha=companiesData.sha; const contentStr=atob(companiesData.content.replace(/\n/g,''))
    let arr:any[]; try { arr=JSON.parse(contentStr) } catch{ throw new Error('Parse companies.json failed') }
    const newObj=JSON.parse(generatedCompanyJson.value)
    if(arr.some(c=>c.name.toLowerCase()===newObj.name.toLowerCase())){ companySubmitResult.value=`Company ${newObj.name} already exists.`; submittingCompany.value=false; return }
    arr.push(newObj)
    const newContentB64=btoa(JSON.stringify(arr,null,2))
    const putResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/public/companies.json`, { method:'PUT', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${githubToken.value}` }, body:JSON.stringify({ message: companyCommitMsg.value || `feat(company): add ${newObj.name}`, content:newContentB64, branch:branchName, sha:existingSha }) })
    if(!putResp.ok) throw new Error('Failed to update companies.json')
    const prResp=await fetch(`https://api.github.com/repos/${owner}/${repo}/pulls`, { method:'POST', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${githubToken.value}` }, body:JSON.stringify({ title: companyCommitMsg.value || `feat(company): add ${newObj.name}`, head:branchName, base:'main', body:'Add new company entry via web form.' }) })
    if(!prResp.ok) throw new Error('Failed to create PR')
    const prData=await prResp.json(); companySubmitResult.value=`Success! PR: ${prData.html_url}`
  } catch(e:any){ companySubmitResult.value=`Error: ${e.message}` } finally { submittingCompany.value=false }
}
</script>