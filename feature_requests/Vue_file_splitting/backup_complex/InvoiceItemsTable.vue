<template>
  <div class="invoice-items-section">
    <v-card
      class="cards py-0 grey lighten-5 d-flex flex-column flex-grow-1"
      style="min-height: 0"
    >
      <!-- Compact Customer Section -->
      <div class="compact-customer-section">
        <slot name="customer">
          <!-- Customer component goes here -->
        </slot>
      </div>

      <!-- Items Table -->
      <div class="my-0 py-0 invoice-items-scrollable">
        <v-data-table
          :headers="headers"
          :items="items"
          item-key="posa_row_id"
          item-value="posa_row_id"
          class="elevation-0 invoice-table"
          style="width: 700px"
          hide-default-footer
          :items-per-page="25"
          density="compact"
        >
          <!-- Item Name Column -->
          <template v-slot:item.item_name="{ item }">
            <div style="width: 120px">
              <p class="mb-0">{{ item.item_name }}</p>
            </div>
          </template>

          <!-- Quantity Column -->
          <template v-slot:item.qty="{ item }">
            <div class="compact-qty-controls">
              <button
                class="qty-btn minus-btn"
                @click="handleDecreaseQty(item)"
                :disabled="!(item.qty && item.qty > 0)"
                type="button"
              >
                <span class="btn-icon">−</span>
              </button>
              <input
                type="number"
                v-model.number="item.qty"
                @input="handleQtyInput(item)"
                @change="handleQtyChange(item)"
                @blur="handleQtyChange(item)"
                class="compact-qty-input"
                placeholder="0"
              />
              <button
                class="qty-btn plus-btn"
                @click="handleIncreaseQty(item)"
                type="button"
              >
                <span class="btn-icon">+</span>
              </button>
            </div>
          </template>

          <!-- Rate Column -->
          <template v-slot:item.rate="{ item }">
            <div class="compact-rate-wrapper">
              <input
                type="text"
                :value="formatCurrency(item.rate)"
                @change="handleRateChange(item, $event)"
                @blur="handleRateChange(item, $event)"
                @keyup.enter="handleRateChange(item, $event)"
                :disabled="!isItemEditable(item)"
                class="compact-rate-input"
                placeholder="0.00"
              />
            </div>
          </template>

          <!-- Discount Percentage Column -->
          <template v-slot:item.discount_percentage="{ item }">
            <div
              class="compact-discount-wrapper"
              :class="{ 'has-discount': item.discount_percentage > 0 }"
            >
              <input
                type="number"
                :value="formatFloat(item.discount_percentage || 0)"
                @change="handleDiscountChange(item, $event)"
                @blur="handleDiscountChange(item, $event)"
                @keyup.enter="handleDiscountChange(item, $event)"
                :disabled="!isItemDiscountEditable(item)"
                class="compact-discount-input"
                placeholder="0"
                min="0"
                :max="maxDiscountAllowed"
                step="0.01"
              />
              <span class="discount-suffix">%</span>
            </div>
          </template>

          <!-- Discount Amount Column -->
          <template v-slot:item.discount_amount="{ item }">
            <div class="compact-discount-amount">
              <span
                class="amount-value"
                :class="{ 'has-value': getDiscountAmount(item) > 0 }"
              >
                {{ formatCurrency(getDiscountAmount(item)) }}
              </span>
            </div>
          </template>

          <!-- Total Amount Column -->
          <template v-slot:item.amount="{ item }">
            <div class="compact-total-amount">
              <span class="amount-value">
                {{
                  formatCurrency(
                    flt(item.qty, floatPrecision) *
                      flt(item.rate, currencyPrecision)
                  )
                }}
              </span>
            </div>
          </template>

          <!-- Offer Indicator -->
          <template v-slot:item.posa_is_offer="{ item }">
            <v-checkbox
              :model-value="Boolean(item.posa_is_offer || item.posa_is_replace)"
              :disabled="true"
            ></v-checkbox>
          </template>

          <!-- Delete Action -->
          <template v-slot:item.actions="{ item }">
            <div class="flex justify-end">
              <v-btn
                :disabled="Boolean(item.posa_is_offer || item.posa_is_replace)"
                icon
                color="error"
                size="small"
                class="delete-item-btn"
                @click.stop="handleDeleteItem(item)"
                title="Delete item"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </div>
          </template>

          <!-- List Price Column -->
          <template v-slot:item.price_list_rate="{ item }">
            <div class="compact-price-display">
              <span class="amount-value">
                {{ formatCurrency(item.price_list_rate) }}
              </span>
            </div>
          </template>
        </v-data-table>
      </div>
    </v-card>
  </div>
