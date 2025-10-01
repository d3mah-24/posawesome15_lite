<template>
  <v-app class="">
    <v-main>
      <Navbar @changePage="setPage" />
      <keep-alive>
        <component :is="page" class="mx-4 my-4 container1" />
      </keep-alive>
    </v-main>
  </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue';
import POS from './components/pos/Pos.vue';

export default {
  data: function () {
    return {
      page: 'POS',
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
    remove_frappe_nav() {
      this.$nextTick(function () {
        // Your existing logic here
      });
    },
  },
  mounted() {
    this.remove_frappe_nav();
  },
  updated() {},
  created: function () {
    setTimeout(() => {
      this.remove_frappe_nav();
    }, 1000);
  },
};
</script>

<style scoped>
.container1 {
  margin: 0 auto;
  max-width: min(1024px, 100%);
  width: calc(100% - 2rem); /* Account for mx-4 margins */
  min-height: 100vh;
  overflow-y: auto;
}

/* Custom scrollbar styling for main container */
.container1::-webkit-scrollbar {
  width: 10px;
}

.container1::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 5px;
}

.container1::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 5px;
}

.container1::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Fallback for Firefox */
.container1 {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

/* Here first i take the full screen width then minus 2rem from left and right both side
 and set the max-width to 1024px so that it doesn't exceed on larger screens
*/

/* For very small screens, remove margins and use full width */
@media (max-width: 1024px) {
  .container1 {
    width: 100%;
    margin: 0;
    min-height: calc(100vh - 60px); /* Adjust height for smaller screens */
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