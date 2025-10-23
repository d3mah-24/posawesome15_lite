<template>
  <div class="dialog-row">
    <div v-if="closingDialog" class="custom-modal-overlay" @click="close_dialog">
      <!-- Custom Beautiful Dialog -->
      <div class="beautiful-dialog" @click.stop>
        <!-- Compact Header -->
        <div class="dialog-header">
          <div class="header-content">
            <div class="header-icon">
              <i class="mdi mdi-cash-register cash-icon"></i>
            </div>
            <div class="header-text">
              <h3 class="dialog-title">Close POS</h3>
            </div>
          </div>
          <button class="close-btn" @click="close_dialog">
            <i class="mdi mdi-close close-icon"></i>
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
                    <i 
                      class="mdi payment-icon"
                      :class="getPaymentIcon(item.mode_of_payment).icon"
                      :style="{ color: getPaymentIcon(item.mode_of_payment).color }"
                    ></i>
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
                    <i class="mdi mdi-pencil edit-icon"></i>
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
            <i class="mdi mdi-close cancel-icon"></i>
            Cancel
          </button>
          <button 
            v-if="isClosingAllowed"
            class="action-btn submit-btn" 
            @click="submit_dialog"
          >
            <i class="mdi mdi-check submit-icon"></i>
            Submit
          </button>
          <div v-if="!isClosingAllowed && closingTimeMessage" class="time-restriction-message">
            <i class="mdi mdi-clock-alert-outline alert-icon"></i>
            {{ closingTimeMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { evntBus } from '../../bus';
import format from '../../format';
import { API_MAP } from "../../api_mapper.js";

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// CONSTANTS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Event names for bus communication
 */
const EVENT_NAMES = {
  OPEN_CLOSING_DIALOG: 'open_ClosingDialog',
  REGISTER_POS_PROFILE: 'register_pos_profile',
  SUBMIT_CLOSING_POS: 'submit_closing_pos',
};

/**
 * Payment method icons and colors
 */
const PAYMENT_ICONS = {
  Cash: { icon: 'mdi-cash', color: '#4CAF50' },
  Card: { icon: 'mdi-credit-card', color: '#2196F3' },
  'Credit Card': { icon: 'mdi-credit-card', color: '#2196F3' },
  'Debit Card': { icon: 'mdi-credit-card-outline', color: '#FF9800' },
  'Bank Transfer': { icon: 'mdi-bank-transfer', color: '#9C27B0' },
  'Mobile Payment': { icon: 'mdi-cellphone', color: '#E91E63' },
  'Digital Wallet': { icon: 'mdi-wallet', color: '#00BCD4' },
  Check: { icon: 'mdi-checkbook', color: '#795548' },
  Voucher: { icon: 'mdi-ticket', color: '#FF5722' },
};

/**
 * Default payment icon for unknown methods
 */
const DEFAULT_PAYMENT_ICON = { icon: 'mdi-currency-usd', color: '#607D8B' };

/**
 * Table column headers configuration
 */
const TABLE_HEADERS = {
  PAYMENT_METHOD: {
    title: 'Payment Method',
    key: 'mode_of_payment',
    align: 'start',
    sortable: true,
  },
  SYSTEM_TOTAL: {
    title: 'System Total',
    align: 'end',
    sortable: true,
    key: 'opening_amount',
  },
  ACTUAL_COUNT: {
    title: 'Actual Count',
    key: 'closing_amount',
    align: 'end',
    sortable: true,
  },
  EXPECTED_TOTAL: {
    title: 'Expected Total',
    key: 'expected_amount',
    align: 'end',
    sortable: false,
  },
  DIFFERENCE: {
    title: 'Difference',
    key: 'difference',
    align: 'end',
    sortable: false,
  },
};

/**
 * Validation rules
 */
const VALIDATION_RULES = {
  MAX_CHARS: (v) => v.length <= 20 || 'Input too long!',
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// COMPONENT
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export default {
  name: 'ClosingDialog',
  
  mixins: [format],
  
  setup() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // STATE
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    const closingDialog = ref(false);
    const itemsPerPage = ref(20);
    const dialog_data = ref({ payment_reconciliation: [] });
    const pos_profile = ref(null);
    const headers = ref([
      TABLE_HEADERS.PAYMENT_METHOD,
      TABLE_HEADERS.SYSTEM_TOTAL,
      TABLE_HEADERS.ACTUAL_COUNT,
    ]);

    // Time control
    const isClosingAllowed = ref(true);
    const closingTimeMessage = ref('');

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DIALOG ACTIONS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Close the closing dialog
     * Resets dialog visibility to false
     */
    const close_dialog = () => {
      closingDialog.value = false;
    };

    /**
     * Submit closing dialog data
     * Emits submit event with payment reconciliation data
     */
    const submit_dialog = () => {
      evntBus.emit(EVENT_NAMES.SUBMIT_CLOSING_POS, dialog_data.value);
      closingDialog.value = false;
    };

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // HELPER METHODS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Get payment method icon and color
     * @param {string} paymentMethod - Payment method name
     * @returns {Object} Icon configuration with icon name and color
     */
    const getPaymentIcon = (paymentMethod) => {
      const method = Object.keys(PAYMENT_ICONS).find((key) =>
        paymentMethod.toLowerCase().includes(key.toLowerCase())
      );

      return method ? PAYMENT_ICONS[method] : DEFAULT_PAYMENT_ICON;
    };

    /**
     * Get CSS class for difference amount
     * @param {number} difference - Difference value
     * @returns {string} CSS class name
     */
    const getDifferenceClass = (difference) => {
      if (difference > 0) return 'positive-diff';
      if (difference < 0) return 'negative-diff';
      return 'zero-diff';
    };

    /**
     * Check if closing POS is allowed based on time controls
     * Validates against configured closing time window if enabled
     */
    const checkClosingTimeAllowed = () => {
      if (!pos_profile.value?.name) {
        isClosingAllowed.value = true;
        return;
      }

      // Call server-side whitelist function
      frappe.call({
        method: API_MAP.POS_CLOSING_SHIFT.CHECK_CLOSING_TIME_ALLOWED,
        args: {
          pos_profile: pos_profile.value.name
        },
        callback: function(r) {
          if (r.message) {
            isClosingAllowed.value = r.message.allowed;
            if (!r.message.allowed) {
              closingTimeMessage.value = r.message.message;
            }
          } else {
            isClosingAllowed.value = false;
            closingTimeMessage.value = 'Error checking closing time permissions';
          }
        }
      });
    };    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EVENT HANDLERS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /**
     * Handle opening closing dialog event
     * @param {Object} data - Payment reconciliation data
     */
    const openClosingDialogHandler = (data) => {
      closingDialog.value = true;
      dialog_data.value = data;
      checkClosingTimeAllowed();
    };

    /**
     * Handle POS profile registration
     * Configures table headers based on profile settings
     * @param {Object} data - Profile data with pos_profile
     */
    const registerPosProfileHandler = (data) => {
      pos_profile.value = data.pos_profile;
      
      if (!pos_profile.value.posa_hide_expected_amount) {
        headers.value.push(TABLE_HEADERS.EXPECTED_TOTAL);
        headers.value.push(TABLE_HEADERS.DIFFERENCE);
      }
    };

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // LIFECYCLE HOOKS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    onMounted(() => {
      evntBus.on(EVENT_NAMES.OPEN_CLOSING_DIALOG, openClosingDialogHandler);
      evntBus.on(EVENT_NAMES.REGISTER_POS_PROFILE, registerPosProfileHandler);
    });

    onBeforeUnmount(() => {
      evntBus.off(EVENT_NAMES.OPEN_CLOSING_DIALOG, openClosingDialogHandler);
      evntBus.off(EVENT_NAMES.REGISTER_POS_PROFILE, registerPosProfileHandler);
    });

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EXPOSE
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    return {
      // State
      closingDialog,
      itemsPerPage,
      dialog_data,
      pos_profile,
      headers,
      
      // Time control
      isClosingAllowed,
      closingTimeMessage,
      
      // Validation
      max25chars: VALIDATION_RULES.MAX_CHARS,
      
      // Actions
      close_dialog,
      submit_dialog,
      
      // Helpers
      getPaymentIcon,
      getDifferenceClass,
    };
  },
};
</script>

