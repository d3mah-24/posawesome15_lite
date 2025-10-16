<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div>
    <v-autocomplete
      density="compact"
      variant="outlined"
      color="primary"
      :label="'Customer'"
      v-model="customer"
      :items="customers"
      item-title="customer_name"
      item-value="name"
      :filter="customFilter"
      :disabled="readonly"
      append-icon="mdi-plus"
      @click:append="new_customer"
      prepend-inner-icon="mdi-account-edit"
      @click:prepend-inner="edit_customer"
      @focus="load_all_customers"
      :style="{ backgroundColor: quick_return ? '#EF9A9A' : 'white' }"
    >
      <template v-slot:item="{ props, item }">
        <v-list-item v-bind="props">
          <v-list-item-title
            class="primary--text subtitle-1"
            v-html="item.customer_name"
          ></v-list-item-title>
          <v-list-item-subtitle
            v-if="item.customer_name != item.name"
            v-html="'Customer ID: ' + item.name"
          ></v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="item.tax_id"
            v-html="'Tax ID: ' + item.tax_id"
          ></v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="item.email_id"
            v-html="'Email: ' + item.email_id"
          ></v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="item.mobile_no"
            v-html="'Mobile: ' + item.mobile_no"
          ></v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="item.primary_address"
            v-html="'Primary Address: ' + item.primary_address"
          ></v-list-item-subtitle>
        </v-list-item>
      </template>
    </v-autocomplete>

    <div class="mb-2">
      <UpdateCustomer />
    </div>
  </div>
</template>

<script>
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// IMPORTS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { evntBus } from "../../bus";
import UpdateCustomer from "./UpdateCustomer.vue";

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// CONSTANTS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * API methods for customer operations
 */
const API_METHODS = {
  GET_CUSTOMER_NAMES: 'posawesome.posawesome.api.customer.customer_names.get_customer_names',
};

/**
 * Event names for bus communication
 */
const EVENT_NAMES = {
  // Emitted events
  UPDATE_CUSTOMER: 'update_customer',
  SHOW_MESSAGE: 'show_mesage',
  OPEN_UPDATE_CUSTOMER: 'open_update_customer',
  
  // Listened events
  TOGGLE_QUICK_RETURN: 'toggle_quick_return',
  REGISTER_POS_PROFILE: 'register_pos_profile',
  PAYMENTS_REGISTER_POS_PROFILE: 'payments_register_pos_profile',
  SET_CUSTOMER: 'set_customer',
  ADD_CUSTOMER_TO_LIST: 'add_customer_to_list',
  SET_CUSTOMER_READONLY: 'set_customer_readonly',
  SET_CUSTOMER_INFO_TO_EDIT: 'set_customer_info_to_edit',
  FETCH_CUSTOMER_DETAILS: 'fetch_customer_details',
  CUSTOMER_DROPDOWN_OPENED: 'customer_dropdown_opened',
};

/**
 * Error messages
 */
