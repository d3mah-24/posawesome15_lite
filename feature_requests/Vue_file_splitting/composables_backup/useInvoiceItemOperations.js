/**
 * useInvoiceItemOperations - Item operations composable
 * Handles all item-level operations (quantity, rate, discount)
 * 
 * This composable contains pure business logic for item operations
 * and can be used across different components.
 */

import { ref } from 'vue'
import { evntBus } from '../bus'

export function useInvoiceItemOperations(posProfile = null, currencyPrecision = 2) {
  // Configuration
  const floatPrecision = 2
  const currency_precision = currencyPrecision

  /**
   * Increase item quantity by 1
   * @param {Object} item - Item to modify
   */
  const increaseQuantity = (item) => {
    if (!item) return
    item.qty = (Number(item.qty) || 0) + 1
    item.amount = calculateItemAmount(item)
    evntBus.emit('item_updated', item)
  }

  /**
   * Decrease item quantity by 1, or remove if already 0
   * @param {Object} item - Item to modify
   * @returns {boolean} - true if item was removed, false if just decreased
   */
  const decreaseQuantity = (item) => {
    if (!item) return false
    const newQty = Math.max(0, (Number(item.qty) || 0) - 1)
    
    if (newQty === 0) {
      // Item will be removed by parent component
      return true
    } else {
      item.qty = newQty
      item.amount = calculateItemAmount(item)
      evntBus.emit('item_updated', item)
      return false
    }
  }

  /**
   * Handle quantity input change
   * @param {Object} item - Item being modified
   */
  const onQtyChange = (item) => {
    if (!item) return
    const newQty = Number(item.qty) || 0
    item.qty = newQty
    item.amount = calculateItemAmount(item)
    evntBus.emit('item_updated', item)
  }

  /**
   * Handle quantity input event (real-time)
   * @param {Object} item - Item being modified
   */
  const onQtyInput = (item) => {
    onQtyChange(item)
  }

  /**
   * Calculate total amount for an item (qty * rate)
   * @param {Object} item - Item to calculate
   * @returns {number} - Total amount
   */
  const calculateItemAmount = (item) => {
    if (!item) return 0
    const qty = flt(item.qty || 0)
    const rate = flt(item.rate || 0)
    return flt(qty * rate, currency_precision)
  }

  /**
   * Get discount amount for an item
   * @param {Object} item - Item to get discount for
   * @returns {number} - Discount amount
   */
  const getDiscountAmount = (item) => {
    if (!item) return 0
    
    // If discount_amount is directly set, use it
    if (item.discount_amount) {
      return flt(item.discount_amount) || 0
    }

    // Calculate from discount percentage
    const basePrice = flt(item.price_list_rate) || flt(item.rate) || 0
    const discountPercentage = flt(item.discount_percentage) || 0
    
    if (discountPercentage > 0 && basePrice > 0) {
      return flt((basePrice * discountPercentage) / 100) || 0
    }
    
    return 0
  }

  /**
   * Set item rate (selling price)
   * @param {Object} item - Item to modify
   * @param {Event} event - Change event
   */
  const setItemRate = (item, event) => {
    if (!item || !event) return
    
    let dis_price = parseFloat(event.target.value) || 0
    const list_price = flt(item.price_list_rate) || 0

    if (dis_price < 0) dis_price = 0

    // Don't allow dis_price higher than list_price
    if (dis_price > list_price) {
      dis_price = list_price
      evntBus.emit('show_mesage', {
        text: 'Price exceeds limit',
        color: 'error',
      })
    }

    // Calculate discount percentage from price difference
    let dis_percent = 0
    if (list_price > 0) {
      dis_percent = ((list_price - dis_price) / list_price) * 100
    }

    // Apply max discount limit if configured
    const maxDiscount = posProfile?.posa_item_max_discount_allowed || 100
    if (dis_percent > maxDiscount) {
      const max_dis_amount = (list_price * maxDiscount) / 100
      dis_price = flt(list_price - max_dis_amount, currency_precision)
      dis_percent = maxDiscount

      evntBus.emit('show_mesage', {
        text: `Maximum discount applied: ${maxDiscount}%`,
        color: 'info',
      })
    }

    item.rate = dis_price
    item.discount_percentage = flt(dis_percent, 2)
    item.amount = calculateItemAmount(item)

    evntBus.emit('item_updated', item)
  }

  /**
   * Set item discount percentage
   * @param {Object} item - Item to modify
   * @param {Event} event - Change event
   */
  const setDiscountPercentage = (item, event) => {
    if (!item || !event) return
    
    let dis_percent = parseFloat(event.target.value) || 0

    // Apply max discount limit
    const maxDiscount = posProfile?.posa_item_max_discount_allowed || 100

    if (dis_percent < 0) dis_percent = 0
    if (dis_percent > maxDiscount) {
      dis_percent = maxDiscount
      evntBus.emit('show_mesage', {
        text: `Maximum discount applied: ${maxDiscount}%`,
        color: 'info',
      })
    }

    item.discount_percentage = dis_percent

    // Calculate new rate from discount percentage
    const list_price = flt(item.price_list_rate) || 0
    if (list_price > 0) {
      if (dis_percent > 0) {
        const dis_amount = (list_price * dis_percent) / 100
        item.rate = flt(list_price - dis_amount, currency_precision)
      } else {
        item.rate = list_price
      }
      item.amount = calculateItemAmount(item)
    }

    evntBus.emit('item_updated', item)
  }

  /**
   * Validate item data
   * @param {Object} item - Item to validate
   * @returns {Object} - Validation result { valid: boolean, errors: array }
   */
  const validateItemData = (item) => {
    const errors = []

    if (!item) {
      errors.push('Item is required')
      return { valid: false, errors }
    }

    if (!item.item_code) {
      errors.push('Item code is required')
    }

    if (item.qty < 0) {
      errors.push('Quantity cannot be negative')
    }

    if (item.rate < 0) {
      errors.push('Rate cannot be negative')
    }

    if (item.discount_percentage < 0 || item.discount_percentage > 100) {
      errors.push('Discount must be between 0 and 100')
    }

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  /**
   * Generate unique row ID for items
   * @returns {string} - Unique ID
   */
  const generateRowId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  /**
   * Check if item is editable (not an offer/promotion)
   * @param {Object} item - Item to check
   * @param {Object} invoiceDoc - Invoice document
   * @returns {boolean} - true if editable
   */
  const isItemEditable = (item, invoiceDoc = null) => {
    if (!item) return false
    
    // Check for offer/promotion indicators
    if (item.posa_is_offer || item.posa_is_replace || item.posa_offer_applied) {
      return false
    }

    // Check for return invoices
    if (invoiceDoc?.is_return) {
      return false
    }

    return true
  }

  return {
    // Quantity operations
    increaseQuantity,
    decreaseQuantity,
    onQtyChange,
    onQtyInput,

    // Amount operations
    calculateItemAmount,
    getDiscountAmount,

    // Rate/Discount operations
    setItemRate,
    setDiscountPercentage,

    // Utilities
    validateItemData,
    generateRowId,
    isItemEditable,
  }
}
