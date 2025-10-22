<template>
  <div>
    <div 
      class="autocomplete" 
      :style="{ backgroundColor: quick_return ? '#EF9A9A' : 'white' }"
    >
      <div class="autocomplete-input-wrapper">
        <input
          type="text"
          class="autocomplete-input"
          :placeholder="'Customer'"
          v-model="customer_search"
          :disabled="readonly"
          @focus="handleCustomerFocus"
          @input="performSearch"
          @keydown.enter="handleEnter"
          @keydown.down="navigateDown"
          @keydown.up="navigateUp"
          @keydown.esc="showDropdown = false"
        />

        <div class="autocomplete-icons">
          <button 
            class="autocomplete-icon-btn" 
            @click="edit_customer"
            :disabled="readonly"
            title="Edit Customer"
          >
            <i class="mdi mdi-account-edit"></i>
          </button>
          <button 
            class="autocomplete-icon-btn" 
            @click="new_customer"
            :disabled="readonly"
            title="New Customer"
          >
            <i class="mdi mdi-plus"></i>
          </button>
        </div>
      </div>

      <!-- Dropdown -->
      <div 
        v-if="showDropdown && filteredCustomers.length > 0" 
        class="autocomplete-dropdown"
        role="listbox"
      >
        <div 
          v-for="(item, index) in filteredCustomers" 
          :key="item.name"
          class="autocomplete-item"
          :class="{ 'autocomplete-item--active': index === selectedIndex }"
          role="option"
          :aria-selected="index === selectedIndex"
          @click="selectCustomer(item)"
          @mouseenter="selectedIndex = index"
        >
          <div class="autocomplete-item-title">
            {{ item.customer_name }}
          </div>
          <div v-if="item.mobile_no" class="autocomplete-item-subtitle">
            {{ item.mobile_no }}
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="showDropdown && loading" class="autocomplete-loading">
        <div class="progress-linear">
          <div class="progress-bar"></div>
        </div>
      </div>
    </div>

    <div class="mb-2">
      <UpdateCustomer />
    </div>
  </div>
</template>

