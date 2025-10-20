import { createApp } from 'vue';
import Home from './Home.vue';
import { createVuetify } from 'vuetify';

// Define Vue 3 feature flags for better tree-shaking and performance
// See: https://link.vuejs.org/feature-flags
if (typeof window !== 'undefined') {
    window.__VUE_OPTIONS_API__ = true;
    window.__VUE_PROD_DEVTOOLS__ = false;
    window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false;
}

// SMART TREE-SHAKING: Import all components but only load what's used in templates
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';



frappe.provide('frappe.PosApp');

frappe.PosApp.posapp = class {
    constructor({ parent }) {
        this.$parent = $(document);
        this.page = parent.page;
        this.make_body();
    }

    make_body() {
        this.$el = this.$parent.find('.main-section');

        const vuetify = createVuetify({
            // AUTOMATIC TREE-SHAKING: All components available, only used ones bundled
            components,
            directives,
            theme: {
                themes: {
                    light: {
                        background: '#FFFFFF',
                        primary: '#0097A7',
                        secondary: '#00BCD4',
                        accent: '#9575CD',
                        success: '#66BB6A',
                        info: '#2196F3',
                        warning: '#FF9800',
                        error: '#E86674',
                        orange: '#E65100',
                        golden: '#A68C59',
                        badge: '#F5528C',     
                        customPrimary: '#085294',
                    },
                },
            },
        });

        const app = createApp(Home);

        app.use(vuetify);
        SetVueGlobals(app);
        app.mount(this.$el[0]);
    }

    setup_header() {
        // Implement header setup logic here
    }
};