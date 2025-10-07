<template>
  <v-row justify="center">
    <v-dialog
      v-model="customerDialog"
      max-width="600px"
      @click:outside="clear_customer"
    >
      <v-card>
        <v-card-title>
          <span v-if="customer_id" class="headline primary--text">Update Customer Data</span>
          <span v-else class="headline primary--text">Register New Customer</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  dense
                  color="primary"
                  label="Customer Name *"
                  background-color="white"
                  hide-details
                  v-model="customer_name"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  label="Tax ID"
                  background-color="white"
                  hide-details
                  v-model="tax_id"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  label="Mobile Number"
                  background-color="white"
                  hide-details
                  v-model="mobile_no"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  label="Email"
                  background-color="white"
                  hide-details
                  v-model="email_id"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-select
                  dense
                  label="Gender"
                  :items="genders"
                  v-model="gender"
                ></v-select>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  label="Referral Code"
                  background-color="white"
                  hide-details
                  v-model="referral_code"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="birthday"
                  label="Date of Birth"
                  readonly
                  dense
                  clearable
                  hide-details
                  color="primary"
                  prepend-inner-icon="mdi-calendar"
                  @click="birthday_menu = true"
                ></v-text-field>
                
                <v-dialog
                  v-model="birthday_menu"
                  max-width="400px"
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
              <v-col cols="6">
                <v-autocomplete
                  clearable
                  dense
                  auto-select-first
                  color="primary"
                  label="Customer Group *"
                  v-model="group"
                  :items="groups"
                  background-color="white"
                  no-data-text="Group not found"
                  hide-details
                  required
                ></v-autocomplete>
              </v-col>
              <v-col cols="6">
                <v-autocomplete
                  clearable
                  dense
                  auto-select-first
                  color="primary"
                  label="Territory *"
                  v-model="territory"
                  :items="territorys"
                  background-color="white"
                  no-data-text="Territory not found"
                  hide-details
                  required
                ></v-autocomplete>
              </v-col>
              <v-col cols="6" v-if="loyalty_program">
                <v-text-field
                  v-model="loyalty_program"
                  label="Loyalty Program"
                  dense
                  readonly
                  hide-details
                ></v-text-field>
              </v-col>
              <v-col cols="6" v-if="loyalty_points">
                <v-text-field
                  v-model="loyalty_points"
                  label="Loyalty Points"
                  dense
                  readonly
                  hide-details
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <v-btn color="success" dark @click="submit_dialog">{{ customer_id ? 'Update Customer Data' : 'Register Customer' }}</v-btn>
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
      this.customer_type = 'Individual';
      this.gender = '';
      this.loyalty_points = null;
      this.loyalty_program = null;
    },
    getCustomerGroups() {
      if (this.groups.length > 0) return;
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
            data.forEach((el) => {
              vm.groups.push(el.name);
            });
          }
        })
        .catch((err) => {
          evntBus.emit('show_mesage', {
            text: 'Error loading customer groups',
            color: 'error',
          });
        });
    },
    getCustomerTerritorys() {
      if (this.territorys.length > 0) return;
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
            data.forEach((el) => {
              vm.territorys.push(el.name);
            });
          }
        })
        .catch((err) => {
          evntBus.emit('show_mesage', {
            text: 'Error loading territories',
            color: 'error',
          });
        });
    },
    getGenders() {
      const vm = this;
      frappe.db
        .get_list('Gender', {
          fields: ['name'],
          page_length: 10,
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => {
              vm.genders.push(el.name);
            });
          }
        })
        .catch((err) => {
          evntBus.emit('show_mesage', {
            text: 'Error loading genders',
            color: 'error',
          });
        });
    },
    submit_dialog() {
      // validate if all required fields are filled
      if (!this.customer_name) {
        evntBus.emit('show_mesage', {
          text: 'Customer name is required.',
          color: 'error',
        });
        return;
      }
      if (!this.group) {
        evntBus.emit('show_mesage', {
          text: 'Customer group name is required.',
          color: 'error',
        });
        return;
      }
      if (!this.territory) {
        evntBus.emit('show_mesage', {
          text: 'Territory name is required.',
          color: 'error',
        });
        return;
      }
      if (this.customer_name) {
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
              let text = 'Customer created successfully.';
              if (vm.customer_id) {
                text = 'Customer data updated successfully.';
              }
              args.name = r.message.name;
              frappe.utils.play_sound('submit');
              // Add customer to list only when creating
              if (!vm.customer_id) {
                evntBus.emit('add_customer_to_list', args);
              }
              // Don't send set_customer when updating to avoid rewriting customer name
              if (!vm.customer_id) {
                evntBus.emit('set_customer', r.message.name);
              }
              // Don't refetch customer list when updating to avoid duplication
              if (!vm.customer_id) {
                evntBus.emit('fetch_customer_details');
              }
              this.close_dialog();
            } else {
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
    evntBus.on('open_update_customer', (data) => {
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
    });
    evntBus.on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    evntBus.on('payments_register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    this.getCustomerGroups();
    this.getCustomerTerritorys();
    this.getGenders();
    // set default values for customer group and territory from user defaults
    this.group = frappe.defaults.get_user_default('Customer Group');
    this.territory = frappe.defaults.get_user_default('Territory');
  },
};
</script>
