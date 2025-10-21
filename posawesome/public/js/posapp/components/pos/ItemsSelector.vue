<template>
  <div class="items-selector-container">
    <!-- Compact header with filters and counters -->
    <div class="selector-header">
      <div class="header-item">
        <div class="group-select-wrapper">
          <i class="mdi mdi-shape group-icon"></i>
          <select
            v-model="item_group"
            @change="onItemGroupChange"
            class="custom-group-select"
          >
            <option v-for="group in items_group" :key="group" :value="group">
              {{ group }}
            </option>
          </select>
        </div>
      </div>
      <div class="header-item">
        <button class="header-btn coupon-btn" @click="show_coupons">
          <i class="mdi mdi-ticket-percent header-icon"></i>
          <span>{{ couponsCount }} Coupons</span>
        </button>
      </div>
      <div class="header-item">
        <button class="header-btn offer-btn" @click="show_offers">
          <i class="mdi mdi-tag-multiple header-icon"></i>
          <span>{{ offersCount }} Offers</span>
        </button>
      </div>
    </div>

    <div class="selector-body">
      <v-progress-linear
        :active="loading"
        :indeterminate="loading"
        absolute
        top
        color="info"
        height="2"
      ></v-progress-linear>

      <!-- Search fields -->
      <div class="search-row">
        <div class="search-col">
          <div class="search-field-wrapper barcode-field">
            <div class="search-icon">
              <i class="mdi mdi-barcode barcode-icon"></i>
            </div>
            <input
              type="text"
              class="custom-search-input barcode-input"
              placeholder="Scan Barcode"
              v-model="barcode_search"
              @keyup.enter="handle_barcode_input"
              ref="barcode_search"
            />
            <button
              v-if="barcode_search"
              class="clear-btn"
              @click="barcode_search = ''"
              type="button"
            >
              ×
            </button>
          </div>
        </div>

        <div class="search-col">
          <div class="search-field-wrapper name-field">
            <v-progress-linear
              :active="search_loading"
              :indeterminate="search_loading"
              absolute
              top
              color="info"
              height="2"
            ></v-progress-linear>
            <div class="search-icon">
              <i class="mdi mdi-magnify search-icon-element"></i>
            </div>
            <input
              type="text"
              class="custom-search-input name-input"
              placeholder="Search Item"
              v-model="debounce_search"
              @keydown.esc="esc_event"
              ref="debounce_search"
              autofocus
            />
            <button
              v-if="debounce_search"
              class="clear-btn"
              @click="debounce_search = ''"
              type="button"
            >
              ×
            </button>
          </div>
        </div>
      </div>

      <!-- Items display area -->
      <div class="items-display-area">
        <div class="items-content" v-if="items_view == 'card'">
          <div
            class="items-grid"
            ref="itemsScrollArea"
            :style="itemsScrollStyle"
          >
            <div
              v-for="(item, idx) in filtred_items"
              :key="idx"
              class="item-grid-col"
            >
              <v-card hover="hover" @click="add_item(item)" class="item-card">
                <v-img
                  :src="
                    item.image ||
                    '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'
                  "
                  class="white--text align-start item-image"
                  gradient="to bottom, rgba(0,0,0,0), rgba(0,0,0,0.4)"
                >
                  <v-card-text
                    v-if="item.actual_qty !== undefined"
                    class="text-caption px-1 pt-1 text-right"
                  >
                    <span
                      :style="{
                        color: item.actual_qty > 0 ? '#4CAF50' : '#F44336',
                        fontWeight: 'bold',
                      }"
                    >
                      Qty: {{ formatFloat(item.actual_qty) }}
                    </span>
                  </v-card-text>
                </v-img>

                <v-card-text class="text--primary pa-1 text-center">
                  <div
                    class="text-caption"
                    style="font-weight: bold; margin-bottom: 4px"
                  >
                    {{ item.item_name }}
                  </div>

                  <div class="text-caption d-flex justify-space-between">
                    <span class="golden--text">
                      {{ item.stock_uom || "" }}
                    </span>
                    <span class="primary--text" style="font-weight: bold">
                      {{ currencySymbol(item.currency) || ""
                      }}{{ formatCurrency(item.rate) || 0 }}
                    </span>
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </div>
        </div>
        <div class="items-content" v-if="items_view == 'list'">
          <div
            class="items-scrollable"
            ref="itemsScrollArea"
            :style="itemsScrollStyle"
          >
            <v-data-table
              :headers="getItemsHeaders()"
              :items="filtred_items"
              item-key="item_code"
              class="elevation-1"
              hide-default-footer
              :items-per-page="50"
              @click:row="add_item_table"
            >
              <template v-slot:item.rate="{ item }">
                <span class="primary--text">
                  {{ formatCurrency(item.rate) }}
                </span>
              </template>
              <template v-slot:item.actual_qty="{ item }">
                {{ formatFloat(item.actual_qty) }}
              </template>
            </v-data-table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// ===== IMPORTS =====
