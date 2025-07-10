<template>
  <div class="container">
    <h1 class="mb-4 title">How to Contribute</h1>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Contributing to AMERODI</h2>
        <p class="card-text">
          We welcome contributions to the A Medical Robot Directory (AMERODI). This guide will help you understand
          how to contribute by adding or updating robot and company information in our database.
        </p>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Step 1: Fork the Repository</h2>
        <p class="card-text">
          Start by forking the <a href="https://github.com/amerodi/amerodi.github.io" target="_blank">AMERODI GitHub repository</a>
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
        <pre class="bg-dark text-light p-3 rounded"><code>git clone https://github.com/YOUR_USERNAME/amerodi.github.io.git
cd amerodi.github.io</code></pre>
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
        <pre class="bg-dark text-light p-3 rounded"><code>{
  "project_name": "Robot Name",
  "id": "uniqueRobotId",
  "company_id": "companyIdReference",
  "urls": [
    "https://example.com/robot-page",
    "https://example.com/additional-info"
  ],
  "photoURL": [
    "https://example.com/robot-image.jpg",
    "https://example.com/another-image.jpg"
  ],
  "tags": [
    "RAMIS",
    "teleoperated",
    "Commercial"
  ],
  "description": "Detailed description of the robot and its capabilities."
}</code></pre>

        <h3>Company Data Format</h3>
        <p>Each company entry should follow this format:</p>
        <pre class="bg-dark text-light p-3 rounded"><code>{
  "name": "Company Name",
  "country": "Country Name",
  "urls": ["https://company-website.com", "https://linkedin.com/company/company-name"],
  "robots": [ "uniqueRobotId1", "uniqueRobotId2" ]
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
          Go to the <a href="https://github.com/amerodi/amerodi.github.io/pulls" target="_blank">original repository</a>
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
</style>
<script setup lang="ts">
</script>