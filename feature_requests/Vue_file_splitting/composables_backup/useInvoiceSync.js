/**
 * useInvoiceSync - Invoice API synchronization composable
 * Handles all server communication and invoice persistence
 */

import { ref } from 'vue'
import { evntBus } from '../bus'
import { API_MAP } from '../api_mapper.js'

export function useInvoiceSync() {
  // ===== INTERNAL STATE =====
  const _itemOperationTimer = ref(null)
  const _autoUpdateTimer = ref(null)
  const _updatingFromAPI = ref(false)

  /**
   * Create a new invoice on the server
   * @param {Object} doc - Invoice document
   * @returns {Promise<Object>} - Created invoice
   */
  const createInvoice = (doc) => {
    return new Promise((resolve, reject) => {
      frappe.call({
        method: API_MAP.SALES_INVOICE.CREATE,
        args: {
          data: doc,
        },
        async: true,
        callback: function (r) {
          if (r.message !== undefined) {
            if (r.message === null) {
              resolve(null)
            } else {
              // Emit event for navbar to update invoice display
              evntBus.emit('update_invoice_doc', r.message)

              // Update posa_offers from backend response
              if (r.message.posa_offers) {
                const appliedOffers = r.message.posa_offers.filter(
                  (offer) => offer.offer_applied
                )
                if (appliedOffers.length > 0) {
                  evntBus.emit('update_pos_offers', appliedOffers)
                }
              }

              resolve(r.message)
            }
          } else {
            reject(new Error('Failed to create invoice'))
          }
        },
        error: function (err) {
          reject(err)
        },
      })
    })
  }

  /**
   * Update existing invoice on the server
   * @param {Object} doc - Invoice document with name
   * @returns {Promise<Object>} - Updated invoice
   */
  const updateInvoice = (doc) => {
    return new Promise((resolve, reject) => {
      // Ensure we have an invoice name for updates
      if (!doc.name) {
        reject(new Error('Invoice name required for updates'))
        return
      }

      frappe.call({
        method: API_MAP.SALES_INVOICE.UPDATE,
        args: {
          data: doc,
        },
        async: true,
        callback: function (r) {
          if (r.message !== undefined) {
            if (r.message === null) {
              resolve(null)
            } else {
              // Update posa_offers from backend response
              if (r.message.posa_offers) {
                const appliedOffers = r.message.posa_offers.filter(
                  (offer) => offer.offer_applied
                )
                if (appliedOffers.length > 0) {
                  evntBus.emit('update_pos_offers', appliedOffers)
                }
              }

              resolve(r.message)
            }
          } else {
            reject(new Error('Failed to update invoice'))
          }
        },
        error: function (err) {
          if (
            err.message &&
            err.message.includes('Document has been modified')
          ) {
            // Invoice was modified by another user - need to reload
            reject(new Error('DOCUMENT_MODIFIED'))
          } else {
            reject(err)
          }
        },
      })
    })
  }

  /**
   * Reload invoice from server (handles conflicts)
   * @param {string} invoiceName - Invoice name to reload
   * @returns {Promise<Object>} - Reloaded invoice
   */
  const reloadInvoice = (invoiceName) => {
    return new Promise((resolve, reject) => {
      if (!invoiceName) {
        reject(new Error('Invoice name required'))
        return
      }

      frappe.call({
        method: 'frappe.client.get',
        args: {
          doctype: 'Sales Invoice',
          name: invoiceName,
        },
        callback: function (r) {
          if (r.message) {
            resolve(r.message)
          } else {
            reject(new Error('Failed to reload invoice'))
          }
        },
        error: function (err) {
          reject(err)
        },
      })
    })
  }

  /**
   * Delete invoice from server
   * @param {string} invoiceName - Invoice name to delete
   * @returns {Promise<void>}
   */
  const deleteInvoice = (invoiceName) => {
    return new Promise((resolve, reject) => {
      if (!invoiceName) {
        reject(new Error('Invoice name required'))
        return
      }

      frappe.call({
        method: API_MAP.SALES_INVOICE.DELETE,
        args: { invoice_name: invoiceName },
        callback: (r) => {
          resolve()
        },
        error: (err) => {
          reject(err)
        },
      })
    })
  }

  /**
   * Auto-save invoice with debouncing
   * @param {Object} doc - Invoice document to save
   * @param {string} reason - Reason for save (auto, item-update, etc)
   * @returns {Promise<Object>} - Saved invoice
   */
  const autoUpdateInvoice = async (doc, reason = 'auto') => {
    // Skip if invoice submitted for payment
    if (doc?.submitted_for_payment) {
      return null
    }

    // Skip if no items and no invoice doc
    if (!doc || (doc.items?.length === 0 && !doc.name)) {
      return null
    }

    try {
      _updatingFromAPI.value = true

      let result

      if (!doc.name && doc.items?.length > 0) {
        // Create new invoice
        result = await createInvoice(doc)
      } else if (doc.name) {
        // Update existing invoice
        result = await updateInvoice(doc)
      } else {
        return null
      }

      if (result && Array.isArray(result.items)) {
        // API returned items - merge with local state
        return result
      }

      return result
    } catch (error) {
      if (error.message === 'DOCUMENT_MODIFIED') {
        // Reload and retry
        try {
          const reloaded = await reloadInvoice(doc.name)
          return reloaded
        } catch (reloadError) {
          throw reloadError
        }
      }
      throw error
    } finally {
      _updatingFromAPI.value = false
    }
  }

  /**
   * Queue auto-save with 1-second debounce
   * @param {Object} doc - Invoice document
   * @param {string} reason - Reason for save
   * @returns {Promise<void>}
   */
  const queueAutoSave = (doc, reason = 'auto') => {
    return new Promise((resolve) => {
      // Clear existing timer
      if (_autoUpdateTimer.value) {
        clearTimeout(_autoUpdateTimer.value)
      }

      // Wait 1 second after user stops, then send update
      _autoUpdateTimer.value = setTimeout(async () => {
        try {
          await autoUpdateInvoice(doc, reason)
          resolve()
        } catch (error) {
          evntBus.emit('show_mesage', {
            text: 'Auto-saving failed: ' + (error.message || 'Unknown error'),
            color: 'error',
          })
          resolve() // Still resolve to prevent hanging
        }
      }, 1000) // 1 second delay
    })
  }

  /**
   * Merge items from API response with local items
   * Preserves local state like price_list_rate
   * @param {Array} localItems - Local item array
   * @param {Array} apiItems - Items from API
   * @returns {Array} - Merged items
   */
  const mergeItemsFromAPI = (localItems, apiItems) => {
    if (!apiItems || !Array.isArray(apiItems) || apiItems.length === 0) {
      return localItems
    }

    // Create a map of local items by item_code
    const localItemsByCode = new Map()
    localItems.forEach((item) => {
      localItemsByCode.set(item.item_code, item)
    })

    // Merge API items with local items
    return apiItems.map((apiItem) => {
      const localItem = localItemsByCode.get(apiItem.item_code)

      // Preserve price_list_rate from local
      if (localItem?.price_list_rate && !apiItem.price_list_rate) {
        apiItem.price_list_rate = localItem.price_list_rate
      }

      // Preserve base_rate from local
      if (localItem?.base_rate && !apiItem.base_rate) {
        apiItem.base_rate = localItem.base_rate
      }

      // Preserve posa_row_id from local
      if (localItem?.posa_row_id && !apiItem.posa_row_id) {
        apiItem.posa_row_id = localItem.posa_row_id
      }

      return apiItem
    })
  }

  /**
   * Get minimal invoice document for API
   * @param {Object} state - Invoice state object
   * @param {string} reason - Reason for API call
   * @returns {Object} - Minimal invoice document
   */
  const getInvoiceDoc = (state, reason = 'auto') => {
    const doc = {}

    // Add invoice name if updating
    if (
      state.invoiceDoc?.name &&
      !state.invoiceDoc?.submitted_for_payment
    ) {
      doc.name = state.invoiceDoc.name
    }

    // Basic fields
    doc.doctype = 'Sales Invoice'
    doc.is_pos = 1
    doc.ignore_pricing_rule = 1
    doc.company = state.posProfile?.company
    doc.pos_profile = state.posProfile?.name
    doc.currency = state.posProfile?.currency
    doc.naming_series = state.posProfile?.naming_series
    doc.customer = state.customer
    doc.posting_date = state.postingDate
    doc.posa_pos_opening_shift = state.posOpeningShift?.name || null

    // Items
    doc.items = state.items.map((item) => ({
      item_code: item.item_code,
      qty: item.qty || 1,
      rate: item.rate || item.price_list_rate || 0,
      price_list_rate: item.price_list_rate || 0,
      uom: item.uom || item.stock_uom,
      conversion_factor: item.conversion_factor || 1,
      serial_no: item.serial_no,
      discount_percentage: item.discount_percentage || 0,
      batch_no: item.batch_no,
    }))

    // Discounts
    doc.discount_amount = flt(state.discountAmount || 0)
    doc.additional_discount_percentage = flt(
      state.additionalDiscountPercentage || 0
    )

    // Offers
    doc.posa_offers = state.posOffers || []

    // Return fields if applicable
    if (state.invoiceDoc) {
      doc.is_return = state.invoiceDoc.is_return
      doc.return_against = state.invoiceDoc.return_against
    }

    // Payment fields for payment flow
    if (reason === 'payment' || reason === 'print') {
      doc.payments = state.payments || []
    }

    return doc
  }

  /**
   * Clean up timers on unmount
   */
  const cleanup = () => {
    if (_itemOperationTimer.value) {
      clearTimeout(_itemOperationTimer.value)
      _itemOperationTimer.value = null
    }
    if (_autoUpdateTimer.value) {
      clearTimeout(_autoUpdateTimer.value)
      _autoUpdateTimer.value = null
    }
  }

  return {
    // CRUD operations
    createInvoice,
    updateInvoice,
    reloadInvoice,
    deleteInvoice,

    // Auto-save operations
    autoUpdateInvoice,
    queueAutoSave,

    // Helpers
    mergeItemsFromAPI,
    getInvoiceDoc,

    // Lifecycle
    cleanup,

    // Internal state (for debugging)
    _updatingFromAPI,
  }
}
