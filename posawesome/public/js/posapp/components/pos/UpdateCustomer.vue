<template>
  <v-row justify="center">
    <v-dialog v-model="customerDialog" max-width="400px" @click:outside="clear_customer">
      <div class="customer-modal">
        <!-- Compact Header -->
        <div class="modal-header">
          <v-icon size="16" color="white">mdi-account-circle</v-icon>
          <span class="modal-title">{{ customer_id ? 'Update Customer' : 'New Customer' }}</span>
          <button class="close-icon" @click="close_dialog">
            <v-icon size="16" color="white">mdi-close</v-icon>
          </button>
        </div>

        <!-- Compact Content with Custom Input Fields -->
        <div class="modal-body">
          <!-- Full width customer name -->
          <div class="field-group">
            <label class="field-label">Customer Name *</label>
            <input type="text" v-model="customer_name" class="custom-input" placeholder="Enter name" />
          </div>

          <!-- Two columns -->
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
              <v-dialog v-model="birthday_menu" max-width="290px">
                <v-date-picker v-model="birthday" color="primary" scrollable :max="frappe.datetime.now_date()"
                  @input="birthday_menu = false"></v-date-picker>
              </v-dialog>
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

        <!-- Compact Footer -->
        <div class="modal-footer">
          <button class="btn-cancel" @click="close_dialog">
            <v-icon size="13">mdi-close</v-icon> Cancel
          </button>
          <button class="btn-submit" @click="submit_dialog">
            <v-icon size="13">mdi-check</v-icon> {{ customer_id ? 'Update' : 'Register' }}
          </button>
        </div>
      </div>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    customerDialog: false,
    pos_profile: '',
    customer_id: '',
    customer_name: '',
    tax_id: '',
    mobile_no: '',
    email_id: '',
    referral_code: '',
    birthday: null,
    birthday_menu: false,
    group: '',
    groups: [],
    territory: '',
    territorys: [],
    genders: [],
    customer_type: 'Individual',
    gender: '',
    loyalty_points: null,
    loyalty_program: null,
  }),
  watch: {},
  methods: {
    close_dialog() {
      console.log('[UpdateCustomer] closing dialog');
      this.customerDialog = false;
      this.clear_customer();
    },
    clear_customer() {
      console.log('[UpdateCustomer] clearing customer data');
      this.customer_name = '';
      this.tax_id = '';
      this.mobile_no = '';
      this.email_id = '';
      this.referral_code = '';
      this.birthday = '';
      this.group = frappe.defaults.get_user_default('Customer Group');
      this.territory = frappe.defaults.get_user_default('Territory');
      this.customer_id = '';
      this.customer_type = 'Individual';
      this.gender = '';
      this.loyalty_points = null;
      this.loyalty_program = null;
    },
    getCustomerGroups() {
      if (this.groups.length > 0) return;
      console.log('[UpdateCustomer] loading customer groups');
      const vm = this;
      frappe.db
        .get_list('Customer Group', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: 1000,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            console.log('[UpdateCustomer] customer groups loaded', data.length);
            data.forEach((el) => {
              vm.groups.push(el.name);
            });
          }
        })
        .catch((err) => {
          console.log('[UpdateCustomer] error loading customer groups', err);
          evntBus.emit('show_mesage', {
            text: 'Error loading customer groups',
            color: 'error',
          });
        });
    },
    getCustomerTerritorys() {
      if (this.territorys.length > 0) return;
      console.log('[UpdateCustomer] loading territories');
      const vm = this;
      frappe.db
        .get_list('Territory', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: 5000,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            console.log('[UpdateCustomer] territories loaded', data.length);
            data.forEach((el) => {
              vm.territorys.push(el.name);
            });
          }
        })
        .catch((err) => {
          console.log('[UpdateCustomer] error loading territories', err);
          evntBus.emit('show_mesage', {
            text: 'Error loading territories',
            color: 'error',
          });
        });
    },
    getGenders() {
      console.log('[UpdateCustomer] loading genders');
      const vm = this;
      frappe.db
        .get_list('Gender', {
          fields: ['name'],
          page_length: 10,
        })
        .then((data) => {
          if (data.length > 0) {
            console.log('[UpdateCustomer] genders loaded', data.length);
            data.forEach((el) => {
              vm.genders.push(el.name);
            });
          }
        })
        .catch((err) => {
          console.log('[UpdateCustomer] error loading genders', err);
          evntBus.emit('show_mesage', {
            text: 'Error loading genders',
            color: 'error',
          });
        });
    },
    submit_dialog() {
      console.log('[UpdateCustomer] submitting dialog', this.customer_name);
      // validate if all required fields are filled
      if (!this.customer_name) {
        console.log('[UpdateCustomer] customer name missing');
        evntBus.emit('show_mesage', {
          text: 'Customer name is required.',
          color: 'error',
        });
        return;
      }
      if (!this.group) {
        console.log('[UpdateCustomer] customer group missing');
        evntBus.emit('show_mesage', {
          text: 'Customer group name is required.',
          color: 'error',
        });
        return;
      }
      if (!this.territory) {
        console.log('[UpdateCustomer] territory missing');
        evntBus.emit('show_mesage', {
          text: 'Territory name is required.',
          color: 'error',
        });
        return;
      }
      if (this.customer_name) {
        console.log('[UpdateCustomer] creating customer');
        const vm = this;
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
          method: 'posawesome.posawesome.api.customer.create_customer',
          args: args,
          callback: (r) => {
            if (!r.exc && r.message.name) {
              console.log('[UpdateCustomer] customer created/updated', r.message.name);
              let text = 'Customer created successfully.';
              if (vm.customer_id) {
                text = 'Customer data updated successfully.';
              }
              args.name = r.message.name;
              frappe.utils.play_sound('submit');
              // Add customer to list only when creating
              if (!vm.customer_id) {
                console.log('[UpdateCustomer] adding customer to list');
                evntBus.emit('add_customer_to_list', args);
              }
              // Don't send set_customer when updating to avoid rewriting customer name
              if (!vm.customer_id) {
                console.log('[UpdateCustomer] setting customer');
                evntBus.emit('set_customer', r.message.name);
              }
              // Don't refetch customer list when updating to avoid duplication
              if (!vm.customer_id) {
                console.log('[UpdateCustomer] fetching customer details');
                evntBus.emit('fetch_customer_details');
              }
              this.close_dialog();
            } else {
              console.log('[UpdateCustomer] failed to create customer');
              frappe.utils.play_sound('error');
              evntBus.emit('show_mesage', {
                text: 'Failed to create customer.',
                color: 'error',
              });
            }
          },
        });
        this.customerDialog = false;
      }
    },
  },
  created: function () {
    console.log('[UpdateCustomer] component created');
    evntBus.on('open_update_customer', (data) => {
      console.log('[UpdateCustomer] opening update customer dialog', data?.name);
      this.customerDialog = true;
      if (data) {
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
      }

      // Load data only when dialog is opened
      console.log('[UpdateCustomer] loading data for dialog');
      this.getCustomerGroups();
      this.getCustomerTerritorys();
      this.getGenders();
    });
    evntBus.on('register_pos_profile', (data) => {
      console.log('[UpdateCustomer] pos profile registered');
      this.pos_profile = data.pos_profile;
    });
    evntBus.on('payments_register_pos_profile', (data) => {
      console.log('[UpdateCustomer] payments pos profile registered');
      this.pos_profile = data.pos_profile;
    });
    // set default values for customer group and territory from user defaults
    this.group = frappe.defaults.get_user_default('Customer Group');
    this.territory = frappe.defaults.get_user_default('Territory');
  },
};
</script>

<style scoped>
/* Ultra-compact beautiful modal */
.customer-modal {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
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

/* Date picker compact */
.v-picker {
  border-radius: 6px !important;
  font-size: 12px !important;
}

.v-date-picker-header {
  padding: 4px 8px !important;
}
</style>
