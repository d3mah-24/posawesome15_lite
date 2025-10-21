<template>
  <div class="payment-controls-card">
    <!-- Financial Summary Row -->
    <div class="financial-summary">
      <!-- Total Quantity -->
      <div class="summary-field readonly-field">
        <label>Total Qty</label>
        <div class="field-value">
          {{ formatFloat(invoiceDoc?.total_qty || 0) }}
        </div>
      </div>

      <!-- Invoice Discount Percentage (Editable) -->
      <div class="summary-field editable-field">
        <label>inv_disc%</label>
        <input
          type="number"
          v-model.number="discountPercentage"
          @blur="handleDiscountChange"
          @keyup.enter="handleDiscountChange"
          step="0.01"
          min="0"
          :max="maxInvoiceDiscount"
          :disabled="isDiscountDisabled"
          class="field-input discount-input"
          placeholder="0.00"
        />
      </div>

      <!-- Item Discount Total (Read-only) -->
      <div class="summary-field readonly-field warning-field">
        <label>items_dis</label>
        <div class="field-value">
          {{ currencySymbol(posProfile?.currency)
          }}{{ formatCurrency(invoiceDoc?.posa_item_discount_total || 0) }}
        </div>
      </div>

      <!-- Subtotal (Before Discount) -->
      <div class="summary-field readonly-field">
        <label>before_disc</label>
        <div class="field-value">
          {{ currencySymbol(posProfile?.currency)
          }}{{ formatCurrency(invoiceDoc?.total || 0) }}
        </div>
      </div>

      <!-- Net Total (After Item Discount) -->
      <div class="summary-field readonly-field">
        <label>net_total</label>
        <div class="field-value">
          {{ currencySymbol(posProfile?.currency)
          }}{{ formatCurrency(invoiceDoc?.net_total) }}
        </div>
      </div>

      <!-- Tax -->
      <div class="summary-field readonly-field info-field">
        <label>tax</label>
        <div class="field-value">
          {{ currencySymbol(posProfile?.currency)
          }}{{ formatCurrency(invoiceDoc?.total_taxes_and_charges) }}
        </div>
      </div>

      <!-- Grand Total (Highlighted) -->
      <div class="summary-field readonly-field success-field grand-total">
        <label>grand_total</label>
        <div class="field-value">
          {{ currencySymbol(posProfile?.currency)
          }}{{ formatCurrency(invoiceDoc?.grand_total) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import format from '../../format'

export default {
  name: 'InvoiceFinancialSummary',

  mixins: [format],

  props: {
    invoiceDoc: {
      type: Object,
      default: null,
    },
    additionalDiscountPercentage: {
      type: Number,
      default: 0,
    },
    posProfile: {
      type: Object,
      default: null,
    },
    isReadonly: {
      type: Boolean,
      default: false,
    },
  },

  emits: ['discount-updated'],

  data() {
    return {
      discountPercentage: this.additionalDiscountPercentage,
    }
  },

  computed: {
    maxInvoiceDiscount() {
      return this.posProfile?.posa_invoice_max_discount_allowed || 100
    },

    isDiscountDisabled() {
      return (
        this.isReadonly ||
        !this.posProfile ||
        !this.posProfile?.posa_allow_user_to_edit_additional_discount ||
        this.invoiceDoc?.is_return
      )
    },
  },

  watch: {
    additionalDiscountPercentage(newVal) {
      this.discountPercentage = newVal
    },
  },

  methods: {
    /**
     * Handle discount percentage change
     */
    handleDiscountChange() {
      let value = flt(this.discountPercentage) || 0
      const maxDiscount = this.maxInvoiceDiscount

      // Validate bounds
      if (value < 0) {
        value = 0
        this.discountPercentage = 0
      } else if (value > maxDiscount) {
        value = maxDiscount
        this.discountPercentage = maxDiscount
      }

      // Emit the updated value
      this.$emit('discount-updated', value)
    },
  },
}
</script>

<style scoped>
/* ===== PAYMENT CONTROLS CARD - COMPACT & PROFESSIONAL ===== */
.payment-controls-card {
  position: fixed !important;
  bottom: 0 !important;
  left: 0 !important;
  right: 0 !important;
  width: 100% !important;
  z-index: 1000 !important;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 0 !important;
  padding: 6px;
  margin: 0 !important;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.15);
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.payment-controls-card:hover {
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.2);
}

/* Financial Summary Row */
.financial-summary {
  display: flex;
  gap: 2px;
  background: white;
  padding: 1px;
  border-radius: 6px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 2px;
}

.summary-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 2px 4px;
  border-radius: 4px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  min-width: 0;
}

.summary-field label {
  font-size: 0.65rem;
  margin-bottom: 0;
  font-weight: 600;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.summary-field .field-value {
  font-size: 0.75rem;
  font-weight: 700;
  color: #1976d2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

/* Readonly field styling */
.readonly-field {
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  cursor: default;
}

.readonly-field:hover {
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
  border-color: #bdbdbd;
}

/* Editable field styling */
.editable-field {
  background: white;
  border: 1px solid #1976d2;
}

.editable-field:hover {
  background: #e3f2fd;
  border-color: #1565c0;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.editable-field .field-input {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1976d2;
  padding: 0;
  text-align: left;
}

.editable-field .field-input:focus {
  color: #0d47a1;
}

/* Color-coded fields */
.warning-field .field-value {
  color: #f57c00;
}

.info-field .field-value {
  color: #0288d1;
}

/* Success field styling (for Grand Total) */
.success-field {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border: 1px solid #4caf50;
}

.success-field .field-value {
  color: #2e7d32;
  font-size: 0.85rem;
}

.success-field:hover {
  background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
  box-shadow: 0 2px 6px rgba(76, 175, 80, 0.2);
}

/* Grand Total emphasis */
.grand-total {
  flex: 1.2;
}

.grand-total .field-value {
  font-size: 0.9rem;
  font-weight: 800;
}

/* Input styling */
.discount-input {
  -moz-appearance: textfield;
}

.discount-input::-webkit-outer-spin-button,
.discount-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.discount-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  color: #999;
}

/* Responsive adjustments */
@media (max-width: 1280px) {
  .summary-field label {
    font-size: 0.6rem;
  }

  .summary-field .field-value,
  .editable-field .field-input {
    font-size: 0.7rem;
  }
}
</style>
