<template>
  <div class="items-selector-container">
    <!-- Compact header with filters and counters -->
    <div class="selector-header">
      <div class="header-item">
        <div class="group-select-wrapper">
          <v-icon size="14" class="group-icon">mdi-shape</v-icon>
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
          <v-icon size="14">mdi-ticket-percent</v-icon>
          <span>{{ couponsCount }} Coupons</span>
        </button>
      </div>
      <div class="header-item">
        <button class="header-btn offer-btn" @click="show_offers">
          <v-icon size="14">mdi-tag-multiple</v-icon>
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
              <v-icon color="success" size="16">mdi-barcode</v-icon>
            </div>
            <input
              type="text"
              class="custom-search-input barcode-input"
              placeholder="Scan Barcode"
              v-model="barcode_search"
              @input="handle_barcode_input"
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
              <v-icon color="primary" size="16">mdi-magnify</v-icon>
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

        <div class="search-col-checkbox" v-if="pos_profile.posa_new_line">
          <v-checkbox
            v-model="new_line"
            color="accent"
            value="true"
            label="New Line"
            dense
            hide-details
            class="compact-checkbox"
          ></v-checkbox>
        </div>
      </div>

      <!-- Items display area -->
      <div class="items-display-area">
        <div class="items-content" v-if="items_view == 'card'">
          <v-row
            dense
            class="items-scrollable"
            ref="itemsScrollArea"
            :style="itemsScrollStyle"
          >
            <v-col
              v-for="(item, idx) in filtred_items"
              :key="idx"
              xl="2"
              lg="3"
              md="4"
              sm="6"
              cols="6"
              min-height="50"
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
                        color: item.actual_qty > 0 ? '#F44336' : '#4CAF50',
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
            </v-col>
          </v-row>
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
              :items-per-page="-1"
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
// ===== SECTION 1: IMPORTS =====
import { evntBus } from "../../bus";
import format from "../../format";
import _ from "lodash";
// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],
  // ===== SECTION 3: DATA =====
  data: () => {
    return {
      pos_profile: "",
      flags: {},
      items_view: "list",
      item_group: "ALL",
      loading: false,
      search_loading: false,
      items_group: ["ALL"],
      items: [],
      search: "",
      first_search: "",
      barcode_search: "",
      itemsPerPage: 1000,
      offersCount: 0,
      appliedOffersCount: 0,
      couponsCount: 0,
      appliedCouponsCount: 0,
      customer_price_list: null,
      customer: null,
      new_line: false,
      qty: 1,
      // Store dynamic scroll height for grid/table wrapper
      itemsScrollHeight: null,
      _suppressCustomerWatcher: false,
      _detailsReady: false,

      // Remove all types of cache for direct speed
      _itemsMap: new Map(), // For quick search in items only
    };
  },

  // ===== SECTION 4: WATCH =====
  watch: {
    filtred_items(new_value, old_value) {
      if (new_value.length != old_value.length) {
        this.update_items_details(new_value);
      }
      // Refresh scroll height whenever the dataset changes size
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
    new_line() {
      evntBus.emit("set_new_line", this.new_line);
    },
    items_view() {
      // Recompute scroll area when toggling views
      this.scheduleScrollHeightUpdate();
    },
  },

  // ===== SECTION 5: METHODS =====
  methods: {
    // ===============================
    // Layout helpers for scroll panel
    // ===============================
    scheduleScrollHeightUpdate() {
      // Defer measurement until DOM updates settle
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
      const bottomPadding = 16; // Keep a tiny gap above footer
      const available = viewportHeight - rect.top - bottomPadding;
      const minPanelHeight = 180; // Enough space to show multiple items

      if (Number.isFinite(available)) {
        this.itemsScrollHeight = Math.max(
          minPanelHeight,
          Math.floor(available)
        );
      }
    },

    // ========================================
    // Barcode search functions (normal/private/weight)
    // ========================================
    // Automatic processing when placing barcode
    handle_barcode_input() {
      if (!this.barcode_search.trim()) return;

      // Send to backend and immediate clearing
      this.analyze_barcode_type(this.barcode_search.trim());
      this.barcode_search = "";
      const barcodeInput = document.querySelector(
        'input[placeholder*="Barcode"]'
      );
      if (barcodeInput) barcodeInput.value = "";
    },

    // Central function to distribute barcode according to POS Profile settings
    analyze_barcode_type(barcode_value) {
      // 1. Check weight barcode first
      if (this.process_scale_barcode(barcode_value)) {
        return;
      }

      // 2. Check private barcode second
      if (this.process_private_barcode(barcode_value)) {
        return;
      }

      // 3. Normal barcode as last option
      this.process_normal_barcode(barcode_value);
    },

    // Weight barcode processing (check + search)
    process_scale_barcode(barcode_value) {
      const posa_enable_scale_barcode =
        this.pos_profile?.posa_enable_scale_barcode;
      const posa_scale_barcode_start =
        this.pos_profile?.posa_scale_barcode_start;
      const posa_scale_barcode_lenth =
        this.pos_profile?.posa_scale_barcode_lenth;

      // Check conditions
      if (
        posa_enable_scale_barcode === 1 &&
        posa_scale_barcode_start &&
        posa_scale_barcode_lenth &&
        barcode_value.startsWith(posa_scale_barcode_start) &&
        barcode_value.length === posa_scale_barcode_lenth
      ) {
        // Search for barcode
        frappe.call({
          method: "posawesome.posawesome.api.item.search_scale_barcode",
          args: { pos_profile: this.pos_profile, barcode_value: barcode_value },
          callback: (response) => {
            if (response?.message?.item_code) {
              this.add_item_to_cart(response.message);
              evntBus.emit("show_mesage", {
                text: `Added ${response.message.item_name} to cart (weight)`,
                color: "success",
              });
            } else {
              evntBus.emit("show_mesage", {
                text: "Item not found with weight barcode",
                color: "error",
              });
            }
          },
        });
        return true;
      }
      return false;
    },

    // Private barcode processing (check + search)
    process_private_barcode(barcode_value) {
      const posa_enable_private_barcode =
        this.pos_profile?.posa_enable_private_barcode;
      const posa_private_barcode_lenth =
        this.pos_profile?.posa_private_barcode_lenth;
      const posa_private_item_code_length =
        this.pos_profile?.posa_private_item_code_length;

      // Check conditions
      if (
        posa_enable_private_barcode === 1 &&
        posa_private_barcode_lenth &&
        posa_private_item_code_length &&
        barcode_value.length === posa_private_barcode_lenth
      ) {
        // Search for barcode
        frappe.call({
          method: "posawesome.posawesome.api.item.search_private_barcode",
          args: { pos_profile: this.pos_profile, barcode_value: barcode_value },
          callback: (response) => {
            if (response?.message?.item_code) {
              this.add_item_to_cart(response.message);
              evntBus.emit("show_mesage", {
                text: `Added ${response.message.item_name} to cart (private)`,
                color: "success",
              });
            } else {
              evntBus.emit("show_mesage", {
                text: "Item not found with private barcode",
                color: "error",
              });
            }
          },
        });
        return true;
      }
      return false;
    },

    // Normal barcode processing (direct search)
    process_normal_barcode(barcode_value) {
      frappe.call({
        method: "posawesome.posawesome.api.item.search_items_barcode",
        args: { pos_profile: this.pos_profile, barcode_value: barcode_value },
        callback: (response) => {
          if (response?.message?.item_code) {
            this.add_item_to_cart(response.message);
            evntBus.emit("show_mesage", {
              text: `Added ${response.message.item_name} to cart (normal)`,
              color: "success",
            });
          } else {
            evntBus.emit("show_mesage", {
              text: "Item not found with barcode",
              color: "error",
            });
          }
        },
      });
    },

    add_item_to_cart(item) {
      // Add item to cart
      evntBus.emit("add_item", item);
    },

    // ========================================
    // Search functions by name/code/batch/serial
    // ========================================
    show_offers() {
      evntBus.emit("show_offers", "true");
    },
    show_coupons() {
      evntBus.emit("show_coupons", "true");
    },

    onItemGroupChange() {
      // Clear search when group changes to avoid confusion
      if (this.debounce_search) {
        this.debounce_search = "";
        this.first_search = "";
      }

      this.get_items();
    },

    // Improve function to get items
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
        method: "posawesome.posawesome.api.item.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: gr,
          search_value: sr,
          customer: vm.customer,
        },
        callback: function (r) {
          if (r.message) {
            // Simple data mapping - only essential fields
            // Backend returns: item_code, item_name, item_group, stock_uom,
            // rate, price_list_rate, base_rate, currency, actual_qty
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

    // Helper function to build items map for quick search
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

      if (this.pos_profile.item_groups.length > 0) {
        this.pos_profile.item_groups.forEach((element) => {
          if (element.item_group !== "All Item Groups") {
            this.items_group.push(element.item_group);
          }
        });
      } else {
        const vm = this;
        frappe.call({
          method: "posawesome.posawesome.api.item.get_items_groups",
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
          title: "Item Name",
          align: "start",
          sortable: true,
          key: "item_name",
          width: "30%",
        },
        {
          title: "Code",
          align: "start",
          sortable: true,
          key: "item_code",
          width: "25%",
        },
        { title: "Price", key: "rate", align: "start", width: "10%" },
        {
          title: "Available Quantity",
          value: "actual_qty",
          align: "center",
          width: "25%",
        },
        { title: "Unit", key: "stock_uom", align: "center", width: "10%" },
      ];

      return items_headers;
    },

    // Improve function to add item
    add_item_table(event, item) {
      console.log(
        "ItemsSelector.vue(add_item_table): Added",
        item.item.item_code
      );
      // إضافة الصنف كما هو من API مع الحد الأدنى من التعديلات
      evntBus.emit("add_item", {
        ...item.item,
        qty: this.qty || 1, // فقط الكمية المطلوبة
      });
      this.qty = 1;
    },

    add_item(item) {
      console.log("ItemsSelector.vue(add_item): Added", item.item_code);
      // إضافة الصنف كما هو من API مع الحد الأدنى من التعديلات
      evntBus.emit("add_item", {
        ...item,
        qty: this.qty || 1, // فقط الكمية المطلوبة
      });
      this.qty = 1;
    },

    // Improve search processing function
    enter_event() {
      let match = false;

      // Improve verification of search items existence
      if (!this.first_search || this.first_search.trim() === "") {
        // Don't show error if nothing entered in search
        return;
      }

      if (!this.filtred_items.length) {
        evntBus.emit("show_mesage", {
          text: "No items found matching search",
          color: "warning",
        });
        return;
      }

      this.get_items();
      const qty = this.get_item_qty(this.first_search);
      const new_item = { ...this.filtred_items[0] };

      // Set quantity correctly always
      const parsedQty = Number(qty);
      const currentQty = Number(this.qty);

      if (parsedQty > 0) {
        new_item.qty = parsedQty;
      } else if (currentQty > 0) {
        new_item.qty = currentQty;
      } else {
        new_item.qty = 1;
      }

      // Make sure stock_qty is defined and numeric
      const convFactor = Number(new_item.conversion_factor || 1);
      new_item.stock_qty = new_item.qty * convFactor;

      // Improve barcode search
      if (new_item.item_barcode) {
        for (const element of new_item.item_barcode) {
          if (this.search === element.barcode) {
            new_item.uom = element.posa_uom;
            match = true;
            break;
          }
        }
      }

      // Improve serial number search
      if (!new_item.to_set_serial_no && new_item.has_serial_no) {
        for (const element of new_item.serial_no_data) {
          if (this.search && element.serial_no === this.search) {
            new_item.to_set_serial_no = this.first_search;
            match = true;
            break;
          }
        }
      }

      if (this.flags.serial_no) {
        new_item.to_set_serial_no = this.flags.serial_no;
      }

      // Improve batch number search
      if (!new_item.to_set_batch_no && new_item.has_batch_no) {
        for (const element of new_item.batch_no_data) {
          if (this.search && element.batch_no === this.search) {
            new_item.to_set_batch_no = this.first_search;
            new_item.batch_no = this.first_search;
            match = true;
            break;
          }
        }
      }

      if (this.flags.batch_no) {
        new_item.to_set_batch_no = this.flags.batch_no;
      }

      if (match) {
        this.add_item(new_item);
        this._resetSearch();
      } else {
      }
    },

    // Helper function to reset search
    _resetSearch() {
      this.search = null;
      this.first_search = null;
      this.debounce_search = null;
      this.flags.serial_no = null;
      this.flags.batch_no = null;
      this.qty = 1;
      this.$refs.debounce_search.focus();
    },

    search_onchange() {
      // Search by name/code/batch/serial (not barcode)
      this._performItemSearch();
    },

    // Live search function with 200ms debounce
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
        method: "posawesome.posawesome.api.item.get_items",
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
              item_group: it.item_group, // ✅ Added
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

    _performItemSearch() {
      const vm = this;

      // If search is empty, do nothing
      if (!vm.debounce_search || vm.debounce_search.trim() === "") {
        vm.items = vm.originalItems || [];
        return;
      }

      // Search by name/code/batch/serial using get_items
      frappe.call({
        method: "posawesome.posawesome.api.item.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: "",
          search_value: vm.debounce_search.trim(),
          customer: vm.customer,
        },
        callback: function (r) {
          if (r.message && r.message.length > 0) {
            // Results found, display for selection
            vm.items = (r.message || []).map((it) => ({
              ...it,
              item_group: it.item_group, // ✅ Added
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
          } else {
            // No results
            vm.items = [];
            evntBus.emit("show_mesage", {
              text: "No results found for search",
              color: "warning",
            });
          }
        },
      });
    },

    _performSearch() {
      const vm = this;

      // If search is empty, do nothing
      if (!vm.debounce_search || vm.debounce_search.trim() === "") {
        return;
      }

      // Update search
      vm.first_search = vm.debounce_search;
      vm.search = vm.debounce_search;

      // Search for barcode directly
      vm.search_barcode_from_server(vm.debounce_search);
    },

    get_item_qty(first_search) {
      // Set quantity correctly always
      const currentQty = Number(this.qty);
      let scal_qty = currentQty > 0 ? currentQty : 1;

      return scal_qty;
    },

    get_search(first_search) {
      return first_search || "";
    },

    esc_event() {
      this._resetSearch();
    },

    // Improve function to update item details using get_items
    update_items_details(items) {
      const vm = this;
      // Avoid triggering on initial load — wait until first list is displayed
      if (!this._detailsReady) {
        this._detailsReady = true;
        return;
      }

      // Get item codes from the items to update
      const item_codes = items.map((item) => item.item_code);

      frappe.call({
        method: "posawesome.posawesome.api.item.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: "",
          search_value: "", // Empty search to get all items
          customer: vm.customer,
        },
        callback: function (r) {
          if (r.message) {
            // Use Map for faster search
            const updatedItemsMap = new Map();
            (r.message || []).forEach((item) => {
              const safeItem = {
                ...item,
                item_group: item.item_group, // ✅ Added
                item_barcode: Array.isArray(item.item_barcode)
                  ? item.item_barcode
                  : [],
                serial_no_data: Array.isArray(item.serial_no_data)
                  ? item.serial_no_data
                  : [],
                batch_no_data: Array.isArray(item.batch_no_data)
                  ? item.batch_no_data
                  : [],
              };
              updatedItemsMap.set(safeItem.item_code, safeItem);
            });

            // Update only the items that were passed in
            items.forEach((item) => {
              const updated_item = updatedItemsMap.get(item.item_code);
              if (updated_item) {
                item.actual_qty = updated_item.actual_qty;
                item.serial_no_data = updated_item.serial_no_data;
                item.batch_no_data = updated_item.batch_no_data;
                item.item_uoms = updated_item.item_uoms;
                item.rate = updated_item.rate;
                item.currency = updated_item.currency;
              }
            });
          }
        },
      });
    },

    update_cur_items_details() {
      this.update_items_details(this.filtred_items);
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

    // Improve barcode processing function
    trigger_onscan(sCode) {
      // Direct barcode processing
      this.analyze_barcode_type(sCode);
    },

    // Direct barcode search from server without cache - optimized for maximum speed
    search_barcode_from_server(barcode) {
      const vm = this;

      // Use get_items to search by barcode
      frappe.call({
        method: "posawesome.posawesome.api.item.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: "",
          search_value: barcode,
          customer: vm.customer,
        },
        callback: function (r) {
          if (r.message && r.message.length > 0) {
            // Item found, add to cart directly
            const found_item = r.message[0];

            const new_item = { ...found_item };
            new_item.qty = vm.qty;
            vm.add_item(new_item);
            vm._resetSearch();

            evntBus.emit("show_mesage", {
              text: `Item found: ${found_item.item_name}`,
              color: "success",
            });
          } else {
            // Item not found
            evntBus.emit("show_mesage", {
              text: `Item not found for barcode: ${barcode}`,
              color: "error",
            });
            vm._resetSearch();
          }
        },
        error: function (err) {
          evntBus.emit("show_mesage", {
            text: "Error searching for barcode",
            color: "error",
          });
          vm._resetSearch();
        },
      });
    },
  },

  computed: {
    // Remove all types of cache - direct filtering
    filtred_items() {
      this.search = this.get_search(this.first_search);

      let filtred_list = [];

      let filtred_group_list = [];

      // Filter by group
      if (this.item_group != "ALL") {
        filtred_group_list = this.items.filter((item) =>
          item.item_group.toLowerCase().includes(this.item_group.toLowerCase())
        );
      } else {
        filtred_group_list = this.items;
      }

      // Simple search logic - only item_code and item_name
      if (!this.search || this.search.length < 3) {
        filtred_list = filtred_group_list.slice(0, 50);
      } else if (this.search) {
        // Search in item_code
        filtred_list = filtred_group_list.filter((item) =>
          item.item_code.toLowerCase().includes(this.search.toLowerCase())
        );

        // Search in item_name if no results
        if (filtred_list.length === 0) {
          filtred_list = filtred_group_list.filter((item) =>
            item.item_name.toLowerCase().includes(this.search.toLowerCase())
          );
        }
      }

      // Final filtering - show all items directly
      filtred_list = filtred_list.slice(0, 50);

      return filtred_list;
    },

    // Inline style for scroll host (keeps template tidy)
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
      set: _.debounce(function (newValue) {
        this.first_search = newValue;
        // Trigger live search after 200ms
        this.performLiveSearch(newValue);
      }, 200),
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
    evntBus.on("update_cur_items_details", () => {
      this.update_cur_items_details();
    });
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
    this._searchCache.clear();
    this._filteredItemsCache.clear();
    this._itemsMap.clear();
    if (this._searchDebounceTimer) {
      clearTimeout(this._searchDebounceTimer);
    }
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
  transition: all 0.2s ease;
  position: relative;
}

.group-select-wrapper:hover {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-color: #1976d2;
  box-shadow: 0 2px 6px rgba(25, 118, 210, 0.15);
  transform: translateY(-1px);
}

.group-select-wrapper .group-icon {
  color: #1976d2;
  flex-shrink: 0;
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
  transition: all 0.2s ease;
  background: white;
  border: 1px solid #e0e0e0;
  color: #1976d2;
}

.header-btn:hover {
  transform: translateY(-1px);
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

.search-col-checkbox {
  display: flex;
  align-items: center;
  padding: 0 4px;
}

.compact-checkbox {
  transform: scale(0.85);
  transform-origin: left center;
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
  transition: all 0.2s ease;
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
  transition: all 0.2s ease;
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
  transition: all 0.2s ease;
  border-radius: 6px !important;
}

.item-card:hover {
  transform: translateY(-2px);
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
  transition: background 0.2s ease;
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

.v-table > .v-table__wrapper > table > tbody > tr > th,
.v-table > .v-table__wrapper > table > tfoot > tr > th,
.v-table > .v-table__wrapper > table > thead > tr > th {
  height: 0 !important;
}
</style>
