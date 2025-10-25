<template>
  <div class="app-container">
    <main class="main-content">
      <Navbar @changePage="setPage" />
      <keep-alive>
        <component :is="page" class="container1" />
      </keep-alive>
    </main>
  </div>
</template>

<script src="./Home.js" />

<style scoped>
.container1 {
  margin: 0 auto;
  max-width: 100%;
  width: 100%;
  min-height: calc(100vh - 32px);
  /* Updated to match actual navbar height */
}

/* For very small screens, remove margins and use full width */
@media (max-width: 1024px) {
  .container1 {
    width: 100%;
    margin: 0;
    min-height: calc(100vh - 32px);
    /* Updated to match actual navbar height */
    overflow: hidden;
  }
}

/* For mobile devices */
@media (max-width: 768px) {
  .container1 {
    min-height: calc(100vh - 32px);
    /* Updated to match actual navbar height */
  }
}

/* Optimized for cashier screens - no browser zoom needed */
.app-container {
  font-size: 0.8rem;
  /* Slightly larger for better readability */
}

.btn {
  font-size: 0.75rem;
  padding: 6px 12px;
  min-height: 28px;
}

.text-input {
  font-size: 0.8rem;
}

.text-input {
  min-height: 32px;
  padding: 6px 12px;
  font-size: 0.8rem;
}

.data-table {
  font-size: 0.8rem;
}

.data-table table {
  font-size: 0.8rem;
}

.data-table th,
.data-table td {
  padding: 6px 8px;
  font-size: 0.8rem;
}

.card {
  padding: 8px;
}

.d-flex {
  margin: -2px;
}

.d-flex>* {
  padding: 2px;
}

/* Optimized select elements for cashier screens */
.select-input {
  font-size: 0.8rem;
  min-height: 32px;
  padding: 6px 12px;
}
</style>