</template>

<script>
import format from '../../format'

export default {
  name: 'InvoiceItemsTable',

  mixins: [format],

  props: {
    items: {
      type: Array,
      required: true,
    },
    headers: {
      type: Array,
      required: true,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    posProfile: {
      type: Object,
      default: null,
    },
    invoiceDoc: {
      type: Object,
      default: null,
    },
    floatPrecision: {
      type: Number,
      default: 2,
    },
    currencyPrecision: {
      type: Number,
      default: 2,
    },
  },

  emits: [
    'qty-change',
    'qty-input',
    'rate-change',
    'discount-change',
    'item-removed',
  ],

  computed: {
    maxDiscountAllowed() {
      return this.posProfile?.posa_item_max_discount_allowed || 100
    },
  },

  methods: {
    /**
     * Handle quantity increase
     */
    handleIncreaseQty(item) {
      if (!item) return
      item.qty = (Number(item.qty) || 0) + 1
      item.amount = this.calculateItemAmount(item)
      this.$emit('qty-change', item)
    },

    /**
     * Handle quantity decrease
     */
    handleDecreaseQty(item) {
      if (!item) return
      const newQty = Math.max(0, (Number(item.qty) || 0) - 1)
      if (newQty === 0) {
        this.handleDeleteItem(item)
      } else {
        item.qty = newQty
        item.amount = this.calculateItemAmount(item)
        this.$emit('qty-change', item)
      }
    },

    /**
     * Handle quantity input in real-time
     */
    handleQtyInput(item) {
      if (!item) return
      const newQty = Number(item.qty) || 0
      item.qty = newQty
      item.amount = this.calculateItemAmount(item)
      this.$emit('qty-input', item)
    },

    /**
     * Handle quantity change (on blur/change)
     */
    handleQtyChange(item) {
      if (!item) return
      const newQty = Number(item.qty) || 0
      item.qty = newQty
      item.amount = this.calculateItemAmount(item)
      this.$emit('qty-change', item)
    },

    /**
     * Handle rate/price change
     */
    handleRateChange(item, event) {
      if (!item || !event) return
      this.$emit('rate-change', { item, event })
    },

    /**
     * Handle discount percentage change
     */
    handleDiscountChange(item, event) {
      if (!item || !event) return
      this.$emit('discount-change', { item, event })
    },

    /**
     * Handle item deletion
     */
    handleDeleteItem(item) {
      if (!item) return
      this.$emit('item-removed', item)
    },

    /**
     * Calculate item total amount
     */
    calculateItemAmount(item) {
      if (!item) return 0
      const qty = flt(item.qty || 0)
      const rate = flt(item.rate || 0)
      return flt(qty * rate, this.currencyPrecision)
    },

    /**
     * Get discount amount for item
     */
    getDiscountAmount(item) {
      if (!item) return 0
      if (item.discount_amount) return flt(item.discount_amount) || 0

      const basePrice = flt(item.price_list_rate) || flt(item.rate) || 0
      const discountPercentage = flt(item.discount_percentage) || 0
      return discountPercentage > 0 && basePrice > 0
        ? flt((basePrice * discountPercentage) / 100) || 0
        : 0
    },

    /**
     * Check if item is editable (not an offer/promotion)
     */
    isItemEditable(item) {
      if (!item || this.readonly) return false
      return !(
        item.posa_is_offer ||
        item.posa_is_replace ||
        item.posa_offer_applied ||
        this.invoiceDoc?.is_return
      )
    },

    /**
     * Check if item discount is editable
     */
    isItemDiscountEditable(item) {
      if (!item || this.readonly) return false
      return (
        this.posProfile?.posa_allow_user_to_edit_item_discount &&
        !item.posa_is_offer &&
        !item.posa_is_replace &&
        !item.posa_offer_applied &&
        !this.invoiceDoc?.is_return
      )
    },
  },
}
</script>

<style scoped>
/* ===== ITEMS TABLE STYLING ===== */

.invoice-items-section {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.cards {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.compact-customer-section {
  padding: 4px 6px;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 0;
  background: white;
}

.invoice-items-scrollable {
  flex: 1 1 auto;
  max-height: calc(100vh - 170px);
  overflow-y: auto;
  overflow-x: hidden;
  border-collapse: collapse;
}

.invoice-table {
  width: 100% !important;
  font-size: 0.75rem !important;
}

.v-data-table__wrapper table {
  width: 100% !important;
  border-collapse: collapse !important;
}

.v-data-table__wrapper table th,
.v-data-table__wrapper table td {
  padding: 2px 4px !important;
  font-size: 0.75rem !important;
  border: none !important;
  height: auto !important;
  min-height: 0 !important;
}

.v-data-table__wrapper table th {
  font-weight: 600 !important;
  background-color: #f5f5f5 !important;
  height: 28px !important;
}

/* Quantity Controls */
.compact-qty-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2px;
  padding: 2px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 4px;
  width: 100%;
  max-width: 85px;
  min-width: 75px;
}

.compact-qty-input {
  flex: 1;
  width: 100%;
  border: 1px solid #1976d2;
  background: white;
  outline: none;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1976d2;
  text-align: center;
  padding: 2px 4px;
  border-radius: 3px;
  height: 20px;
}

.qty-btn {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  padding: 0;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0;
}

.qty-btn.minus-btn {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: white;
}

.qty-btn.plus-btn {
  background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
  color: white;
}

.qty-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Rate Input */
.compact-rate-wrapper {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 2px 4px;
  border: 1px solid #1976d2;
  border-radius: 4px;
  min-width: 70px;
  max-width: 90px;
}

.compact-rate-input {
  width: 100%;
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1976d2;
  text-align: right;
  padding: 2px 4px;
}

.compact-rate-input:disabled {
  color: #999;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Discount Input */
.compact-discount-wrapper {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 2px 4px;
  border: 1px solid #1976d2;
  border-radius: 4px;
  min-width: 55px;
  max-width: 75px;
}

.compact-discount-wrapper.has-discount {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-color: #ff9800;
}

.compact-discount-input {
  width: 100%;
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1976d2;
  text-align: right;
  padding: 2px 2px;
}

.compact-discount-wrapper.has-discount .compact-discount-input {
  color: #f57c00;
  font-weight: 700;
}

.compact-discount-input:disabled {
  color: #999;
  cursor: not-allowed;
  opacity: 0.6;
}

.discount-suffix {
  font-size: 0.65rem;
  font-weight: 700;
  color: #1976d2;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Discount Amount Display */
.compact-discount-amount {
  display: flex;
  align-items: center;
  padding: 3px 6px;
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
  border-radius: 4px;
  min-width: 60px;
}

.amount-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: #757575;
}

.amount-value.has-value {
  color: #ff9800;
  font-weight: 700;
}

/* Total Amount Display */
.compact-total-amount {
  display: flex;
  align-items: center;
  padding: 3px 6px;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border-radius: 4px;
  border: 1px solid #4caf50;
  min-width: 70px;
}

.compact-total-amount .amount-value {
  font-size: 0.8rem;
  font-weight: 700;
  color: #1b5e20;
}

/* Price Display */
.compact-price-display {
  display: flex;
  align-items: center;
  padding: 3px 6px;
  background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
  border-radius: 4px;
  min-width: 65px;
}

.compact-price-display .amount-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: #1976d2;
}

/* Delete Button */
.delete-item-btn {
  width: 16px !important;
  height: 16px !important;
  min-width: 16px !important;
  min-height: 16px !important;
  padding: 0 !important;
  border-radius: 2px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.delete-item-btn .v-icon {
  font-size: 12px !important;
}

.flex {
  display: flex;
}

.justify-end {
  justify-content: flex-end;
}
</style>
