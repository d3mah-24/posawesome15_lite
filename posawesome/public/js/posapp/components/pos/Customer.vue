<template>
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
import { evntBus } from "../../bus";
import UpdateCustomer from "./UpdateCustomer.vue";

const API_METHODS = {
  GET_CUSTOMER_NAMES: 'posawesome.posawesome.api.customer.customer_names.get_customer_names',
};

const EVENT_NAMES = {
  UPDATE_CUSTOMER: 'update_customer',
  SHOW_MESSAGE: 'show_mesage',
  OPEN_UPDATE_CUSTOMER: 'open_update_customer',
  
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

const ERROR_MESSAGES = {
  UNEXPECTED_ERROR: 'An unexpected error occurred while fetching customers',
  POS_PROFILE_NOT_LOADED: 'POS Profile not loaded',
  DEFAULT_CUSTOMER_NOT_DEFINED: 'Default customer not defined in POS Profile',
  FAILED_TO_FETCH: 'Failed to fetch customers',
  NEW_CUSTOMER_ERROR: 'Error opening new customer form',
  EDIT_CUSTOMER_ERROR: 'Error opening customer edit form',
  INITIALIZATION_ERROR: 'An error occurred during component initialization',
};

export default {
  name: 'Customer',
  
  components: {
    UpdateCustomer,
  },
  
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

  
  methods: {
    get_customer_names() {
      try {
        if (this.customers.length > 0) {
          return;
        }
        this.load_default_customer();
      } catch (error) {
        this.showMessage(ERROR_MESSAGES.UNEXPECTED_ERROR, 'error');
      }
    },

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

    new_customer() {
      try {
        evntBus.emit(EVENT_NAMES.OPEN_UPDATE_CUSTOMER, null);
      } catch (error) {
        this.showMessage(ERROR_MESSAGES.NEW_CUSTOMER_ERROR, 'error');
      }
    },

    edit_customer() {
      try {
        evntBus.emit(EVENT_NAMES.OPEN_UPDATE_CUSTOMER, this.customer_info);
      } catch (error) {
        this.showMessage(ERROR_MESSAGES.EDIT_CUSTOMER_ERROR, 'error');
      }
    },

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

    showMessage(message, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { message, color });
    },

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

    handleToggleQuickReturn(value) {
      this.quick_return = value;
    },

    handleRegisterPosProfile(pos_profile) {
      this.pos_profile = pos_profile;
      this.get_customer_names();
    },

    handlePaymentsRegisterPosProfile(pos_profile) {
      this.pos_profile = pos_profile;
      this.get_customer_names();
    },

    handleSetCustomer(customer) {
      this.customer = customer;
    },

    handleAddCustomerToList(customer) {
      this.customers.push(customer);
    },

    handleSetCustomerReadonly(value) {
      this.readonly = value;
    },

    handleSetCustomerInfoToEdit(data) {
      this.customer_info = data;
    },

    handleFetchCustomerDetails() {
      this.get_customer_names();
    },

    handleCustomerDropdownOpened() {
      this.load_all_customers();
    },
  },

  created() {
    this.$nextTick(() => {
      this.registerEventListeners();
    });
  },

  watch: {
    customer() {
      evntBus.emit(EVENT_NAMES.UPDATE_CUSTOMER, this.customer);
    },
  },
};
</script>
