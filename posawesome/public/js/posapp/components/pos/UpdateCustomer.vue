<template>
  <div class="dialog-row">
    <div v-if="customerDialog" class="custom-modal-overlay" @click="clear_customer">
      <div class="custom-modal" @click.stop>
        <div class="customer-modal">
          <div class="modal-header">
            <i class="mdi mdi-account-circle header-icon"></i>
            <span class="modal-title">{{ customer_id ? 'Update Customer' : 'New Customer' }}</span>
            <button class="close-icon" @click="close_dialog">
              <i class="mdi mdi-close close-icon-element"></i>
            </button>
          </div>

          <div class="modal-body">
          <div class="field-group">
            <label class="field-label">Customer Name *</label>
            <input type="text" v-model="customer_name" class="custom-input" placeholder="Enter name" />
          </div>

          <div class="field-row">
            <div class="field-group half">
              <label class="field-label">Tax ID</label>
              <input type="text" v-model="tax_id" class="custom-input" placeholder="Tax ID" />
            </div>
            <div class="field-group half">
              <label class="field-label">Mobile</label>
              <input type="text" v-model="mobile_no" class="custom-input" placeholder="Mobile" />
            </div>
          </div>

          <div class="field-row">
            <div class="field-group half">
              <label class="field-label">Email</label>
              <input type="email" v-model="email_id" class="custom-input" placeholder="Email" />
            </div>
            <div class="field-group half">
              <label class="field-label">Gender</label>
              <select v-model="gender" class="custom-select">
                <option value="">Select</option>
                <option v-for="g in genders" :key="g" :value="g">{{ g }}</option>
              </select>
            </div>
          </div>

          <div class="field-row">
            <div class="field-group half">
              <label class="field-label">Referral Code</label>
              <input type="text" v-model="referral_code" class="custom-input" placeholder="Code" />
            </div>
            <div class="field-group half">
              <label class="field-label">Date of Birth</label>
              <input type="text" v-model="birthday" readonly @click="birthday_menu = true" class="custom-input"
                placeholder="DOB" />
              <div v-if="birthday_menu" class="custom-modal-overlay" @click="birthday_menu = false">
                <div class="custom-modal small-modal" @click.stop>
                  <div class="date-picker-container">
                    <input type="date" v-model="birthday" class="custom-date-input" :max="frappe.datetime.now_date()" @change="birthday_menu = false" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="field-row">
            <div class="field-group half">
              <label class="field-label">Customer Group *</label>
              <select v-model="group" class="custom-select" required>
                <option value="">Select</option>
                <option v-for="g in groups" :key="g" :value="g">{{ g }}</option>
              </select>
            </div>
            <div class="field-group half">
              <label class="field-label">Territory *</label>
              <select v-model="territory" class="custom-select" required>
                <option value="">Select</option>
                <option v-for="t in territorys" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
          </div>

          <div class="field-row" v-if="loyalty_program || loyalty_points">
            <div class="field-group half" v-if="loyalty_program">
              <label class="field-label">Loyalty Program</label>
              <input type="text" v-model="loyalty_program" readonly class="custom-input readonly" />
            </div>
            <div class="field-group half" v-if="loyalty_points">
              <label class="field-label">Points</label>
              <input type="text" v-model="loyalty_points" readonly class="custom-input readonly" />
            </div>
          </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="close_dialog">
            <i class="mdi mdi-close btn-icon"></i> Cancel
          </button>
          <button class="btn-submit" @click="submit_dialog">
            <i class="mdi mdi-check btn-icon"></i> {{ customer_id ? 'Update' : 'Register' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
import { API_MAP } from "../../api_mapper.js";

const EVENT_NAMES = {
  SHOW_MESSAGE: 'show_mesage',
  ADD_CUSTOMER_TO_LIST: 'add_customer_to_list',
  SET_CUSTOMER: 'set_customer',
  FETCH_CUSTOMER_DETAILS: 'fetch_customer_details',
  
  OPEN_UPDATE_CUSTOMER: 'open_update_customer',
  REGISTER_POS_PROFILE: 'register_pos_profile',
  PAYMENTS_REGISTER_POS_PROFILE: 'payments_register_pos_profile',
};

const VALIDATION_MESSAGES = {
  CUSTOMER_NAME_REQUIRED: 'Customer name is required.',
  CUSTOMER_GROUP_REQUIRED: 'Customer group name is required.',
  TERRITORY_REQUIRED: 'Territory name is required.',
};

const SUCCESS_MESSAGES = {
  CUSTOMER_CREATED: 'Customer created successfully.',
  CUSTOMER_UPDATED: 'Customer data updated successfully.',
};

const ERROR_MESSAGES = {
  FAILED_TO_CREATE: 'Failed to create customer.',
  FAILED_TO_LOAD_GROUPS: 'Error loading customer groups',
  FAILED_TO_LOAD_TERRITORIES: 'Error loading territories',
  FAILED_TO_LOAD_GENDERS: 'Error loading genders',
};

const CUSTOMER_TYPE = {
  INDIVIDUAL: 'Individual',
};

const DB_LIMITS = {
  CUSTOMER_GROUPS: 1000,
  TERRITORIES: 5000,
  GENDERS: 10,
};

const DEFAULT_VALUES = {
  CUSTOMER_GROUP: 'Individual',
  TERRITORY: 'Rest Of The World',
};

export default {
  name: 'UpdateCustomer',
  data() {
    return {
      customerDialog: false,
      pos_profile: null,
      customer_id: '',
      customer_name: '',
      tax_id: '',
      mobile_no: '',
      email_id: '',
      referral_code: '',
      birthday: null,
      birthday_menu: false,
      customer_type: CUSTOMER_TYPE.INDIVIDUAL,
      gender: '',
      loyalty_points: null,
      loyalty_program: null,
      group: '',
      groups: [],
      territory: '',
      territorys: [],
      genders: [],
    };
  },
  
  methods: {
    close_dialog() {
      this.customerDialog = false;
      this.clear_customer();
    },
    clear_customer() {
      this.customer_name = '';
      this.tax_id = '';
      this.mobile_no = '';
      this.email_id = '';
      this.referral_code = '';
      this.birthday = '';
      this.group = frappe.defaults.get_user_default('Customer Group');
      this.territory = frappe.defaults.get_user_default('Territory');
      this.customer_id = '';
      this.customer_type = CUSTOMER_TYPE.INDIVIDUAL;
      this.gender = '';
      this.loyalty_points = null;
      this.loyalty_program = null;
    },

    getCustomerGroups() {
      if (this.groups.length > 0) return;

      frappe.db
        .get_list('Customer Group', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: DB_LIMITS.CUSTOMER_GROUPS,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            this.groups = data.map((el) => el.name);
          }
        })
        .catch((err) => {
          this.showMessage(ERROR_MESSAGES.FAILED_TO_LOAD_GROUPS, 'error');
        });
    },

    getCustomerTerritorys() {
      if (this.territorys.length > 0) return;

      frappe.db
        .get_list('Territory', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: DB_LIMITS.TERRITORIES,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            this.territorys = data.map((el) => el.name);
          }
        })
        .catch((err) => {
          this.showMessage(ERROR_MESSAGES.FAILED_TO_LOAD_TERRITORIES, 'error');
        });
    },

    getGenders() {
      frappe.db
        .get_list('Gender', {
          fields: ['name'],
          page_length: DB_LIMITS.GENDERS,
        })
        .then((data) => {
          if (data.length > 0) {
            this.genders = data.map((el) => el.name);
          }
        })
        .catch((err) => {
          this.showMessage(ERROR_MESSAGES.FAILED_TO_LOAD_GENDERS, 'error');
        });
    },

    validateForm() {
      if (!this.customer_name) {
        this.showMessage(VALIDATION_MESSAGES.CUSTOMER_NAME_REQUIRED, 'error');
        return false;
      }
      if (!this.group) {
        this.showMessage(VALIDATION_MESSAGES.CUSTOMER_GROUP_REQUIRED, 'error');
        return false;
      }
      if (!this.territory) {
        this.showMessage(VALIDATION_MESSAGES.TERRITORY_REQUIRED, 'error');
        return false;
      }
      return true;
    },

    submit_dialog() {
      if (!this.validateForm()) {
        return;
      }

      const args = {
        customer_id: this.customer_id,
        customer_name: this.customer_name,
        company: this.pos_profile.company,
        tax_id: this.tax_id,
        mobile_no: this.mobile_no,
        email_id: this.email_id,
        referral_code: this.referral_code,
        birthday: this.birthday,
        customer_group: this.group,
        territory: this.territory,
        customer_type: this.customer_type,
        gender: this.gender,
        method: this.customer_id ? 'update' : 'create',
        pos_profile_doc: JSON.stringify(this.pos_profile),
      };

      frappe.call({
        method: this.customer_id ? API_MAP.CUSTOMER.UPDATE_CUSTOMER : API_MAP.CUSTOMER.POST_CUSTOMER,
        args: args,
        callback: (r) => {
          if (!r.exc && r.message.name) {
            this.handleCustomerSuccess(r.message.name, args);
          } else {
            this.handleCustomerError();
          }
        },
      });

      this.customerDialog = false;
    },

    handleCustomerSuccess(customerName, args) {
      const isUpdate = !!this.customer_id;
      const message = isUpdate 
        ? SUCCESS_MESSAGES.CUSTOMER_UPDATED 
        : SUCCESS_MESSAGES.CUSTOMER_CREATED;

      args.name = customerName;

      if (!isUpdate) {
        evntBus.emit(EVENT_NAMES.ADD_CUSTOMER_TO_LIST, args);
        evntBus.emit(EVENT_NAMES.SET_CUSTOMER, customerName);
        evntBus.emit(EVENT_NAMES.FETCH_CUSTOMER_DETAILS);
      }

      this.close_dialog();
    },

    handleCustomerError() {
      this.showMessage(ERROR_MESSAGES.FAILED_TO_CREATE, 'error');
    },

    showMessage(text, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { text, color });
    },

    populateCustomerData(data) {
      if (!data) return;

      this.customer_name = data.customer_name;
      this.customer_id = data.name;
      this.tax_id = data.tax_id;
      this.mobile_no = data.mobile_no;
      this.email_id = data.email_id;
      this.referral_code = data.referral_code;
      this.birthday = data.birthday;
      this.group = data.customer_group;
      this.territory = data.territory;
      this.loyalty_points = data.loyalty_points;
      this.loyalty_program = data.loyalty_program;
      this.gender = data.gender;
    },

    registerEventListeners() {
      evntBus.on(EVENT_NAMES.OPEN_UPDATE_CUSTOMER, this.handleOpenUpdateCustomer);
      evntBus.on(EVENT_NAMES.REGISTER_POS_PROFILE, this.handleRegisterPosProfile);
      evntBus.on(EVENT_NAMES.PAYMENTS_REGISTER_POS_PROFILE, this.handlePaymentsRegisterPosProfile);
    },

    handleOpenUpdateCustomer(data) {
      this.customerDialog = true;
      this.populateCustomerData(data);

      this.getCustomerGroups();
      this.getCustomerTerritorys();
      this.getGenders();
    },

    handleRegisterPosProfile(data) {
      this.pos_profile = data.pos_profile;
    },

    handlePaymentsRegisterPosProfile(data) {
      this.pos_profile = data.pos_profile;
    },
  },

  created() {
    this.registerEventListeners();
    
    this.group = frappe.defaults.get_user_default('Customer Group') || DEFAULT_VALUES.CUSTOMER_GROUP;
    this.territory = frappe.defaults.get_user_default('Territory') || DEFAULT_VALUES.TERRITORY;
  },

  beforeDestroy() {
    // Clean up all event listeners
    evntBus.$off(EVENT_NAMES.OPEN_UPDATE_CUSTOMER, this.handleOpenUpdateCustomer);
    evntBus.$off(EVENT_NAMES.REGISTER_POS_PROFILE, this.handleRegisterPosProfile);
    evntBus.$off(EVENT_NAMES.PAYMENTS_REGISTER_POS_PROFILE, this.handlePaymentsRegisterPosProfile);
  }
};
</script>