<script>
import { evntBus } from "../../bus";
import UpdateCustomer from "./UpdateCustomer.vue";
import { API_MAP } from "../../api_mapper.js";

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

  components: { UpdateCustomer },

  data() {
    return {
      pos_profile: null,
      customers: [],
      customer: '',
      readonly: false,
      customer_info: {},
      quick_return: false,
      searchTimeout: null,
      loading: false,
      customer_search: '',
      showDropdown: false,
      selectedIndex: -1,
      filteredCustomers: [],
      defaultLoaded: false, // ✅ New flag
    };
  },

  methods: {
    get_many_customers() {
      try {
        if (this.customers.length > 0) return;
        this.load_all_customers("");
        this.load_default_customer();
      } catch (error) {
        this.showMessage(ERROR_MESSAGES.UNEXPECTED_ERROR, 'error');
      }
    },

    handleCustomerFocus() {
      this.load_all_customers("");
      this.showDropdown = true;
    },

    load_default_customer() {
      if (!this.pos_profile) {
        this.showMessage(ERROR_MESSAGES.POS_PROFILE_NOT_LOADED, 'error');
        return;
      }

      const default_customer = this.pos_profile.pos_profile?.customer;
      if (default_customer) {
        this.customer = default_customer;

        // Wait for customers list to load, then match name
        const checkInterval = setInterval(() => {
          const selected = this.customers.find(c => c.name === default_customer);
          if (selected) {
            this.customer_search = selected.customer_name;
            this.customer_info = selected;
            this.defaultLoaded = true;
            clearInterval(checkInterval);
          }
        }, 300);

        evntBus.emit(EVENT_NAMES.UPDATE_CUSTOMER, default_customer);
      } else {
        this.showMessage(ERROR_MESSAGES.DEFAULT_CUSTOMER_NOT_DEFINED, 'error');
      }
    },

    load_all_customers(searchTerm = "") {
      if (!this.pos_profile) {
        this.showMessage(ERROR_MESSAGES.POS_PROFILE_NOT_LOADED, 'error');
        return;
      }

      const args = {
        pos_profile: this.pos_profile.pos_profile,
        limit: 100,
      };
      if (searchTerm.trim()) args.search_term = searchTerm.trim();

      this.loading = true;

      frappe.call({
        method: API_MAP.CUSTOMER.GET_MANY_CUSTOMERS,
        args,
        callback: (r) => {
          if (r.message) {
            this.customers = r.message;
            this.filteredCustomers = r.message;

            // ✅ After customers loaded, if default not yet shown, show it now
            if (!this.defaultLoaded && this.customer) {
              const selected = this.customers.find(c => c.name === this.customer);
              if (selected) {
                this.customer_search = selected.customer_name;
                this.customer_info = selected;
                this.defaultLoaded = true;
              }
            }
          }
          this.loading = false;
        },
        error: () => {
          this.showMessage(ERROR_MESSAGES.FAILED_TO_FETCH, 'error');
          this.loading = false;
        },
      });
    },

    performSearch(event) {
      const searchTerm = event?.target?.value || "";
      this.customer_search = searchTerm;
      this.showDropdown = true;
      this.selectedIndex = -1;

      if (this.searchTimeout) clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.load_all_customers(searchTerm);
      }, 300);
    },

    selectCustomer(customer) {
      this.customer = customer.name;
      this.customer_search = customer.customer_name;
      this.customer_info = customer;
      this.showDropdown = false;
      this.selectedIndex = -1;
      evntBus.emit(EVENT_NAMES.UPDATE_CUSTOMER, customer.name);
    },

    handleEnter() {
      if (!this.showDropdown) return;
      if (this.filteredCustomers.length > 0 && this.selectedIndex >= 0) {
        this.selectCustomer(this.filteredCustomers[this.selectedIndex]);
      } else if (this.filteredCustomers.length > 0) {
        this.selectCustomer(this.filteredCustomers[0]);
      }
    },

    navigateDown() {
      if (this.selectedIndex < this.filteredCustomers.length - 1) {
        this.selectedIndex++;
      }
    },

    navigateUp() {
      if (this.selectedIndex > 0) {
        this.selectedIndex--;
      }
    },

    new_customer() {
      try {
        evntBus.emit(EVENT_NAMES.OPEN_UPDATE_CUSTOMER, null);
      } catch {
        this.showMessage(ERROR_MESSAGES.NEW_CUSTOMER_ERROR, 'error');
      }
    },

    edit_customer() {
      try {
        evntBus.emit(EVENT_NAMES.OPEN_UPDATE_CUSTOMER, this.customer_info);
      } catch {
        this.showMessage(ERROR_MESSAGES.EDIT_CUSTOMER_ERROR, 'error');
      }
    },

    showMessage(message, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { message, color });
    },

    handleClickOutside(e) {
      const wrapper = this.$el.querySelector(".autocomplete");
      if (wrapper && !wrapper.contains(e.target)) {
        this.showDropdown = false;
      }
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
      } catch {
        this.showMessage(ERROR_MESSAGES.INITIALIZATION_ERROR, 'error');
      }
    },

    handleToggleQuickReturn(value) {
      this.quick_return = value;
    },
    handleRegisterPosProfile(pos_profile) {
      this.pos_profile = pos_profile;
      this.get_many_customers();
    },
    handlePaymentsRegisterPosProfile(pos_profile) {
      this.pos_profile = pos_profile;
      this.get_many_customers();
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
      this.get_many_customers();
    },
    handleCustomerDropdownOpened() {
      this.load_all_customers("");
    },
  },

  mounted() {
    document.addEventListener("click", this.handleClickOutside);
  },

  beforeUnmount() {
    if (this.searchTimeout) clearTimeout(this.searchTimeout);
    document.removeEventListener("click", this.handleClickOutside);
  },

  created() {
    this.$nextTick(() => {
      this.registerEventListeners();
    });
  },

  watch: {
    customer(newVal) {
      const selected = this.customers.find(c => c.name === newVal);
      if (selected) this.customer_search = selected.customer_name;
      evntBus.emit(EVENT_NAMES.UPDATE_CUSTOMER, newVal);
    },
  },
};
</script>

<style scoped>
.autocomplete {
  position: relative;
  width: 100%;
}

.autocomplete-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.autocomplete-input {
  width: 100%;
  padding: 8px 40px 8px 12px;
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-sm);
  font-size: 14px;
  background: white;
  transition: all 0.2s;
}

.autocomplete-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.autocomplete-input:disabled {
  background: var(--gray-100);
  color: var(--gray-500);
  cursor: not-allowed;
}

.autocomplete-icons {
  position: absolute;
  right: 4px;
  display: flex;
  gap: 4px;
}

.autocomplete-icon-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--gray-500);
  transition: color 0.15s;
}

.autocomplete-icon-btn:hover:not(:disabled) {
  color: var(--primary);
}

.autocomplete-icon-btn:disabled {
  color: var(--gray-300);
  cursor: not-allowed;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--gray-300);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  box-shadow: var(--shadow-md);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.autocomplete-item {
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.15s;
  border-bottom: 1px solid var(--gray-200);
}

.autocomplete-item:hover,
.autocomplete-item--active {
  background: var(--gray-50);
}

.autocomplete-item:last-child {
  border-bottom: none;
}

.autocomplete-item-title {
  font-weight: 500;
  color: var(--primary);
  font-size: 14px;
}

.autocomplete-item-subtitle {
  font-size: 12px;
  color: var(--gray-600);
  margin-top: 2px;
}

.autocomplete-loading {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--gray-300);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  padding: 8px;
}

.progress-linear {
  width: 100%;
  height: 4px;
  background: var(--gray-200);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary);
  border-radius: 2px;
  animation: progressIndeterminate 1.5s infinite linear;
}

@keyframes progressIndeterminate {
  0% { transform: translateX(0) scaleX(0); }
  40% { transform: translateX(0) scaleX(0.4); }
  100% { transform: translateX(100%) scaleX(0.5); }
}
</style>
