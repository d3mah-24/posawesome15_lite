import { createApp } from "vue";
import Home from "./Home.vue";
import { API_MAP } from "./api_mapper.js";

// Define Vue 3 feature flags for better tree-shaking and performance
// See: https://link.vuejs.org/feature-flags
if (typeof window !== "undefined") {
  window.__VUE_OPTIONS_API__ = true;
  window.__VUE_PROD_DEVTOOLS__ = false;
  window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false;
}

// Define SetVueGlobals function to set up Vue global properties
function SetVueGlobals(app) {
  // Set up global properties that components might need
  app.config.globalProperties.$frappe = frappe;
  app.config.globalProperties.$__ = __; // Frappe's translation function

  // Make common Frappe utilities available globally
  if (typeof frappe !== "undefined") {
    app.config.globalProperties.$call = frappe.call;
    app.config.globalProperties.$format = frappe.format;
    app.config.globalProperties.$db = frappe.db;
  }

  // Add posTranslations globally
  app.config.globalProperties.$posT = (key) =>
    window.posTranslations?.t(key) || key;
}

frappe.provide("frappe.PosApp");

frappe.PosApp.posapp = class {
  constructor({ parent }) {
    this.$parent = $(document);
    this.page = parent.page;

    // Initialize translations first
    this.initTranslations().then(() => {
      this.make_body();
    });
  }

  async initTranslations() {
    window.posTranslations = {
      state: {
        lang: "en",
        translations: {},
        loadedLangs: {},
      },

      async load(lang = "en") {
        lang = lang.toLowerCase();
        if (this.state.loadedLangs[lang]) {
          this.state.lang = lang;
          return this.state.translations;
        }

        try {
          frappe.call({
            method: API_MAP.TRANSLATIONS.GET_TRANSLATIONS,
            args: {
              lang: lang,
            },
            callback: (r) => {
              if (r && r.message) {
                const result = r.message;
                if (result.success && result.translations) {
                  this.state.translations = result.translations;
                  this.state.loadedLangs[lang] = true;
                  this.state.lang = lang;
                  if (lang === "ar") {
                    document.documentElement.setAttribute("dir", "rtl");
                  } else {
                    document.documentElement.removeAttribute("dir");
                  }
                }
              }
            },
            error: () => {
              console.error("Failed to load translations for lang:", lang);
            },
          });
        } catch (err) {
          console.error("Translation load failed", err);
        }
        return this.state.translations;
      },

      t(key) {
        return this.state.translations[key] || key;
      },
    };

    let posaLang = "en";
    let currentPosProfile = null;
    await frappe.call({
      method: API_MAP.POS_PROFILE.GET_CURRENT_PROFILE_LANG,
      callback: async (r) => {
        if (r && r.message) {
          currentPosProfile = r.message;
        }
        console.log("Current POS Profile:", currentPosProfile);
        if (currentPosProfile && currentPosProfile.posa_language) {
          posaLang = currentPosProfile.posa_language.toLowerCase();
        }

        if (window.posTranslations) {
          await window.posTranslations.load(posaLang);

          // Translate static elements
          document.querySelectorAll("[data-pos-t]").forEach((el) => {
            const key = el.dataset.posT;
            el.textContent = window.posTranslations.t(key);
          });
        }
      },
    });
  }

  make_body() {
    this.$el = this.$parent.find(".main-section");

    const app = createApp(Home);

    SetVueGlobals(app);
    app.mount(this.$el[0]);
  }

  setup_header() {
    // Implement header setup logic here
  }
};