<style scoped>
.customer-modal {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

/* Dialog Row Container */
.dialog-row {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Header - very compact */
.modal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: white;
}

.header-icon {
  color: white;
  font-size: 16px;
}

.modal-title {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.close-icon {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 3px;
  padding: 2px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.close-icon:hover {
  background: rgba(255, 255, 255, 0.25);
}

.close-icon-element {
  color: white;
  font-size: 16px;
}

/* Body - minimal padding */
.modal-body {
  padding: 8px 10px;
}

/* Field groups - super compact */
.field-group {
  margin-bottom: 6px;
}

.field-group.half {
  flex: 1;
  min-width: 0;
}

.field-row {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
}

.field-label {
  display: block;
  font-size: 11px;
  color: #555;
  margin-bottom: 2px;
  font-weight: 500;
}

/* Custom inputs - beautiful and compact */
.custom-input,
.custom-select {
  width: 100%;
  padding: 5px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  color: #1f2937;
  background: #fff;
  transition: all 0.2s;
  outline: none;
  height: 28px;
}

.custom-input:focus,
.custom-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.custom-input::placeholder {
  color: #9ca3af;
  font-size: 11px;
}

.custom-input.readonly {
  background: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.custom-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 6px center;
  padding-right: 24px;
}

/* Footer - compact buttons */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  padding: 6px 10px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-submit {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  height: 26px;
}

.btn-cancel {
  background: white;
  border-color: #d1d5db;
  color: #374151;
}

.btn-cancel:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-submit {
  background: linear-gradient(135deg, #1976d2 0%, #1e88e5 100%);
  border-color: #1565c0;
  color: white;
}

.btn-submit:hover {
  background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);
  box-shadow: 0 2px 4px rgba(25, 118, 210, 0.2);
}

.btn-icon {
  font-size: 13px;
}

/* Date picker compact */
.v-picker {
  border-radius: 6px !important;
  font-size: 12px !important;
}

.v-date-picker-header {
  padding: 4px 8px !important;
}

/* ===== CUSTOM MODAL ===== */
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: modal-fade-in 0.2s ease;
}

.custom-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
  animation: modal-slide-in 0.3s ease;
}

.custom-modal.small-modal {
  max-width: 290px;
  padding: 16px;
}

.date-picker-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.custom-date-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  font-size: 0.9rem;
  outline: none;
}

.custom-date-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

@keyframes modal-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modal-slide-in {
  from {
    transform: translateY(-20px) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

/* Responsive modal */
@media (max-width: 600px) {
  .custom-modal {
    width: 95%;
    margin: 20px;
  }
  
  .custom-modal.small-modal {
    width: 90%;
    max-width: 280px;
  }
}
</style>
