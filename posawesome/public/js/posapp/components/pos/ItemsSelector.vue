<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div>

  <!-- Filters and counters (no extra top margin) -->
    <v-card class="cards mb-2 pa-2 grey lighten-5">
      <v-row no-gutters align="center">
        <v-col cols="4" class="pa-1">
          <v-select
            :items="items_group"
            label="Item Group"
            dense
            outlined
            hide-details
            v-model="item_group"
            @update:modelValue="onItemGroupChange"
            class="header-control"
          ></v-select>
        </v-col>
        <v-col cols="4" class="pa-1">
          <v-btn small block color="primary" text @click="show_coupons" class="header-control"
            >{{ couponsCount }} Coupons</v-btn
          >
        </v-col>
        <v-col cols="4" class="pa-1">
          <v-btn small block color="primary" text @click="show_offers" class="header-control"
            >{{ offersCount }} Offers : {{ appliedOffersCount }}
            Applied</v-btn
          >
        </v-col>
      </v-row>
    </v-card>

    <v-card
      class="selection mx-auto grey lighten-5 d-flex flex-column flex-grow-1"
      style="min-height: 0;"
    >
      <v-progress-linear
        :active="loading"
        :indeterminate="loading"
        absolute
        top
        color="info"
      ></v-progress-linear>
  <v-row class="items px-2 py-1" style="flex: 1; min-height: 0;">
        <!-- Barcode search field -->
        <v-col cols="6" class="pb-0 mb-2">
          <v-text-field
            dense
            clearable
            outlined
            color="success"
            label="Search by Barcode"
            hint="Normal/Private/Weight barcode - automatically added to cart"
            background-color="white"
            hide-details
            v-model="barcode_search"
            @input="handle_barcode_input"
            ref="barcode_search"
          >
            <template v-slot:prepend-inner>
              <v-icon color="success">mdi-barcode</v-icon>
            </template>
          </v-text-field>
        </v-col>
        
        <!-- Name or code search field -->
        <v-col cols="6" class="pb-0 mb-2">
          <v-progress-linear
            :active="search_loading"
            :indeterminate="search_loading"
            absolute
            top
            color="info"
            height="3"
          ></v-progress-linear>
          <v-text-field
            dense
            clearable
            autofocus
            outlined
            color="primary"
            label="Search by Name or Code"
            hint="Direct search - Item name/Item code/Batch/Serial number"
            background-color="white"
            hide-details
            v-model="debounce_search"
            @keydown.esc="esc_event"
            ref="debounce_search"
          >
            <template v-slot:prepend-inner>
              <v-icon color="primary">mdi-magnify</v-icon>
            </template>
          </v-text-field>
        </v-col>
        <v-col cols="2" class="pb-0 mb-2" v-if="pos_profile.posa_new_line">
          <v-checkbox
            v-model="new_line"
            color="accent"
            value="true"
            label="New Line"
            dense
            hide-details
          ></v-checkbox>
        </v-col>
        <v-col cols="12" class="pt-0 mt-0 d-flex flex-column flex-grow-1">
          <div class="items d-flex flex-column flex-grow-1" v-if="items_view == 'card'">
            <v-row dense class="items-scrollable">
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
                    <!-- Quantity at the top of the image from right to left -->
                    <v-card-text
                      v-if="item.actual_qty !== undefined"
                      class="text-caption px-1 pt-1 text-right"
                    >
                      <span :style="{color: item.actual_qty > 0 ? '#F44336' : '#4CAF50', fontWeight: 'bold'}">
                        Qty: {{ formatFloat(item.actual_qty) }}
                      </span>
                    </v-card-text>
                  </v-img>
                  
                  <!-- Item name in the middle -->
                  <v-card-text class="text--primary pa-1 text-center">
                    <div class="text-caption" style="font-weight: bold; margin-bottom: 4px;">
                      {{ item.item_name }}
                    </div>
                    
                    <!-- Price and unit on the same line -->
                    <div class="text-caption d-flex justify-space-between">
                      <span class="golden--text">
                        {{ item.stock_uom || "" }}
                      </span>
                      <span class="primary--text" style="font-weight: bold;">
                        {{ currencySymbol(item.currency) || "" }}{{ formatCurrency(item.rate) || 0 }}
                      </span>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </div>
          <div class="items d-flex flex-column flex-grow-1" v-if="items_view == 'list'">
            <div class="my-0 py-0 flex-grow-1 items-scrollable">
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
        </v-col>
      </v-row>
    </v-card>
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
    },
    customer(newVal, oldVal) {
      if (this._suppressCustomerWatcher) {
        console.log('[ItemsSelector.vue:watch customer] suppressed initial change');
        this._suppressCustomerWatcher = false;
        return;
      }
      if (oldVal !== undefined && newVal !== oldVal) {
        console.log('[ItemsSelector.vue:watch customer] changed', { oldVal, newVal });
        this.get_items();
      } else {
        console.log('[ItemsSelector.vue:watch customer] ignored', { oldVal, newVal });
      }
    },
    new_line() {
      evntBus.emit("set_new_line", this.new_line);
    }
  },

  // ===== SECTION 5: METHODS =====
  methods: {
    
    // ========================================
    // Barcode search functions (normal/private/weight)
    // ========================================
    // Automatic processing when placing barcode
    handle_barcode_input() {
      if (!this.barcode_search.trim()) return;
      
      
      // Send to backend and immediate clearing
      this.analyze_barcode_type(this.barcode_search.trim());
      this.barcode_search = "";
      const barcodeInput = document.querySelector('input[placeholder*="Barcode"]');
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
      const posa_enable_scale_barcode = this.pos_profile?.posa_enable_scale_barcode;
      const posa_scale_barcode_start = this.pos_profile?.posa_scale_barcode_start;
      const posa_scale_barcode_lenth = this.pos_profile?.posa_scale_barcode_lenth;
      
      // Check conditions
      if (posa_enable_scale_barcode === 1 && 
          posa_scale_barcode_start && 
          posa_scale_barcode_lenth && 
          barcode_value.startsWith(posa_scale_barcode_start) && 
          barcode_value.length === posa_scale_barcode_lenth) {
        
        
        // Search for barcode
        frappe.call({
          method: 'posawesome.posawesome.api.search_scale_barcode.search_scale_barcode',
          args: { pos_profile: this.pos_profile, barcode_value: barcode_value },
          callback: (response) => {
            if (response?.message?.item_code) {
              this.add_item_to_cart(response.message);
              evntBus.emit("show_mesage", { text: `Added ${response.message.item_name} to cart (weight)`, color: "success" });
            } else {
              evntBus.emit("show_mesage", { text: "Item not found with weight barcode", color: "error" });
            }
          }
        });
        return true;
      }
      return false;
    },
    
    // Private barcode processing (check + search)
    process_private_barcode(barcode_value) {
      const posa_enable_private_barcode = this.pos_profile?.posa_enable_private_barcode;
      const posa_private_barcode_lenth = this.pos_profile?.posa_private_barcode_lenth;
      const posa_private_item_code_length = this.pos_profile?.posa_private_item_code_length;
      
      // Check conditions
      if (posa_enable_private_barcode === 1 && 
          posa_private_barcode_lenth && 
          posa_private_item_code_length && 
          barcode_value.length === posa_private_barcode_lenth) {
        
        
        // Search for barcode
        frappe.call({
          method: 'posawesome.posawesome.api.search_private_barcode.search_private_barcode',
          args: { pos_profile: this.pos_profile, barcode_value: barcode_value },
          callback: (response) => {
            if (response?.message?.item_code) {
              this.add_item_to_cart(response.message);
              evntBus.emit("show_mesage", { text: `Added ${response.message.item_name} to cart (private)`, color: "success" });
            } else {
              evntBus.emit("show_mesage", { text: "Item not found with private barcode", color: "error" });
            }
          }
        });
        return true;
      }
      return false;
    },
    
    // Normal barcode processing (direct search)
    process_normal_barcode(barcode_value) {
      frappe.call({
        method: 'posawesome.posawesome.api.search_items_barcode.search_items_barcode',
        args: { pos_profile: this.pos_profile, barcode_value: barcode_value },
        callback: (response) => {
          if (response?.message?.item_code) {
            this.add_item_to_cart(response.message);
            evntBus.emit("show_mesage", { text: `Added ${response.message.item_name} to cart (normal)`, color: "success" });
          } else {
            evntBus.emit("show_mesage", { text: "Item not found with barcode", color: "error" });
          }
        }
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
      console.log('[ItemsSelector.vue:onItemGroupChange] group change', this.item_group);
      
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
        evntBus.emit('show_mesage', {
          text: 'POS Profile not specified',
          color: 'error'
        });
        return;
      }
      
      console.log('[ItemsSelector.vue:get_items] calling get_items API', {
        item_group: this.item_group,
        search: this.first_search,
        customer: this.customer
      });
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
        method: "posawesome.posawesome.api.get_items.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: gr,
          search_value: sr,
          customer: vm.customer,
        },
        callback: function (r) {
          console.log('[ItemsSelector.vue:get_items] response', r && r.message ? r.message.length : 0);
          if (r.message) {
            vm.items = (r.message || []).map(it => ({
              ...it,
              item_barcode: Array.isArray(it.item_barcode) ? it.item_barcode : [],
              serial_no_data: Array.isArray(it.serial_no_data) ? it.serial_no_data : [],
              batch_no_data: Array.isArray(it.batch_no_data) ? it.batch_no_data : []
            }));
            vm._buildItemsMap();
            evntBus.emit("set_all_items", vm.items);
            vm.loading = false;
            vm.search_loading = false;
          }
        },
      });
    },

    // Helper function to build items map for quick search
    _buildItemsMap() {
      this._itemsMap.clear();
      
      this.items.forEach(item => {
        // Add search by code
        this._itemsMap.set(item.item_code.toLowerCase(), item);
        
        // Add search by barcode
        if (item.item_barcode) {
          item.item_barcode.forEach(barcode => {
            this._itemsMap.set(barcode.barcode.toLowerCase(), item);
          });
        }
        
        // Add search by name
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
          method: "posawesome.posawesome.api.get_items.get_items_groups",
          args: {},
          callback: function (r) {
            console.log('[ItemsSelector.vue:get_items_groups] response', r && r.message ? r.message.length : 0);
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
        },
        {
          title: "Code",
          align: "start",
          sortable: true,
          key: "item_code",
        },
        { title: "Price", key: "rate", align: "start" },
        { title: "Available Quantity", value: "actual_qty", align: "start" },
        { title: "Unit", key: "stock_uom", align: "start" },
      ];
      
      if (!this.pos_profile.posa_display_item_code) {
        items_headers.splice(1, 1);
      }

      return items_headers;
    },

    // Improve function to add item
    add_item_table(event, item){
      item = { ...item.item };
      if (item.has_variants) {
        evntBus.emit("open_variants_model", item, this.items);
      } else {
    // Set quantity correctly always
    const currentQty = Number(this.qty);
    if (!item.qty || item.qty === 1) {
      item.qty = currentQty > 0 ? currentQty : 1;
    }
    // Make sure stock_qty is defined and numeric
    const convFactor = Number(item.conversion_factor || 1);
    item.stock_qty = Number(item.qty) * convFactor;
        evntBus.emit("add_item", item);
        this.qty = 1;
      }
    },

    add_item(item) {
      item = { ...item };
      if (item.has_variants) {
        evntBus.emit("open_variants_model", item, this.items);
      } else {
    // Set quantity correctly always
    const currentQty = Number(this.qty);
    if (!item.qty || item.qty === 1) {
      item.qty = currentQty > 0 ? currentQty : 1;
    } else {
      item.qty = Number(item.qty) || 1;
    }
    
    // Make sure stock_qty is defined and numeric
    const convFactor = Number(item.conversion_factor || 1);
    item.stock_qty = Number(item.qty) * convFactor;
    
    // Make sure price_list_rate is defined and numeric
    item.price_list_rate = Number(item.price_list_rate || item.rate || 0);
        
        evntBus.emit("add_item", item);
        this.qty = 1;
      }
    },

    // Improve search processing function
    enter_event() {
      let match = false;
      
      // Improve verification of search items existence
      if (!this.first_search || this.first_search.trim() === '') {
        // Don't show error if nothing entered in search
        return;
      }
      
      if (!this.filtred_items.length) {
        evntBus.emit('show_mesage', {
          text: 'No items found matching search',
          color: 'warning'
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

    // Live search function with 100ms debounce
    performLiveSearch(searchValue) {
      const vm = this;
      
      // Activate search progress bar
      this.search_loading = true;
      
      // If search is empty, reload all items
      if (!searchValue || searchValue.trim() === '') {
        console.log('[ItemsSelector.vue:performLiveSearch] empty search, calling get_items');
        this.get_items();
        return;
      }
      
      // Perform live search using get_items
      console.log('[ItemsSelector.vue:performLiveSearch] calling get_items with search', searchValue);
      frappe.call({
        method: "posawesome.posawesome.api.get_items.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: vm.item_group !== "ALL" ? vm.item_group.toLowerCase() : "",
          search_value: searchValue.trim(),
          customer: vm.customer,
        },
        callback: function (r) {
          // Stop search progress bar
          vm.search_loading = false;
          
          console.log('[ItemsSelector.vue:performLiveSearch] response', r && r.message ? r.message.length : 0);
          if (r.message) {
            vm.items = (r.message || []).map(it => ({
              ...it,
              item_barcode: Array.isArray(it.item_barcode) ? it.item_barcode : [],
              serial_no_data: Array.isArray(it.serial_no_data) ? it.serial_no_data : [],
              batch_no_data: Array.isArray(it.batch_no_data) ? it.batch_no_data : []
            }));
            vm._buildItemsMap();
            evntBus.emit("set_all_items", vm.items);
          }
        },
        error: function(err) {
          // Stop search progress bar
          vm.search_loading = false;
          
        }
      });
    },

    _performItemSearch() {
      const vm = this;
      
      // If search is empty, do nothing
      if (!vm.debounce_search || vm.debounce_search.trim() === '') {
        vm.items = vm.originalItems || [];
        return;
      }

      // Search by name/code/batch/serial using get_items
      console.log('[ItemsSelector.vue:_performItemSearch] calling get_items with debounce_search', vm.debounce_search);
      frappe.call({
        method: "posawesome.posawesome.api.get_items.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: "",
          search_value: vm.debounce_search.trim(),
          customer: vm.customer,
        },
        callback: function (r) {
          
          console.log('[ItemsSelector.vue:_performItemSearch] response', r && r.message ? r.message.length : 0);
          if (r.message && r.message.length > 0) {
            // Results found, display for selection
            vm.items = (r.message || []).map(it => ({
              ...it,
              item_barcode: Array.isArray(it.item_barcode) ? it.item_barcode : [],
              serial_no_data: Array.isArray(it.serial_no_data) ? it.serial_no_data : [],
              batch_no_data: Array.isArray(it.batch_no_data) ? it.batch_no_data : []
            }));
          } else {
            // No results
            vm.items = [];
            evntBus.emit("show_mesage", {
              text: "No results found for search",
              color: "warning",
            });
          }
        }
      });
    },

    _performSearch() {
      const vm = this;
      
      // If search is empty, do nothing
      if (!vm.debounce_search || vm.debounce_search.trim() === '') {
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
        console.log('[ItemsSelector.vue:update_items_details] skipped on initial load');
        return;
      }
      
      // Get item codes from the items to update
      const item_codes = items.map(item => item.item_code);
      
      frappe.call({
        method: "posawesome.posawesome.api.get_items.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: "",
          search_value: "", // Empty search to get all items
          customer: vm.customer,
        },
        callback: function (r) {
          console.log('[ItemsSelector.vue:update_items_details] response for refresh', r && r.message ? r.message.length : 0);
          if (r.message) {
            // Use Map for faster search
            const updatedItemsMap = new Map();
            (r.message || []).forEach(item => {
              const safeItem = {
                ...item,
                item_barcode: Array.isArray(item.item_barcode) ? item.item_barcode : [],
                serial_no_data: Array.isArray(item.serial_no_data) ? item.serial_no_data : [],
                batch_no_data: Array.isArray(item.batch_no_data) ? item.batch_no_data : []
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
        method: "posawesome.posawesome.api.get_items.get_items",
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
            
            evntBus.emit('show_mesage', {
              text: `Item found: ${found_item.item_name}`,
              color: 'success'
            });
          } else {
            // Item not found
            evntBus.emit('show_mesage', {
              text: `Item not found for barcode: ${barcode}`,
              color: 'error'
            });
            vm._resetSearch();
          }
        },
        error: function(err) {
          evntBus.emit('show_mesage', {
            text: 'Error searching for barcode',
            color: 'error'
          });
          vm._resetSearch();
        }
      });
    },

    // Improve word combinations generation function
    generateWordCombinations(inputString) {
      const words = inputString.split(" ");
      const combinations = [];
      
      function permute(arr, m = []) {
        if (arr.length === 0) {
          combinations.push(m.join(" "));
        } else {
          for (let i = 0; i < arr.length; i++) {
            const current = arr.slice();
            const next = current.splice(i, 1);
            permute(current.slice(), m.concat(next));
          }
        }
      }
      
      permute(words);
      return combinations;
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
      
      // Filter by search
      if (!this.search || this.search.length < 3) {
        if (this.pos_profile.posa_show_template_items && this.pos_profile.posa_hide_variants_items) {
          filtred_list = filtred_group_list
            .filter((item) => !item.variant_of)
            .slice(0, 50);
        } else {
          filtred_list = filtred_group_list.slice(0, 50);
        }
      } else if (this.search) {
        // Search in barcode first
        filtred_list = filtred_group_list.filter((item) => {
          return item.item_barcode.some(element => element.barcode === this.search);
        });
        
        // Search in code
        if (filtred_list.length === 0) {
          filtred_list = filtred_group_list.filter((item) =>
            item.item_code.toLowerCase().includes(this.search.toLowerCase())
          );
        }
        
        // Search in name
        if (filtred_list.length === 0) {
          const search_combinations = this.generateWordCombinations(this.search);
          filtred_list = filtred_group_list.filter((item) => {
            return search_combinations.some(element => {
              element = element.toLowerCase().trim();
              let element_regex = new RegExp(`.*${element.split("").join(".*")}.*`);
              return element_regex.test(item.item_name.toLowerCase());
            });
          });
        }
        
        // Search in serial numbers
        if (filtred_list.length === 0) {
          filtred_list = filtred_group_list.filter((item) => {
            return item.serial_no_data.some(element => {
              if (element.serial_no === this.search) {
                this.flags.serial_no = this.search;
                return true;
              }
              return false;
            });
          });
        }
        
        // Search in batch numbers
        if (filtred_list.length === 0) {
          filtred_list = filtred_group_list.filter((item) => {
            return item.batch_no_data.some(element => {
              if (element.batch_no === this.search) {
                this.flags.batch_no = this.search;
                return true;
              }
              return false;
            });
          });
        }
      }
      
      // Final filtering
      if (this.pos_profile.posa_show_template_items && this.pos_profile.posa_hide_variants_items) {
        filtred_list = filtred_list.filter((item) => !item.variant_of).slice(0, 50);
      } else {
        filtred_list = filtred_list.slice(0, 50);
      }
      
      return filtred_list;
    },

    debounce_search: {
      get() {
        return this.first_search;
      },
      set: _.debounce(function (newValue) {
        this.first_search = newValue;
        // Trigger live search after 100ms
        this.performLiveSearch(newValue);
      }, 100),
    },
  },

  created: function () {
    this.$nextTick(function () {});
    evntBus.on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile;
      // Set customer without triggering watcher for first time
      this._suppressCustomerWatcher = true;
      this.customer = this.pos_profile && this.pos_profile.customer ? this.pos_profile.customer : this.customer;
      console.log('[ItemsSelector.vue:register_pos_profile] init', { customer: this.customer });
      this.get_items();
      this.get_items_groups();
      this.items_view = this.pos_profile.posa_default_card_view ? "card" : "list";
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
  },

  // Add beforeDestroy to clean up memory
  beforeDestroy() {
    this._searchCache.clear();
    this._filteredItemsCache.clear();
    this._itemsMap.clear();
    if (this._searchDebounceTimer) {
      clearTimeout(this._searchDebounceTimer);
    }
  }
};
</script>

<style scoped>
.item-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.item-card .v-card__text {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.item-card .v-img {
  position: relative;
}

.item-card .v-img .v-card__text {
  position: absolute;
  top: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  margin: 4px;
  padding: 2px 6px !important;
}

/* Unify header controls height */
.header-control {
  min-height: 28px !important;
  font-size: 0.8rem !important;
}

/* Optimized styling for ItemsSelector - cashier screens */
.v-select {
  font-size: 0.8rem !important;
}

.v-select .v-field {
  min-height: 28px !important;
}

.v-select .v-field__input {
  padding: 6px 10px !important;
  font-size: 0.8rem !important;
}

.v-text-field {
  font-size: 0.8rem !important;
}

.v-text-field .v-field {
  min-height: 28px !important;
}

.v-text-field .v-field__input {
  padding: 6px 10px !important;
  font-size: 0.8rem !important;
}

.v-data-table {
  font-size: 0.8rem !important;
}

.v-data-table .v-data-table__wrapper table {
  font-size: 0.75rem !important;
}

/* Consistent table formatting matching Invoice */
.v-data-table .v-data-table__wrapper table th,
.v-data-table .v-data-table__wrapper table td {
  padding: 4px 6px !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  line-height: 1.2 !important;
  height: 32px !important;
}

.v-data-table .v-data-table__wrapper table th {
  font-weight: 600 !important;
  font-size: 0.8rem !important;
  background-color: #f5f5f5 !important;
  height: 28px !important;
}

/* Make ItemsSelector use full available space */
.items-scrollable {
  min-height: 60vh !important;
  height: auto !important;
}

.items-scrollable .v-data-table__wrapper {
  min-height: 60vh !important;
  height: auto !important;
}

/* Ensure proper spacing for card view */
.items-scrollable .v-row {
  min-height: 60vh !important;
  height: auto !important;
}

/* Make parent containers use full space */
.items {
  min-height: 60vh !important;
  height: auto !important;
}

.flex-grow-1 {
  flex-grow: 1 !important;
  min-height: 60vh !important;
}

/* Ensure card items take proper space */
.item-card {
  min-height: 120px !important;
  height: auto !important;
}

.item-card .v-card__text {
  min-height: 60px !important;
}

.v-row {
  margin: -2px !important;
}

.v-col {
  padding: 2px !important;
}

/* Smaller visuals on 1024x768 and below */
@media (max-width: 1280px) {
  .item-card .v-card__text {
    padding: 6px !important;
  }
  .item-card .v-card__text .text-caption {
    font-size: 11px !important;
  }
  .item-image {
    height: 80px !important;
  }
}

@media (max-width: 1024px) {
  .item-image {
    height: 70px !important;
  }
  .item-card .v-card__text .text-caption {
    font-size: 10px !important;
  }
}
</style>