<style scoped>
/* ===== CENTRALIZED POS STYLING ===== */
/* This file contains all POS dialog styling */
/* ERP forms use default Frappe styling */
/* Reports use simple HTML without custom CSS */

/* Dialog Row Container */
.dialog-row {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Enhanced Beautiful Dialog with Centralized POS Styling */
.beautiful-dialog {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-width: 450px;
  width: 100%;
  animation: dialogSlideIn 0.3s ease-out;
  border: 1px solid rgba(102, 126, 234, 0.1);
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

/* Enhanced Header with Centralized POS Styling */
.dialog-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.dialog-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  transform: rotate(45deg);
  pointer-events: none;
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

.cash-icon {
  color: white;
  font-size: 18px;
}

.close-icon {
  color: white;
  font-size: 14px;
}

.dialog-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
  position: relative;
  z-index: 2;
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

.payment-icon {
  font-size: 14px;
}

.edit-icon {
  opacity: 0;
  transition: opacity 0.1s ease;
  color: #6366f1;
  margin-left: 2px;
  font-size: 10px;
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

.cancel-icon,
.submit-icon {
  font-size: 14px;
}

.time-restriction-message {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f59e0b;
  font-size: 12px;
  font-weight: 500;
  padding: 8px 12px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.alert-icon {
  color: #ff9800;
  font-size: 14px;
  margin-left: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
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

/* ===== CUSTOM MODAL ===== */
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: modal-fade-in 0.2s ease;
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
</style>