const ERROR_MESSAGES = {
  UNEXPECTED_ERROR: 'An unexpected error occurred while fetching customers',
  POS_PROFILE_NOT_LOADED: 'POS Profile not loaded',
  DEFAULT_CUSTOMER_NOT_DEFINED: 'Default customer not defined in POS Profile',
  FAILED_TO_FETCH: 'Failed to fetch customers',
  NEW_CUSTOMER_ERROR: 'Error opening new customer form',
  EDIT_CUSTOMER_ERROR: 'Error opening customer edit form',
  INITIALIZATION_ERROR: 'An error occurred during component initialization',
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// COMPONENT
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export default {
  name: 'Customer',
  
  components: {
    UpdateCustomer,
  },
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // DATA
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  data() {
    return {
      pos_profile: null,
      customers: [],
      customer: '',
      readonly: false,
      customer_info: {},
      quick_return: false,
    };
  },
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // COMPUTED
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  computed: {},
  
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // METHODS
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  methods: {
    /**
     * Initialize customer data
     * Loads default customer initially for performance
     */
    get_customer_names() {
      try {
        if (this.customers.length > 0) {
          return;
        }
        // Load only default customer initially for better performance
        this.load_default_customer();
      } catch (error) {
        this.showMessage(ERROR_MESSAGES.UNEXPECTED_ERROR, 'error');
      }
    },

    /**
     * Load default customer from POS profile
     * Sets initial customer without fetching all customers
     */
    load_default_customer() {
      if (!this.pos_profile) {
        this.showMessage(ERROR_MESSAGES.POS_PROFILE_NOT_LOADED, 'error');
        return;
      }

      const default_customer = this.pos_profile.pos_profile?.customer;
      if (default_customer) {
        this.customer = default_customer;
        evntBus.emit(EVENT_NAMES.UPDATE_CUSTOMER, default_customer);
      } else {
        this.showMessage(ERROR_MESSAGES.DEFAULT_CUSTOMER_NOT_DEFINED, 'error');
      }
    },

    /**
     * Load all customers from server
     * Called when dropdown is opened/focused
     */
    load_all_customers() {
      frappe.call({
        method: API_METHODS.GET_CUSTOMER_NAMES,
        args: {
          pos_profile: this.pos_profile.pos_profile,
        },
        callback: (r) => {
          if (r.message) {
            this.customers = r.message;
          }
        },
        error: (err) => {
          this.showMessage(ERROR_MESSAGES.FAILED_TO_FETCH, 'error');
        },
      });
    },

    /**
     * Open new customer dialog
     * Emits event to open UpdateCustomer component
     */
    new_customer() {
      try {
        evntBus.emit(EVENT_NAMES.OPEN_UPDATE_CUSTOMER, null);
      } catch (error) {
        this.showMessage(ERROR_MESSAGES.NEW_CUSTOMER_ERROR, 'error');
      }
    },

    /**
     * Open edit customer dialog
     * Emits event with current customer info
     */
    edit_customer() {
      try {
        evntBus.emit(EVENT_NAMES.OPEN_UPDATE_CUSTOMER, this.customer_info);
      } catch (error) {
        this.showMessage(ERROR_MESSAGES.EDIT_CUSTOMER_ERROR, 'error');
      }
    },

    /**
     * Custom filter for customer autocomplete
     * Searches across multiple fields: name, tax_id, email, mobile, customer_name
     * @param {Object} item - Customer item
     * @param {string} queryText - Search query
     * @param {string} itemText - Item text (not used)
     * @returns {boolean} True if match found
     */
    customFilter(item, queryText, itemText) {
      try {
        const searchText = queryText.toLowerCase();
        const fields = [
          item.customer_name,
          item.tax_id,
          item.email_id,
          item.mobile_no,
          item.name,
        ];

        return fields.some((field) =>
          field ? field.toLowerCase().indexOf(searchText) > -1 : false
        );
      } catch (error) {
        return false;
      }
    },

    /**
     * Show message to user via event bus
     * @param {string} message - Message text
     * @param {string} color - Message color (success, error, warning, info)
     */
    showMessage(message, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { message, color });
    },

    /**
     * Register event listeners
     * Sets up all event bus subscriptions
     */
    registerEventListeners() {
      try {
        evntBus.on(EVENT_NAMES.TOGGLE_QUICK_RETURN, this.handleToggleQuickReturn);
        evntBus.on(EVENT_NAMES.REGISTER_POS_PROFILE, this.handleRegisterPosProfile);
        evntBus.on(EVENT_NAMES.PAYMENTS_REGISTER_POS_PROFILE, this.handlePaymentsRegisterPosProfile);
        evntBus.on(EVENT_NAMES.SET_CUSTOMER, this.handleSetCustomer);
        evntBus.on(EVENT_NAMES.ADD_CUSTOMER_TO_LIST, this.handleAddCustomerToList);
        evntBus.on(EVENT_NAMES.SET_CUSTOMER_READONLY, this.handleSetCustomerReadonly);
        evntBus.on(EVENT_NAMES.SET_CUSTOMER_INFO_TO_EDIT, this.handleSetCustomerInfoToEdit);
        evntBus.on(EVENT_NAMES.FETCH_CUSTOMER_DETAILS, this.handleFetchCustomerDetails);
        evntBus.on(EVENT_NAMES.CUSTOMER_DROPDOWN_OPENED, this.handleCustomerDropdownOpened);
      } catch (error) {
        this.showMessage(ERROR_MESSAGES.INITIALIZATION_ERROR, 'error');
      }
    },

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EVENT HANDLERS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Handle quick return toggle
     * @param {boolean} value - Quick return state
     */
    handleToggleQuickReturn(value) {
      this.quick_return = value;
    },

    /**
     * Handle POS profile registration
     * @param {Object} pos_profile - POS profile data
     */
    handleRegisterPosProfile(pos_profile) {
      this.pos_profile = pos_profile;
      this.get_customer_names();
    },

    /**
     * Handle payments POS profile registration
     * @param {Object} pos_profile - POS profile data
     */
    handlePaymentsRegisterPosProfile(pos_profile) {
      this.pos_profile = pos_profile;
      this.get_customer_names();
    },

    /**
     * Handle set customer
     * @param {string} customer - Customer name
     */
    handleSetCustomer(customer) {
      this.customer = customer;
    },

    /**
     * Handle add customer to list
     * @param {Object} customer - Customer data
     */
    handleAddCustomerToList(customer) {
      this.customers.push(customer);
    },

    /**
     * Handle set customer readonly
     * @param {boolean} value - Readonly state
     */
    handleSetCustomerReadonly(value) {
      this.readonly = value;
    },

    /**
     * Handle set customer info to edit
     * @param {Object} data - Customer info
     */
    handleSetCustomerInfoToEdit(data) {
      this.customer_info = data;
    },

    /**
     * Handle fetch customer details
     */
    handleFetchCustomerDetails() {
      this.get_customer_names();
    },

    /**
     * Handle customer dropdown opened
     */
    handleCustomerDropdownOpened() {
      this.load_all_customers();
    },
  },

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // LIFECYCLE HOOKS
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  created() {
    this.$nextTick(() => {
      this.registerEventListeners();
    });
  },

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // WATCHERS
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  watch: {
    /**
     * Watch customer changes
     * Emits update_customer event when customer changes
     */
    customer() {
      evntBus.emit(EVENT_NAMES.UPDATE_CUSTOMER, this.customer);
    },
  },
};
</script>
