<template>
  <div class="container">
    <h1 class="mb-4 title">Contact Us</h1>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Get in Touch</h2>
        <p class="card-text">
          We welcome feedback, questions, and suggestions about the A Medical Robot Directory (AMERODI).
          The best way to reach us is through the GitHub Issues section of our repository.
        </p>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">Using GitHub Issues</h2>
        <p class="card-text">
          GitHub Issues is a tracking system integrated with our repository that allows for transparent communication
          and documentation of questions, bugs, and feature requests.
        </p>

        <div class="alert alert-info">
          <i class="bi bi-info-circle me-2"></i>
          You'll need a GitHub account to create issues. It's free and easy to create one at <a href="https://github.com/join" target="_blank">github.com/join</a>.
        </div>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">How to Create an Issue</h2>
        <ol class="card-text">
          <li>Visit our <a href="https://github.com/amerodi/amerodi.github.io/issues" target="_blank">GitHub Issues page</a></li>
          <li>Click on the green "New issue" button in the top right</li>
          <li>Provide a clear title that summarizes your question or feedback</li>
          <li>In the description, include as much detail as possible</li>
          <li>Submit your issue by clicking "Submit new issue"</li>
        </ol>

        <div class="mt-4">
          <a href="https://github.com/amerodi/amerodi.github.io/issues/new" target="_blank" class="btn btn-primary">
            Create New Issue
          </a>
        </div>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h2 class="card-title">What to Include in Your Issue</h2>
        <p class="card-text">To help us address your question or feedback effectively, please include:</p>
        <ul>
          <li>Clear description of your question or feedback</li>
          <li>For data corrections: specific details about what needs to be updated</li>
          <li>For feature requests: detailed description of the feature and why it would be valuable</li>
          <li>For technical issues: steps to reproduce, expected behavior, and actual behavior</li>
          <li>Screenshots if relevant</li>
        </ul>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <h2 class="card-title">Issue Types</h2>
        <p class="card-text">You can use GitHub Issues for:</p>
        <div class="row">
          <div class="col-md-6 mb-3">
            <div class="h-100 p-3 border rounded">
              <h3 class="h5">Data Corrections</h3>
              <p>Report inaccurate or outdated information about robots or companies</p>
            </div>
          </div>
          <div class="col-md-6 mb-3">
            <div class="h-100 p-3 border rounded">
              <h3 class="h5">Feature Requests</h3>
              <p>Suggest new features or improvements to the directory</p>
            </div>
          </div>
          <div class="col-md-6 mb-3">
            <div class="h-100 p-3 border rounded">
              <h3 class="h5">Questions</h3>
              <p>Ask about medical robots or how to use the directory</p>
            </div>
          </div>
          <div class="col-md-6 mb-3">
            <div class="h-100 p-3 border rounded">
              <h3 class="h5">Technical Issues</h3>
              <p>Report bugs or problems with the website functionality</p>
            </div>
          </div>
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

.card-title {
  color: var(--color-heading);
}

a {
  color: var(--color-primary);
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

.border {
  border-color: var(--color-border) !important;
}

.title {
  color: rgba(255, 255, 255);
}

.btn-primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  transition: all 0.3s;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark, #0056b3);
  border-color: var(--color-primary-dark, #0056b3);
  opacity: 0.9;
}

h3.h5 {
  color: var(--color-heading);
}
</style>