import { evntBus } from "../../bus";
import format from "../../format";
import { API_MAP } from "../../api_mapper.js";

// Lightweight debounce function (replaces lodash)
// CRITICAL: Preserve 'this' context for Vue component methods
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const context = this; // ✅ Capture the Vue component context
    const later = () => {
      clearTimeout(timeout);
      func.apply(context, args); // ✅ Apply with correct context
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

const EVENT_NAMES = {
  // Item Events
  ADD_ITEM: "add_item",
  SET_ALL_ITEMS: "set_all_items",
  UPDATE_CUR_ITEMS_DETAILS: "update_cur_items_details",
  
  // UI Events
  SHOW_OFFERS: "show_offers",
  SHOW_COUPONS: "show_coupons",
  SHOW_MESSAGE: "show_mesage",
  
  // Configuration Events
  REGISTER_POS_PROFILE: "register_pos_profile",
  UPDATE_CUSTOMER: "update_customer",
  UPDATE_CUSTOMER_PRICE_LIST: "update_customer_price_list",
  
  // Counter Events
  UPDATE_OFFERS_COUNTERS: "update_offers_counters",
  UPDATE_COUPONS_COUNTERS: "update_coupons_counters",
};

const UI_CONFIG = {
  SEARCH_MIN_LENGTH: 3,
  MAX_DISPLAYED_ITEMS: 50,
  MIN_PANEL_HEIGHT: 180,
  BOTTOM_PADDING: 16,
  DEBOUNCE_DELAY: 200,
};

const VIEW_MODES = {
  CARD: "card",
  LIST: "list",
};

const BARCODE_TYPES = {
  SCALE: "scale",
  PRIVATE: "private",
  NORMAL: "normal",
};

// ===== COMPONENT =====
export default {
  name: "ItemsSelector",
  
  mixins: [format],

  // ===== DATA =====
  data() {
    return {
      // POS Configuration
      pos_profile: null,
      flags: {},
      
      // View State
      items_view: VIEW_MODES.LIST,
      item_group: "ALL",
      loading: false,
      search_loading: false,
      
      // Items Data
      items_group: ["ALL"],
      items: [],
      
      // Search State
      search: "",
      first_search: "",
      barcode_search: "",
      
      // Pagination
      itemsPerPage: 1000,
      
      // Counters
      offersCount: 0,
      appliedOffersCount: 0,
      couponsCount: 0,
      appliedCouponsCount: 0,
      
      // Customer Data
      customer_price_list: null,
      customer: null,
      
      // Item Operations
      qty: 1,
      
      // UI State
      itemsScrollHeight: null,
      
      // Internal Flags
      _suppressCustomerWatcher: false,
      _detailsReady: false,
      
      // Caching & Performance
      _itemsMap: new Map(),
    };
  },

  // ===== WATCH =====
  watch: {
    filtred_items(newValue, oldValue) {
      if (newValue.length !== oldValue.length) {
        this.update_items_details(newValue);
      }
      this.scheduleScrollHeightUpdate();
    },

    customer(newVal, oldVal) {
      if (this._suppressCustomerWatcher) {
        this._suppressCustomerWatcher = false;
        return;
      }
      if (oldVal !== undefined && newVal !== oldVal) {
        this.get_items();
      }
    },

    items_view() {
      this.scheduleScrollHeightUpdate();
    },
  },

  // ===== COMPUTED =====
  computed: {
    filtred_items() {
      this.search = this.get_search(this.first_search);

      // Cache expensive operations
      const groupFilter = this.item_group !== "ALL";
      const hasSearch = this.search && this.search.length >= UI_CONFIG.SEARCH_MIN_LENGTH;
      
      let filtred_list = [];
      let filtred_group_list = [];

      // Filter by group - cache toLowerCase results
      if (groupFilter) {
        const lowerGroup = this.item_group.toLowerCase();
        filtred_group_list = this.items.filter((item) =>
          item.item_group.toLowerCase().includes(lowerGroup)
        );
      } else {
        filtred_group_list = this.items;
      }

      // Filter by search term
      if (!hasSearch) {
        filtred_list = filtred_group_list.slice(0, UI_CONFIG.MAX_DISPLAYED_ITEMS);
      } else {
        // Search in item_code - cache toLowerCase result
        const lowerSearch = this.search.toLowerCase();
        filtred_list = filtred_group_list.filter((item) =>
          item.item_code.toLowerCase().includes(lowerSearch)
        );

        // Search in item_name if no results
        if (filtred_list.length === 0) {
          filtred_list = filtred_group_list.filter((item) =>
            item.item_name.toLowerCase().includes(lowerSearch)
          );
        }
      }

      return filtred_list.slice(0, UI_CONFIG.MAX_DISPLAYED_ITEMS);
    },

    itemsScrollStyle() {
      if (!this.itemsScrollHeight) {
        return {};
      }
      return {
        maxHeight: `${this.itemsScrollHeight}px`,
      };
    },

    debounce_search: {
      get() {
        return this.first_search;
      },
      set: debounce(function (newValue) {
        this.first_search = newValue;
        this.performLiveSearch(newValue);
      }, UI_CONFIG.DEBOUNCE_DELAY),
    },
  },

  methods: {
    scheduleScrollHeightUpdate() {
      this.$nextTick(() => {
        this.updateScrollableHeight();
      });
    },

    updateScrollableHeight() {
      const scrollRef = this.$refs.itemsScrollArea;
      const scrollEl = scrollRef ? scrollRef.$el || scrollRef : null;
      
      if (!scrollEl || typeof scrollEl.getBoundingClientRect !== "function") {
        return;
      }

      const viewportHeight =
        window.innerHeight || document.documentElement?.clientHeight || 0;
      
      if (!viewportHeight) {
        return;
      }

      const rect = scrollEl.getBoundingClientRect();
      const available = viewportHeight - rect.top - UI_CONFIG.BOTTOM_PADDING;

      if (Number.isFinite(available)) {
        this.itemsScrollHeight = Math.max(
          UI_CONFIG.MIN_PANEL_HEIGHT,
          Math.floor(available)
        );
      }
    },

    handle_barcode_input() {
      if (!this.barcode_search.trim()) return;

      this.process_barcode(this.barcode_search.trim());
      this.barcode_search = "";
      
      const barcodeInput = document.querySelector('input[placeholder*="Barcode"]');
      if (barcodeInput) barcodeInput.value = "";
    },

    process_barcode(barcode_value) {
      // Single unified method - backend determines barcode type
      console.log("=== BARCODE SCAN ===");
      console.log("Barcode:", barcode_value);
      console.log("Calling unified API...");
      
      frappe.call({
        method: API_MAP.ITEM.GET_BARCODE_ITEM,
        args: { 
          pos_profile: this.pos_profile, 
          barcode_value: barcode_value 
        },
        callback: (response) => {
          console.log("Barcode API Response:", response);
          
          if (response?.message?.item_code) {
            console.log("✓ Item found:", response.message);
            
            // Add item to cart
            this.add_item_to_cart(response.message);
            
            // Show success message with quantity info
            const qty = response.message.qty || 1;
            const qtyText = qty !== 1 ? ` (qty: ${qty})` : '';
            
            evntBus.emit("show_mesage", {
              text: `Added ${response.message.item_name}${qtyText} to cart`,
              color: "success"
            });
          } else {
            console.error("✗ Item not found for barcode:", barcode_value);
            evntBus.emit("show_mesage", {
              text: "Item not found with this barcode",
              color: "error"
            });
          }
        },
        error: (error) => {
          console.error("Barcode API Error:", error);
          evntBus.emit("show_mesage", {
            text: "Error processing barcode",
            color: "error"
          });
        }
      });
    },

    add_item_to_cart(item) {
      evntBus.emit(EVENT_NAMES.ADD_ITEM, item);
    },

    show_offers() {
      evntBus.emit(EVENT_NAMES.SHOW_OFFERS, "true");
    },

    show_coupons() {
      evntBus.emit(EVENT_NAMES.SHOW_COUPONS, "true");
    },

    onItemGroupChange() {
      if (this.debounce_search) {
        this.debounce_search = "";
        this.first_search = "";
      }
      this.get_items();
    },

    get_items() {
      if (!this.pos_profile) {
        evntBus.emit("show_mesage", {
          text: "POS Profile not specified",
          color: "error",
        });
        return;
      }

      const vm = this;
      this.loading = true;
      let search = this.get_search(this.first_search);
      let gr = "";
      let sr = "";

      if (search) {
        sr = search;
      }
      if (vm.item_group != "ALL") {
        gr = vm.item_group.toLowerCase();
      }

      frappe.call({
        method: API_MAP.ITEM.GET_ITEMS,
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: gr,
          search_value: sr,
          customer: vm.customer,
        },
        callback: function (r) {
          if (r.message) {
            vm.items = (r.message || []).map((it) => ({
              item_code: it.item_code,
              item_name: it.item_name,
              item_group: it.item_group, // ✅ Added for filtred_items
              rate: it.rate,
              price_list_rate: it.price_list_rate,
              base_rate: it.base_rate,
              currency: it.currency,
              actual_qty: it.actual_qty,
              stock_uom: it.stock_uom,
              // Empty arrays for compatibility with barcode/batch/serial features
              item_barcode: [],
              serial_no_data: [],
              batch_no_data: [],
            }));
            vm._buildItemsMap();
            evntBus.emit("set_all_items", vm.items);
            vm.loading = false;
            vm.search_loading = false;
            vm.scheduleScrollHeightUpdate();
          }
        },
      });
    },

    _buildItemsMap() {
      this._itemsMap.clear();

      this.items.forEach((item) => {
        // Add search by item_code
        this._itemsMap.set(item.item_code.toLowerCase(), item);

        // Add search by item_name
        this._itemsMap.set(item.item_name.toLowerCase(), item);
      });
    },

    get_items_groups() {
      if (!this.pos_profile) {
        return;
      }

      if (this.pos_profile.item_groups && this.pos_profile.item_groups.length > 0) {
        this.pos_profile.item_groups.forEach((element) => {
          if (element.item_group !== "ALL") {
            this.items_group.push(element.item_group);
          }
        });
      } else {
        const vm = this;
        frappe.call({
          method: API_MAP.ITEM.GET_ITEMS_GROUPS,
          args: {},
          callback: function (r) {
            if (r.message) {
              r.message.forEach((element) => {
                vm.items_group.push(element.name);
              });
            }
          },
        });
      }
    },

    getItemsHeaders() {
      const items_headers = [
        {
          title: "I-Name",
          align: "start",
          sortable: true,
          key: "item_name",
          width: "30%",
        },
        {
          title: "I-Code",
          align: "start",
          sortable: true,
          key: "item_code",
          width: "25%",
        },
        { title: "Price", key: "rate", align: "start", width: "10%" },
        {
          title: "Qty",
          value: "actual_qty",
          align: "center",
          width: "25%",
        },
        { title: "Uom", key: "stock_uom", align: "center", width: "10%" },
      ];

      return items_headers;
    },

    add_item_table(event, item) {
      // Add the item from the table - use the item object directly
      evntBus.emit("add_item", {
        ...item.item,
        qty: this.qty || 1,
      });
      this.qty = 1;
    },

    add_item(item) {
      // Add item from card view
      evntBus.emit("add_item", {
        ...item,
        qty: this.qty || 1,
      });
      this.qty = 1;
    },

    get_search(val) {
      return val || "";
    },

    esc_event() {
      this.first_search = "";
      this.debounce_search = "";
    },

    performLiveSearch(searchValue) {
      const vm = this;

      // Activate search progress bar
      this.search_loading = true;

      // If search is empty, reload all items
      if (!searchValue || searchValue.trim() === "") {
        this.get_items();
        return;
      }

      // Perform live search using get_items
      frappe.call({
        method: API_MAP.ITEM.GET_ITEMS,
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group:
            vm.item_group !== "ALL" ? vm.item_group.toLowerCase() : "",
          search_value: searchValue.trim(),
          customer: vm.customer,
        },
        callback: function (r) {
          // Stop search progress bar
          vm.search_loading = false;

          if (r.message) {
            vm.items = (r.message || []).map((it) => ({
              ...it,
              item_group: it.item_group,
              price_list_rate: it.price_list_rate || it.rate,
              base_rate: it.base_rate || it.rate,
              item_barcode: Array.isArray(it.item_barcode)
                ? it.item_barcode
                : [],
              serial_no_data: Array.isArray(it.serial_no_data)
                ? it.serial_no_data
                : [],
              batch_no_data: Array.isArray(it.batch_no_data)
                ? it.batch_no_data
                : [],
            }));
            vm._buildItemsMap();
            evntBus.emit("set_all_items", vm.items);
          }
        },
        error: function (err) {
          // Stop search progress bar
          vm.search_loading = false;
        },
      });
    },

    update_items_details(items) {
      evntBus.emit("update_cur_items_details", items);
    },

    scan_barcode() {
      const vm = this;
      onScan.attachTo(document, {
        suffixKeyCodes: [],
        keyCodeMapper: function (oEvent) {
          oEvent.stopImmediatePropagation();
          return onScan.decodeKeyEvent(oEvent);
        },
        onScan: function (sCode) {
          // Immediate addition to cart without condition
          vm.trigger_onscan(sCode);
        },
      });
    },

    trigger_onscan(sCode) {
      // Direct barcode processing using existing working method
      console.log("🔍 Auto-scan detected:", sCode);
      this.process_barcode(sCode);
    },
  },

  created: function () {
    this.$nextTick(function () {});
    evntBus.on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile;
      // Set customer without triggering watcher for first time
      this._suppressCustomerWatcher = true;
      this.customer =
        this.pos_profile && this.pos_profile.customer
          ? this.pos_profile.customer
          : this.customer;
      this.get_items();
      this.get_items_groups();
      this.items_view = this.pos_profile.posa_default_card_view
        ? "card"
        : "list";
    });
    // Removed: This was causing infinite recursion
    // evntBus.on("update_cur_items_details", () => {
    //   this.update_items_details(this.filtred_items);
    // });
    evntBus.on("update_offers_counters", (data) => {
      this.offersCount = data.offersCount;
      this.appliedOffersCount = data.appliedOffersCount;
    });
    evntBus.on("update_coupons_counters", (data) => {
      this.couponsCount = data.couponsCount;
      this.appliedCouponsCount = data.appliedCouponsCount;
    });
    evntBus.on("update_customer_price_list", (data) => {
      this.customer_price_list = data;
    });
    evntBus.on("update_customer", (data) => {
      this.customer = data;
    });
  },

  // ===== SECTION 6: LIFECYCLE HOOKS =====
  mounted() {
    this.scan_barcode();
    // Calculate scrollable area as soon as the card renders
    this.scheduleScrollHeightUpdate();
    window.addEventListener("resize", this.scheduleScrollHeightUpdate);
  },

  // Add beforeDestroy to clean up memory
  beforeDestroy() {
    // Clear timer
    if (this._searchDebounceTimer) {
      clearTimeout(this._searchDebounceTimer);
    }
    
    // Clean up event listeners
    evntBus.$off("register_pos_profile");
    evntBus.$off("update_cur_items_details");
    evntBus.$off("update_offers_counters");
    evntBus.$off("update_coupons_counters");
    evntBus.$off("update_customer_price_list");
    evntBus.$off("update_customer");
    
    // Remove window listener
    window.removeEventListener("resize", this.scheduleScrollHeightUpdate);
  },
};
</script>

