<template>
  <div class="dialog-row">
    <v-dialog v-model="addressDialog" max-width="480px">
      <div class="card compact-dialog">
        <div class="card-header">
          <span class="card-title">Add New Address</span>
        </div>
        <div class="card-body">
          <div class="form-container">
            <div class="form-row">
              <div class="form-col form-col-12">
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
              </div>
              <div class="form-col form-col-12">
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
              </div>
              <div class="form-col form-col-12">
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
              </div>
              <div class="form-col form-col-6">
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
              </div>
              <div class="form-col form-col-6">
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
              </div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <div class="spacer"></div>
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
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
import { API_MAP } from "../../api_mapper.js";
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
        method: API_MAP.CUSTOMER.CREATE_CUSTOMER_ADDRESS,
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

  beforeDestroy() {
    // Clean up event listener
    evntBus.$off('open_new_address');
  }
};
</script>

<style scoped>
/* Dialog Row Container */
.dialog-row {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Card Components */
.card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1976d2;
}

.card-body {
  padding: 8px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px 0;
  border-top: 1px solid #e0e0e0;
}

/* Spacer */
.spacer {
  flex: 1;
}

/* Form Container */
.form-container {
  padding: 8px;
}

/* Form Row */
.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: -4px;
}

/* Form Columns */
.form-col {
  padding: 4px;
}

.form-col-12 {
  flex: 0 0 100%;
  max-width: 100%;
}

.form-col-6 {
  flex: 0 0 calc(50% - 4px);
  max-width: calc(50% - 4px);
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
</style>
