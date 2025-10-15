<template>
  <v-app>
    <v-main>
      <Navbar @changePage="setPage" />
      <keep-alive>
        <component :is="page" class="container1" />
      </keep-alive>
    </v-main>
  </v-app>
</template>

<script>
import Navbar from "./components/Navbar.vue";
import POS from "./components/pos/Pos.vue";

export default {
  data: function () {
    return {
      page: "POS",
    };
  },
  components: {
    Navbar,
    POS,
  },
  methods: {
    setPage(page) {
      this.page = page;
    },
  },
};
</script>

<style scoped>
.container1 {
  margin: 0 auto;
  max-width: 100%;
  width: 100%;
  min-height: calc(100vh - 60px);
  padding: 1rem 0;
}

/* For very small screens, remove margins and use full width */
@media (max-width: 1024px) {
  .container1 {
    width: 100%;
    margin: 0;
    min-height: calc(100vh - 60px); /* Adjust height for smaller screens */
    overflow: hidden;
  }
}

/* For mobile devices */
@media (max-width: 768px) {
  .container1 {
    min-height: calc(100vh - 50px);
  }
}

/* Optimized for cashier screens - no browser zoom needed */
.v-application {
  font-size: 0.8rem !important; /* Slightly larger for better readability */
}

.v-btn {
  font-size: 0.75rem !important;
  padding: 6px 12px !important;
  min-height: 28px !important;
}

.v-text-field {
  font-size: 0.8rem !important;
}

.v-text-field .v-field {
  min-height: 32px !important;
}

.v-text-field .v-field__input {
  padding: 6px 12px !important;
  font-size: 0.8rem !important;
}

.v-data-table {
  font-size: 0.8rem !important;
}

.v-data-table .v-data-table__wrapper table {
  font-size: 0.8rem !important;
}

.v-data-table .v-data-table__wrapper table th,
.v-data-table .v-data-table__wrapper table td {
  padding: 6px 8px !important;
  font-size: 0.8rem !important;
}

.v-card {
  padding: 8px !important;
}

.v-row {
  margin: -2px !important;
}

.v-col {
  padding: 2px !important;
}

/* Optimized select elements for cashier screens */
.v-select {
  font-size: 0.8rem !important;
}

.v-select .v-field {
  min-height: 32px !important;
}

.v-select .v-field__input {
  padding: 6px 12px !important;
  font-size: 0.8rem !important;
}
</style>