<style scoped>
/* ===== MAIN CONTAINER ===== */
.items-selector-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  overflow: hidden;
}

/* ===== COMPACT HEADER ===== */
.selector-header {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e0e0e0;
}

.header-item {
  flex: 1;
  min-width: 0;
}

/* Group Select Wrapper */
.group-select-wrapper {
  width: 100%;
  height: 26px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 8px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  position: relative;
}

.group-select-wrapper:hover {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-color: #1976d2;
  box-shadow: 0 2px 6px rgba(25, 118, 210, 0.15);
}

.group-icon {
  color: #1976d2;
  flex-shrink: 0;
  font-size: 14px;
}

.custom-group-select {
  flex: 1;
  height: 100%;
  border: none;
  background: transparent;
  font-size: 0.7rem;
  font-weight: 600;
  color: #1976d2;
  cursor: pointer;
  outline: none;
  padding-right: 16px;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.custom-group-select:focus {
  outline: none;
}

/* Custom dropdown arrow */
.group-select-wrapper::after {
  content: "▼";
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 8px;
  color: #1976d2;
  pointer-events: none;
}

.header-btn {
  width: 100%;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border: none;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  background: white;
  border: 1px solid #e0e0e0;
  color: #1976d2;
}

.header-btn:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.header-btn span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.coupon-btn:hover {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: white;
  border-color: #f57c00;
}

.offer-btn:hover {
  background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
  color: white;
  border-color: #388e3c;
}

.header-icon {
  font-size: 14px;
}

/* ===== SELECTOR BODY ===== */
.selector-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* ===== SEARCH ROW ===== */
.search-row {
  display: flex;
  gap: 3px;
  padding: 4px;
  background: #fafafa;
  border-bottom: 1px solid #e0e0e0;
}

.search-col {
  flex: 1;
  min-width: 0;
}

/* ===== CUSTOM SEARCH FIELDS ===== */
.search-field-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  height: 28px;
  overflow: hidden;
}

