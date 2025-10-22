import { createApp } from 'vue';
import Home from './Home.vue';

// Define Vue 3 feature flags for better tree-shaking and performance
// See: https://link.vuejs.org/feature-flags
if (typeof window !== 'undefined') {
    window.__VUE_OPTIONS_API__ = true;
    window.__VUE_PROD_DEVTOOLS__ = false;
    window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false;
}



frappe.provide('frappe.PosApp');

frappe.PosApp.posapp = class {
    constructor({ parent }) {
        this.$parent = $(document);
        this.page = parent.page;
        this.make_body();
    }

    make_body() {
        this.$el = this.$parent.find('.main-section');

        const app = createApp(Home);

        SetVueGlobals(app);
        app.mount(this.$el[0]);
    }

    setup_header() {
        // Implement header setup logic here
    }
};