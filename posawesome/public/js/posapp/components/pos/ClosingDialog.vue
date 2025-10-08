<template>
  <v-row justify="center">
    <v-dialog v-model="closingDialog" max-width="420px" overlay-opacity="0.7">
      <!-- Custom Beautiful Dialog -->
      <div class="beautiful-dialog">
        <!-- Compact Header -->
        <div class="dialog-header">
          <div class="header-content">
            <div class="header-icon">
              <v-icon color="white" size="18">mdi-cash-register</v-icon>
            </div>
            <div class="header-text">
              <h3 class="dialog-title">Close POS</h3>
            </div>
          </div>
          <button class="close-btn" @click="close_dialog">
            <v-icon color="white" size="14">mdi-close</v-icon>
          </button>
        </div>

        <!-- Compact Content -->
        <div class="dialog-content" v-if="pos_profile">
          <!-- Compact Table -->
          <div class="payment-table">
            <div class="table-header">
              <div class="header-cell method-col">Method</div>
              <div class="header-cell amount-col">System</div>
              <div class="header-cell amount-col">Actual</div>
              <div class="header-cell amount-col" v-if="!pos_profile.posa_hide_expected_amount">Expected</div>
              <div class="header-cell amount-col" v-if="!pos_profile.posa_hide_expected_amount">Diff</div>
            </div>
            
            <div class="table-body">
              <div 
                v-for="(item, index) in dialog_data.payment_reconciliation" 
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
                  <span class="amount">{{ formatCurrency(item.opening_amount) }}</span>
                </div>
                
                <div class="table-cell amount-col">
                  <div class="editable-amount" v-if="item.editing">
                    <input 
                      v-model="item.closing_amount"
                      type="number"
                      class="amount-input"
                      @blur="item.editing = false"
                      @keyup.enter="item.editing = false"
                    />
                  </div>
                  <div v-else class="amount-display" @click="item.editing = true">
                    <span class="amount clickable">{{ formatCurrency(item.closing_amount) }}</span>
                    <v-icon size="10" class="edit-icon">mdi-pencil</v-icon>
                  </div>
                </div>
                
                <div class="table-cell amount-col" v-if="!pos_profile.posa_hide_expected_amount">
                  <span class="amount">{{ formatCurrency(item.expected_amount) }}</span>
                </div>
                
                <div class="table-cell amount-col" v-if="!pos_profile.posa_hide_expected_amount">
                  <span class="amount" :class="getDifferenceClass(item.expected_amount - item.closing_amount)">
                    {{ formatCurrency(item.expected_amount - item.closing_amount) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Compact Footer -->
        <div class="dialog-footer">
          <button class="action-btn cancel-btn" @click="close_dialog">
            <v-icon size="14">mdi-close</v-icon>
            Cancel
          </button>
          <button class="action-btn submit-btn" @click="submit_dialog">
            <v-icon size="14">mdi-check</v-icon>
            Submit
          </button>
        </div>
      </div>
    </v-dialog>
  </v-row>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { evntBus } from '../../bus';
import format from '../../format';

export default {
  mixins: [format],
  setup() {
    const closingDialog = ref(false);
    const itemsPerPage = ref(20);
    const dialog_data = ref({ payment_reconciliation: [] });
    const pos_profile = ref('');
    const headers = ref([
      {
        title: 'Payment Method',
        key: 'mode_of_payment',
        align: 'start',
        sortable: true,
      },
      {
        title: 'System Total',
        align: 'end',
        sortable: true,
        key: 'opening_amount',
      },
      {
        title: 'Actual Count',
        key: 'closing_amount',
        align: 'end',
        sortable: true,
      },
    ]);
    const max25chars = (v) => v.length <= 20 || 'Input too long!';

    const close_dialog = () => {
      closingDialog.value = false;
    };

    const submit_dialog = () => {
      evntBus.emit('submit_closing_pos', dialog_data.value);
      closingDialog.value = false;
    };

    // Helper methods for custom design
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

    const getDifferenceClass = (difference) => {
      if (difference > 0) return 'positive-diff';
      if (difference < 0) return 'negative-diff';
      return 'zero-diff';
    };

    const openClosingDialogHandler = (data) => {
      closingDialog.value = true;
      dialog_data.value = data;
    };

    const registerPosProfileHandler = (data) => {
      pos_profile.value = data.pos_profile;
      if (!pos_profile.value.posa_hide_expected_amount) {
        headers.value.push({
          title: 'Expected Total',
          key: 'expected_amount',
          align: 'end',
          sortable: false,
        });
        headers.value.push({
          title: 'Difference',
          key: 'difference',
          align: 'end',
          sortable: false,
        });
      }
    };

    onMounted(() => {
      evntBus.on('open_ClosingDialog', openClosingDialogHandler);
      evntBus.on('register_pos_profile', registerPosProfileHandler);
    });

    onBeforeUnmount(() => {
      evntBus.off('open_ClosingDialog', openClosingDialogHandler);
      evntBus.off('register_pos_profile', registerPosProfileHandler);
    });

    return {
      closingDialog,
      itemsPerPage,
      dialog_data,
      pos_profile,
      headers,
      max25chars,
      close_dialog,
      submit_dialog,
      getPaymentIcon,
      getDifferenceClass,
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
  padding: 8px;
  background: #fafbfc;
}

/* Compact Table */
.payment-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8eaed;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
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
  justify-content: flex-end;
}

.header-cell.method-col {
  justify-content: flex-start;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.1s ease;
}

.table-row:hover {
  background: #f8fafc;
}

.table-cell {
  padding: 6px 8px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 12px;
  min-height: 32px;
}

.table-cell.method-col {
  justify-content: flex-start;
}

/* Compact Payment Method */
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

/* Compact Amount */
.amount {
  font-weight: 600;
  color: #1e293b;
  font-size: 11px;
  font-family: monospace;
}

.amount.clickable {
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 3px;
  transition: all 0.1s ease;
  background: rgba(99, 102, 241, 0.05);
}

.amount.clickable:hover {
  background: rgba(99, 102, 241, 0.1);
}

.edit-icon {
  opacity: 0;
  transition: opacity 0.1s ease;
  color: #6366f1;
  margin-left: 2px;
}

.amount.clickable:hover .edit-icon {
  opacity: 1;
}

/* Compact Input */
.amount-input {
  background: white;
  border: 1px solid #6366f1;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  font-family: monospace;
  width: 70px;
  text-align: right;
  outline: none;
}

/* Difference Colors */
.positive-diff { color: #059669; }
.negative-diff { color: #dc2626; }
.zero-diff { color: #64748b; }

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

.cancel-btn {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.cancel-btn:hover {
  background: #e2e8f0;
}

.submit-btn {
  background: #10b981;
  color: white;
}

.submit-btn:hover {
  background: #059669;
  transform: translateY(-1px);
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
    padding: 6px;
  }
  
  .table-header,
  .table-row {
    font-size: 10px;
  }
  
  .header-cell,
  .table-cell {
    padding: 4px 6px;
  }
  
  .action-btn {
    padding: 5px 10px;
    font-size: 11px;
  }
}
</style>