.search-field-wrapper:hover {
  border-color: #bdbdbd;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.search-field-wrapper:focus-within {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.barcode-field:focus-within {
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.search-icon {
  display: flex;
  align-items: center;
  padding: 0 6px;
  height: 100%;
}

.barcode-icon {
  color: #4caf50;
  font-size: 16px;
}

.search-icon-element {
  color: #1976d2;
  font-size: 16px;
}

.custom-search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 4px 6px;
  font-size: 0.8rem;
  font-weight: 500;
  color: #333;
  height: 100%;
}

.custom-search-input::placeholder {
  color: #999;
  font-weight: 400;
  font-size: 0.75rem;
}

.custom-search-input:focus::placeholder {
  color: #bdbdbd;
}

.barcode-input {
  color: #2e7d32;
  font-weight: 600;
}

.name-input {
  color: #1565c0;
  font-weight: 500;
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: #999;
  font-size: 18px;
  cursor: pointer;
  margin-right: 2px;
  border-radius: 50%;
  padding: 0;
  line-height: 1;
}

.clear-btn:hover {
  background: #f5f5f5;
  color: #666;
}

.clear-btn:active {
  transform: scale(0.9);
}

/* ===== ITEMS DISPLAY AREA ===== */
/* Items Grid */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  padding: 8px;
  overflow-y: auto;
}

