<template>
  <div class="action-buttons-container">
    <!-- Action Buttons Row -->
    <div class="action-buttons">
      <!-- Print Button -->
      <button
        class="action-btn primary-btn"
        :disabled="!hasItems || !canPrint"
        @click="handlePrint"
        title="Print after choosing a payment method"
      >
        <v-icon size="16">mdi-printer</v-icon>
        <span>Print</span>
      </button>

      <!-- Pay Button -->
      <button
        class="action-btn success-btn"
        :disabled="!hasItems || isPaymentVisible"
        @click="handlePay"
        title="Process payment"
      >
        <v-icon size="16">mdi-cash-multiple</v-icon>
        <span>Pay</span>
      </button>

      <!-- Return Button -->
      <button
        class="action-btn secondary-btn"
        :disabled="!allowReturn"
        @click="handleReturn"
        title="Process return"
      >
        <v-icon size="16">mdi-keyboard-return</v-icon>
        <span>Return</span>
      </button>

      <!-- Quick Return Button -->
      <button
        class="action-btn purple-btn"
        :disabled="!allowQuickReturn"
        @click="handleQuickReturn"
        title="Quick return"
      >
        <v-icon size="16">mdi-flash</v-icon>
        <span>Quick Return</span>
      </button>

      <!-- Cancel Button -->
      <button
        class="action-btn error-btn"
        @click="handleCancel"
        title="Cancel invoice"
      >
        <v-icon size="16">mdi-close-circle</v-icon>
        <span>Cancel</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InvoiceActionButtons',

  props: {
    hasItems: {
      type: Boolean,
      default: false,
    },
    canPrint: {
      type: Boolean,
      default: false,
    },
    isReadonly: {
      type: Boolean,
      default: false,
    },
    isPaymentVisible: {
      type: Boolean,
      default: false,
    },
    allowReturn: {
      type: Boolean,
      default: false,
    },
    allowQuickReturn: {
      type: Boolean,
      default: false,
    },
  },

  emits: [
    'print-clicked',
    'pay-clicked',
    'return-clicked',
    'quick-return-clicked',
    'cancel-clicked',
  ],

  methods: {
    /**
     * Handle print button click
     */
    handlePrint() {
      if (!this.hasItems || !this.canPrint) return
      this.$emit('print-clicked')
    },

    /**
     * Handle pay button click
     */
    handlePay() {
      if (!this.hasItems || this.isPaymentVisible) return
      this.$emit('pay-clicked')
    },

    /**
     * Handle return button click
     */
    handleReturn() {
      if (!this.allowReturn) return
      this.$emit('return-clicked')
    },

    /**
     * Handle quick return button click
     */
    handleQuickReturn() {
      if (!this.allowQuickReturn) return
      this.$emit('quick-return-clicked')
    },

    /**
     * Handle cancel button click
     */
    handleCancel() {
      this.$emit('cancel-clicked')
    },
  },
}
</script>

<style scoped>
/* ===== ACTION BUTTONS CONTAINER ===== */

.action-buttons-container {
  padding: 0;
  margin: 0;
}

/* Action Buttons Row */
.action-buttons {
  display: flex;
  gap: 1px;
  background: white;
  padding: 2px;
  border-radius: 6px;
  width: 100%;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 30px;
  border: none;
  border-radius: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  min-width: 0;
  white-space: nowrap;
}

.action-btn:hover:not(:disabled) {
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}

.action-btn:active:not(:disabled) {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(50%);
}

.action-btn span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Button color variants */
.primary-btn {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
}

.primary-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
}

.success-btn {
  background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
  color: white;
}

.success-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
}

.secondary-btn {
  background: linear-gradient(135deg, #757575 0%, #616161 100%);
  color: white;
}

.secondary-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #616161 0%, #424242 100%);
}

.purple-btn {
  background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);
  color: white;
}

.purple-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #7b1fa2 0%, #6a1b9a 100%);
}

.error-btn {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  color: white;
}

.error-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%);
}

/* Responsive adjustments */
@media (max-width: 1280px) {
  .action-btn {
    height: 28px;
    font-size: 0.7rem;
  }

  .action-btn .v-icon {
    font-size: 14px !important;
  }
}

@media (max-width: 768px) {
  .action-btn {
    height: 26px;
    font-size: 0.65rem;
    gap: 2px;
  }

  .action-btn span {
    display: none;
  }
}
</style>
