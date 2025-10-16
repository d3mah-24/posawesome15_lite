<template>
  <v-row justify="center">
    <v-dialog v-model="isOpen" persistent max-width="420px" overlay-opacity="0.7">
      <!-- Custom Beautiful Dialog -->
      <div class="beautiful-dialog">
        <!-- Compact Header -->
        <div class="dialog-header">
          <div class="header-content">
            <div class="header-icon">
              <v-icon color="white" size="18">mdi-cash-register</v-icon>
            </div>
            <div class="header-text">
              <h3 class="dialog-title">POS Opening</h3>
            </div>
          </div>
          <button class="close-btn" @click="go_desk">
            <v-icon color="white" size="14">mdi-close</v-icon>
          </button>
        </div>

        <!-- Compact Content -->
        <div class="dialog-content">
          <!-- Company Selection -->
          <div class="form-section">
            <label class="field-label">Company</label>
            <select v-model="company" class="custom-select" required>
              <option v-for="comp in companies" :key="comp" :value="comp">{{ comp }}</option>
            </select>
          </div>

          <!-- POS Profile Selection -->
          <div class="form-section">
            <label class="field-label">POS Profile</label>
            <select v-model="pos_profile" class="custom-select" required>
              <option v-for="profile in pos_profiles" :key="profile" :value="profile">{{ profile }}</option>
            </select>
          </div>

          <!-- Payment Methods Table -->
          <div class="form-section">
            <label class="field-label">Payment Methods</label>
            <div class="payment-table">
              <div class="table-header">
                <div class="header-cell method-col">Payment Method</div>
                <div class="header-cell amount-col">Opening Amount</div>
              </div>
              
              <div class="table-body">
                <div 
                  v-for="(item, index) in payments_methods" 
                  :key="item.mode_of_payment"
                  class="table-row"
                >
                  <div class="table-cell method-col">
                    <div class="payment-method">
                      <v-icon :color="getPaymentIcon(item.mode_of_payment).color" size="14">
                        {{ getPaymentIcon(item.mode_of_payment).icon }}
                      </v-icon>
                      <span class="method-name">{{ item.mode_of_payment }}</span>
                    </div>
                  </div>
                  
                  <div class="table-cell amount-col">
                    <div class="amount-input-wrapper">
                      <span class="currency">{{ currencySymbol(item.currency) }}</span>
                      <input 
                        v-model="item.amount"
                        type="number"
                        class="amount-input"
                        placeholder="0.00"
                        step="0.01"
                        min="0"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Compact Footer -->
        <div class="dialog-footer">
          <button class="action-btn cancel-btn" @click="go_desk">
            <v-icon size="14">mdi-close</v-icon>
            Cancel
          </button>
          <button 
            class="action-btn submit-btn" 
            @click="submit_dialog"
            :disabled="is_loading"
            :class="{ 'loading': is_loading }"
          >
            <v-icon size="14" v-if="!is_loading">mdi-check</v-icon>
            <v-icon size="14" v-else class="rotating">mdi-loading</v-icon>
            {{ is_loading ? 'Creating...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </v-dialog>
  </v-row>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { evntBus } from '../../bus';
import format from '../../format';

export default {
  mixins: [format],
  props: ['dialog'],
  setup(props) {
    const isOpen = ref(props.dialog ? props.dialog : false);
    const dialog_data = ref({});
    const is_loading = ref(false);
    const companies = ref([]);
    const company = ref('');
    const pos_profiles_data = ref([]);
    const pos_profiles = ref([]);
    const pos_profile = ref('');
    const payments_method_data = ref([]);
    const payments_methods = ref([]);
    const payments_methods_headers = ref([
      {
        title: 'Payment Method',
        align: 'start',
        sortable: false,
        key: 'mode_of_payment',
      },
      {
        title: 'Opening Amount',
        key: 'amount',
        align: 'center',
        sortable: false,
      },
    ]);
    const itemsPerPage = ref(100);
    const max25chars = (v) => v.length <= 12 || 'Text too long!';

    const close_opening_dialog = () => {
      evntBus.emit('close_opening_dialog');
    };

    const get_opening_dialog_data = () => {
        frappe.call({
          method: 'posawesome.posawesome.api.pos_profile.get_opening_dialog_data.get_opening_dialog_data',
          args: {},
        callback: function (r) {
          if (r.message) {
            r.message.companies.forEach((element) => {
              companies.value.push(element.name);
            });
            company.value = companies.value[0];
            pos_profiles_data.value = r.message.pos_profiles_data;
            payments_method_data.value = r.message.payments_method;
          } else {
            evntBus.emit('show_mesage', {
              text: 'Failed to load POS opening data',
              color: 'error'
            });
          }
        },
      });
    };

    const submit_dialog = () => {
      if (!payments_methods.value.length || !company.value || !pos_profile.value) {
        evntBus.emit('show_mesage', {
          text: 'Please fill all required fields',
          color: 'error'
        });
        return;
      }
      is_loading.value = true;
      frappe
        .call('posawesome.posawesome.api.pos_opening_shift.create_opening_voucher.create_opening_voucher', {
          pos_profile: pos_profile.value,
          company: company.value,
          balance_details: payments_methods.value,
        })
        .then((r) => {
          if (r.message) {
            evntBus.emit('register_pos_data', r.message);
            evntBus.emit('set_company', r.message.company);
            evntBus.emit('show_mesage', {
              text: `POS Opening Shift ${r.message.pos_opening_shift.name} Created`,
              color: 'success'
            });
            close_opening_dialog();
            is_loading.value = false;
          } else {
            evntBus.emit('show_mesage', {
              text: 'Failed to create opening document',
              color: 'error'
            });
          }
        });
    };

    const go_desk = () => {
      frappe.set_route('/');
      location.reload();
    };

    // Helper method for payment icons (same as ClosingDialog)
    const getPaymentIcon = (paymentMethod) => {
      const icons = {
        'Cash': { icon: 'mdi-cash', color: '#4CAF50' },
        'Card': { icon: 'mdi-credit-card', color: '#2196F3' },
        'Credit Card': { icon: 'mdi-credit-card', color: '#2196F3' },
        'Debit Card': { icon: 'mdi-credit-card-outline', color: '#FF9800' },
        'Bank Transfer': { icon: 'mdi-bank-transfer', color: '#9C27B0' },
        'Mobile Payment': { icon: 'mdi-cellphone', color: '#E91E63' },
        'Digital Wallet': { icon: 'mdi-wallet', color: '#00BCD4' },
        'Check': { icon: 'mdi-checkbook', color: '#795548' },
        'Voucher': { icon: 'mdi-ticket', color: '#FF5722' },
      };
      
      // Find matching payment method or use default
      const method = Object.keys(icons).find(key => 
        paymentMethod.toLowerCase().includes(key.toLowerCase())
      );
      
      return method ? icons[method] : { icon: 'mdi-currency-usd', color: '#607D8B' };
    };

    watch(company, (val) => {
      pos_profiles.value = [];
      pos_profiles_data.value.forEach((element) => {
        if (element.company === val) {
          pos_profiles.value.push(element.name);
        }
      });
      pos_profile.value = pos_profiles.value.length ? pos_profiles.value[0] : '';
    });

    watch(pos_profile, (val) => {
      payments_methods.value = [];
      payments_method_data.value.forEach((element) => {
        if (element.parent === val) {
          payments_methods.value.push({
            mode_of_payment: element.mode_of_payment,
            amount: 0,
            currency: element.currency,
          });
        }
      });
    });

    onMounted(() => {
      get_opening_dialog_data();
    });

    return {
      isOpen,
      dialog_data,
      is_loading,
      companies,
      company,
      pos_profiles_data,
      pos_profiles,
      pos_profile,
      payments_method_data,
      payments_methods,
      payments_methods_headers,
      itemsPerPage,
      max25chars,
      close_opening_dialog,
      submit_dialog,
      go_desk,
      getPaymentIcon,
    };
  },
};
</script>

<style scoped>
/* Compact Beautiful Dialog */
.beautiful-dialog {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  max-width: 420px;
  width: 100%;
  animation: dialogSlideIn 0.3s ease-out;
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Compact Header */
.dialog-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.close-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* Compact Content */
.dialog-content {
  padding: 12px;
  background: #fafbfc;
}

/* Form Sections */
.form-section {
  margin-bottom: 12px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Custom Select */
.custom-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  background: white;
  color: #374151;
  outline: none;
  transition: all 0.2s ease;
}

.custom-select:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

/* Compact Table */
.payment-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8eaed;
  margin-top: 6px;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.header-cell {
  padding: 6px 8px;
  font-size: 10px;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.header-cell.amount-col {
  justify-content: flex-end;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.1s ease;
}

.table-row:hover {
  background: #f8fafc;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 8px;
  display: flex;
  align-items: center;
  font-size: 12px;
  min-height: 36px;
}

.table-cell.method-col {
  justify-content: flex-start;
}

.table-cell.amount-col {
  justify-content: flex-end;
}

/* Payment Method Styling */
.payment-method {
  display: flex;
  align-items: center;
  gap: 6px;
}

.method-name {
  font-weight: 500;
  color: #334155;
  font-size: 11px;
}

/* Amount Input Styling */
.amount-input-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 2px 6px;
  transition: all 0.2s ease;
}

.amount-input-wrapper:focus-within {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.currency {
  font-size: 10px;
  color: #64748b;
  font-weight: 500;
}

.amount-input {
  border: none;
  outline: none;
  font-size: 11px;
  font-weight: 600;
  font-family: monospace;
  width: 60px;
  text-align: right;
  background: transparent;
  color: #1e293b;
}

.amount-input::placeholder {
  color: #9ca3af;
}

/* Compact Footer */
.dialog-footer {
  background: #f8fafc;
  padding: 8px 12px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.cancel-btn:hover:not(:disabled) {
  background: #e2e8f0;
}

.submit-btn {
  background: #10b981;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
}

.submit-btn.loading {
  background: #6b7280;
}

/* Loading Animation */
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.rotating {
  animation: rotate 1s linear infinite;
}

/* Mobile Responsive */
@media (max-width: 600px) {
  .beautiful-dialog {
    margin: 8px;
    max-width: calc(100vw - 16px);
  }
  
  .dialog-header {
    padding: 8px 10px;
  }
  
  .dialog-title {
    font-size: 13px;
  }
  
  .dialog-content {
    padding: 10px;
  }
  
  .form-section {
    margin-bottom: 10px;
  }
  
  .table-header,
  .table-row {
    font-size: 10px;
  }
  
  .header-cell,
  .table-cell {
    padding: 6px;
  }
  
  .action-btn {
    padding: 5px 10px;
    font-size: 11px;
  }
  
  .amount-input {
    width: 50px;
  }
}

/* Enhanced Focus States */
.custom-select:focus,
.amount-input:focus {
  outline: none;
}

/* Improved Visual Hierarchy */
.payment-table {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-header {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}
</style>