.item-grid-col {
  display: flex;
  flex-direction: column;
}

@media (max-width: 600px) {
  .items-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 601px) and (max-width: 960px) {
  .items-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 961px) and (max-width: 1264px) {
  .items-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1265px) and (max-width: 1904px) {
  .items-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (min-width: 1905px) {
  .items-grid {
    grid-template-columns: repeat(8, 1fr);
  }
}

.items-display-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.items-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.items-scrollable {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px;
}

/* Special styling for table view - no padding, full height */
.items-content:has(.v-data-table) .items-scrollable {
  padding: 0;
  display: flex;
  flex-direction: column;
}

/* ===== ITEM CARD STYLES ===== */
.item-card {
  height: 100%;
  min-height: 110px !important;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  border-radius: 6px !important;
}

.item-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.item-card .v-card__text {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 50px !important;
  padding: 4px !important;
}

.item-card .v-img {
  position: relative;
  height: 60px !important;
}

.item-card .v-img .v-card__text {
  position: absolute;
  top: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 3px;
  margin: 3px;
  padding: 1px 4px !important;
  font-size: 0.65rem !important;
}

.item-card .text-caption {
  font-size: 0.7rem !important;
  line-height: 1.2 !important;
}

/* ===== DATA TABLE STYLES ===== */
.v-data-table {
  font-size: 0.75rem !important;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.v-data-table .v-data-table__wrapper {
  flex: 1;
  overflow-y: auto !important;
  overflow-x: hidden;
  max-height: none !important;
}

.v-data-table .v-data-table__wrapper table {
  font-size: 0.7rem !important;
}

.v-data-table .v-data-table__wrapper table th,
.v-data-table .v-data-table__wrapper table td {
  padding: 4px 6px !important;
  font-size: 0.7rem !important;
  font-weight: 500 !important;
  line-height: 1.2 !important;
}

.v-data-table .v-data-table__wrapper table th {
  font-weight: 600 !important;
  font-size: 0.75rem !important;
  background-color: #f5f5f5 !important;
}

.v-data-table .v-data-table__wrapper table tr {
  cursor: pointer;
}

.v-data-table .v-data-table__wrapper table tr:hover {
  background: #e3f2fd !important;
}

/* ===== SCROLLBAR STYLING ===== */
.items-scrollable::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

.items-scrollable::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.items-scrollable::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  border-radius: 3px;
}

.items-scrollable::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
}

/* ===== RESPONSIVE ADJUSTMENTS ===== */
@media (max-width: 1280px) {
  .item-card {
    min-height: 100px !important;
  }

  .item-card .v-img {
    height: 55px !important;
  }

  .header-btn {
    font-size: 0.65rem;
  }
}

@media (max-width: 1024px) {
  .selector-header {
    padding: 3px;
    gap: 3px;
  }

  .search-row {
    padding: 3px;
    gap: 2px;
  }

  .item-card {
    min-height: 90px !important;
  }

  .item-card .v-img {
    height: 50px !important;
  }

  .header-btn {
    height: 24px;
    font-size: 0.6rem;
  }

  .search-field-wrapper {
    height: 26px;
  }
}
</style>