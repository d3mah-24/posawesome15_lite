<template>
  <v-row justify="center">
    <v-dialog v-model="addressDialog" max-width="480px">
      <v-card class="compact-dialog">
        <v-card-title class="py-3 px-4">
          <span class="text-h6 primary--text font-weight-bold">Add New Address</span>
        </v-card-title>
        <v-card-text class="pa-2">
          <v-container class="pa-2">
            <v-row dense>
              <v-col cols="12" class="pb-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  label="Address Title"
                  background-color="white"
                  hide-details="auto"
                  v-model="address.name"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="12" class="pb-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  label="Address Line 1"
                  background-color="white"
                  hide-details="auto"
                  v-model="address.address_line1"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="12" class="pb-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  label="Address Line 2"
                  background-color="white"
                  hide-details="auto"
                  v-model="address.address_line2"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="6" class="pb-1 pr-1">
                <v-text-field
                  label="City"
                  dense
                  outlined
                  color="primary"
                  background-color="white"
                  hide-details="auto"
                  v-model="address.city"
                  class="compact-field"
                ></v-text-field>
              </v-col>
              <v-col cols="6" class="pb-1 pl-1">
                <v-text-field
                  label="State"
                  dense
                  outlined
                  color="primary"
                  background-color="white"
                  hide-details="auto"
                  v-model="address.state"
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
            Confirm
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
    addressDialog: false,
    address: {},
    customer: '',
  }),

  methods: {
    close_dialog() {
      this.addressDialog = false;
    },

    submit_dialog() {
      const vm = this;
      this.address.customer = this.customer;
      this.address.doctype = 'Customer';
      frappe.call({
        method: 'posawesome.posawesome.api.customer.get_customer_addresses.create_customer_address',
        args: {
          args: this.address,
        },
        callback: (r) => {
          if (!r.exc) {
            evntBus.emit('add_the_new_address', r.message);
            evntBus.emit('show_mesage', {
              text: 'Customer address created successfully.',
              color: 'success',
            });
            vm.addressDialog = false;
            vm.customer = '';
            vm.address = {};
          }
        },
      });
    },
  },
  created: function () {
    evntBus.on('open_new_address', (data) => {
      this.addressDialog = true;
      this.customer = data;
    });
  },
};
</script>

<style scoped>
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
</style>
