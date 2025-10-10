<template>
  <v-row justify="center">
    <v-dialog
      v-model="customerDialog"
      max-width="480px"
      @click:outside="clear_customer"
    >
      <v-card class="compact-dialog">
        <v-card-title class="">
          <span v-if="customer_id" class="text-h6 p-0 primary--text font-weight-bold">Update Customer</span>
          <span v-else class="text-h6 p-0 primary--text font-weight-bold">New Customer</span>
        </v-card-title>
        <v-card-text class="pa-2">
          <v-container class="pa-2">
            <v-row dense>
              <v-col cols="12" class="pb-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  label="Customer Name *"
                  background-color="white"
                  hide-details="auto"
                  v-model="customer_name"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="6" class="pb-1 pr-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  label="Tax ID"
                  background-color="white"
                  hide-details="auto"
                  v-model="tax_id"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="6" class="pb-1 pl-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  label="Mobile"
                  background-color="white"
                  hide-details="auto"
                  v-model="mobile_no"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="6" class="pb-1 pr-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  label="Email"
                  background-color="white"
                  hide-details="auto"
                  v-model="email_id"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="6" class="pb-1 pl-1">
                <v-select
                  dense
                  outlined
                  label="Gender"
                  :items="genders"
                  v-model="gender"
                  hide-details="auto"
                  class="compact-field"
                ></v-select>
              </v-col>
              <v-col cols="6" class="pb-1 pr-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  label="Referral Code"
                  background-color="white"
                  hide-details="auto"
                  v-model="referral_code"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="6" class="pb-1 pl-1">
                <v-text-field
                  v-model="birthday"
                  label="Date of Birth"
                  readonly
                  dense
                  outlined
                  clearable
                  hide-details="auto"
                  color="primary"
                  prepend-inner-icon="mdi-calendar"
                  @click="birthday_menu = true"
                  class="compact-field"
                ></v-text-field>
                
                <v-dialog
                  v-model="birthday_menu"
                  max-width="320px"
                >
                  <v-date-picker
                    v-model="birthday"
                    color="primary"
                    scrollable
                    :max="frappe.datetime.now_date()"
                    @input="birthday_menu = false"
                  >
                  </v-date-picker>
                </v-dialog>
              </v-col>
              <v-col cols="6" class="pb-1 pr-1">
                <v-autocomplete
                  clearable
                  dense
                  outlined
                  auto-select-first
                  color="primary"
                  label="Customer Group *"
                  v-model="group"
                  :items="groups"
                  background-color="white"
                  no-data-text="Group not found"
                  hide-details="auto"
                  required
                  class="compact-field"
                ></v-autocomplete>
              </v-col>
              <v-col cols="6" class="pb-1 pl-1">
                <v-autocomplete
                  clearable
                  dense
                  outlined
                  auto-select-first
                  color="primary"
                  label="Territory *"
                  v-model="territory"
                  :items="territorys"
                  background-color="white"
                  no-data-text="Territory not found"
                  hide-details="auto"
                  required
                  class="compact-field"
                ></v-autocomplete>
              </v-col>
              <v-col cols="6" v-if="loyalty_program" class="pb-1 pr-1">
                <v-text-field
                  v-model="loyalty_program"
                  label="Loyalty Program"
                  dense
                  outlined
                  readonly
                  hide-details="auto"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="6" v-if="loyalty_points" class="pb-1" :class="loyalty_program ? 'pl-1' : 'pr-1'">
                <v-text-field
                  v-model="loyalty_points"
                  label="Loyalty Points"
                  dense
                  outlined
                  readonly
                  hide-details="auto"
                  class="compact-field"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions class="pa-3 pt-0">
          <v-spacer></v-spacer>
          <v-btn 
            outlined
            color="grey darken-1" 
            class="mr-2 compact-btn" 
            @click="close_dialog"
            small
          >
            Cancel
          </v-btn>
          <v-btn 
            color="primary" 
            class="compact-btn white--text" 
            @click="submit_dialog"
            small
            elevation="2"
          >
            {{ customer_id ? 'Update' : 'Register' }}
          </v-btn>
        </v-card-actions>
      </v-card>
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
          pos_profile_name: this.pos_profile.name,
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
.v-card-title{
  padding: .5rem 1rem 0 !important;
}
.compact-dialog {
  border-radius: 12px !important;
}

.compact-dialog .v-card__title {
  border-bottom: 1px solid #e0e0e0;
}

.compact-field {
  margin-bottom: 4px !important;
}

.compact-field .v-input__control {
  min-height: 40px !important;
}

.compact-field .v-text-field__details {
  margin-top: 2px !important;
  padding-top: 0 !important;
}

.compact-btn {
  text-transform: none !important;
  font-weight: 500 !important;
  letter-spacing: 0.5px !important;
  min-width: 80px !important;
  height: 36px !important;
}

.v-input--dense .v-input__control {
  min-height: 40px !important;
}

.v-text-field--outlined.v-input--dense .v-input__control {
  min-height: 40px !important;
}

.v-text-field--outlined .v-input__control {
  min-height: 40px !important;
}

/* Custom styling for better visual hierarchy */
.v-card__title .text-h6 {
  font-size: 1.1rem !important;
  line-height: 1.3 !important;
}

/* Reduce spacing in rows */
.row.dense {
  margin: -2px !important;
}

.row.dense > .col {
  padding: 2px !important;
}

/* Better button styling */
.v-btn.compact-btn {
  border-radius: 6px !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

.v-btn.compact-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
  transition: all 0.2s ease;
}

/* Outlined text fields styling */
.v-text-field--outlined > .v-input__control > .v-input__slot {
  border-radius: 6px !important;
}

.v-select--outlined > .v-input__control > .v-input__slot {
  border-radius: 6px !important;
}

/* Date picker dialog smaller */
.v-picker {
  border-radius: 8px !important;
}
</style>
