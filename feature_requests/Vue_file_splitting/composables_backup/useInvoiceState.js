/**
 * useInvoiceState - Invoice state management composable
 * Manages all invoice-related reactive state
 */

import { ref, computed } from 'vue'
import { evntBus } from '../bus'

export function useInvoiceState() {
  // ===== CORE STATE =====
  const invoiceDoc = ref(null)
  const items = ref([])
  const posProfile = ref(null)
  const posOpeningShift = ref(null)
  const stockSettings = ref(null)
  const customer = ref('')
  const customerInfo = ref({})
  
  // ===== DISCOUNT STATE =====
  const discountAmount = ref(0)
  const additionalDiscountPercentage = ref(0)
  const totalTax = ref(0)

  // ===== OFFERS & COUPONS =====
  const posOffers = ref([])
  const posCoupons = ref([])
  const discountPercentageOfferName = ref(null)

  // ===== CONFIGURATION =====
  const floatPrecision = ref(2)
  const currencyPrecision = ref(2)
  const invoicePostingDate = ref(false)
  const postingDate = ref(frappe.datetime.nowdate())
  const quickReturnValue = ref(false)
  const invoiceType = ref('Invoice')
  const invoiceTypes = ref(['Invoice'])
  const returnDoc = ref(null)

  // ===== INTERNAL STATE =====
  const _itemOperationTimer = ref(null)
  const _updatingFromAPI = ref(false)
  const _offersCache = ref(null)
  const _offersProcessing = ref(false)
  const _couponCache = ref(null)
  const _autoUpdateTimer = ref(null)
  const allItems = ref([])

  // ===== COMPUTED PROPERTIES =====

  /**
   * Check if invoice is readonly (return invoices, submitted, etc)
   */
  const readonly = computed(() => {
    return invoiceDoc.value?.is_return || false
  })

  /**
   * Check if invoice has items
   */
  const hasItems = computed(() => {
    return items.value && items.value.length > 0
  })

  /**
   * Check if invoice has valid payments
   */
  const hasValidPayments = computed(() => {
    return invoiceDoc.value?.payments?.some((p) => flt(p.amount) > 0) || false
  })

  /**
   * Get default payment mode from profile or invoice
   */
  const defaultPaymentMode = computed(() => {
    const invoicePayments =
      invoiceDoc.value && Array.isArray(invoiceDoc.value?.payments)
        ? invoiceDoc.value?.payments
        : []
    const profilePayments =
      posProfile.value && Array.isArray(posProfile.value?.payments)
        ? posProfile.value?.payments
        : []
    const payments = invoicePayments.length ? invoicePayments : profilePayments

    // First try to find a payment marked as default
    let defaultRow = payments.find((payment) => payment.default == 1)

    // If no default payment is found, use the first payment as default
    if (!defaultRow && payments.length > 0) {
      defaultRow = payments[0]
    }

    return defaultRow ? defaultRow.mode_of_payment : null
  })

  /**
   * Check if can print invoice
   */
  const canPrintInvoice = computed(() => {
    if (readonly.value || !items.value?.length) return false
    return hasValidPayments.value || !!defaultPaymentMode.value
  })

  /**
   * Get dynamic table headers based on config
   */
  const dynamicHeaders = computed(() => {
    const baseHeaders = [
      {
        title: 'i_name',
        align: 'start',
        sortable: true,
        key: 'item_name',
        width: '25%',
      },
      {
        title: 'Qty',
        key: 'qty',
        align: 'center',
        width: '8%',
      },
      {
        title: 'Uom',
        key: 'uom',
        align: 'center',
        width: '8%',
      },
      {
        title: 'list_price',
        key: 'price_list_rate',
        align: 'center',
        width: '10%',
      },
      {
        title: 'dis_price',
        key: 'rate',
        align: 'center',
        width: '10%',
      },
      {
        title: 'dis_%',
        key: 'discount_percentage',
        align: 'center',
        width: '8%',
      },
      {
        title: 'dis_amount',
        key: 'discount_amount',
        align: 'center',
        width: '10%',
      },
      {
        title: 'Total',
        key: 'amount',
        align: 'center',
        width: '11%',
      },
      {
        title: 'Delete',
        key: 'actions',
        align: 'end',
        sortable: false,
        width: '5%',
      },
    ]

    let headers = [...baseHeaders]

    if (!posProfile.value?.posa_display_discount_percentage) {
      headers = headers.filter((header) => header.key !== 'discount_percentage')
    }

    if (!posProfile.value?.posa_display_discount_amount) {
      headers = headers.filter((header) => header.key !== 'discount_amount')
    }

    if (!posProfile.value?.posa_allow_user_to_edit_item_discount) {
      headers = headers.filter((header) => header.key !== 'rate')
    }

    return headers
  })

  // ===== STATE MODIFIERS =====

  /**
   * Reset invoice to initial state
   */
  const resetInvoiceState = () => {
    invoiceType.value = 'Invoice'
    invoiceTypes.value = ['Invoice']
    postingDate.value = frappe.datetime.nowdate()
    items.value = []
    posOffers.value = []
    posCoupons.value = []
    discountAmount.value = 0
    additionalDiscountPercentage.value = 0
    evntBus.emit('update_invoice_type', invoiceType.value)
    evntBus.emit('set_pos_coupons', [])
    evntBus.emit('update_invoice_doc', null)
  }

  /**
   * Load an existing invoice
   */
  const loadInvoice = (data) => {
    if (!data) return

    invoiceDoc.value = data
    items.value = data.items || []
    customer.value = data.customer || customer.value
    postingDate.value = data.posting_date || frappe.datetime.nowdate()
    discountAmount.value = data.discount_amount || 0
    additionalDiscountPercentage.value = data.additional_discount_percentage || 0
    posOffers.value = data.posa_offers || []

    if (data.is_return) {
      invoiceType.value = 'Return'
      invoiceTypes.value = ['Return']
      returnDoc.value = data
    }

    // Ensure items have row IDs
    items.value.forEach((item) => {
      if (!item.posa_row_id) {
        item.posa_row_id = generateUUID(20)
      }
    })

    evntBus.emit('update_invoice_type', invoiceType.value)
  }

  /**
   * Start a new invoice
   */
  const newInvoice = (data = {}) => {
    invoiceDoc.value = null
    customer.value = posProfile.value?.customer || customer.value
    resetInvoiceState()

    if (data.name || data.is_return) {
      loadInvoice(data)
    }
  }

  /**
   * Clear customer and reset discounts
   */
  const clearInvoice = () => {
    invoiceDoc.value = null
    items.value = []
    customer.value = posProfile.value?.customer || customer.value
    discountAmount.value = 0
    additionalDiscountPercentage.value = 0
    posOffers.value = []
    posCoupons.value = []
    returnDoc.value = null
  }

  /**
   * Update customer
   */
  const setCustomer = (customerName) => {
    customer.value = customerName
  }

  /**
   * Update pos profile
   */
  const setPosProfile = (profile) => {
    posProfile.value = profile
    if (profile?.customer) {
      customer.value = profile.customer
    }
  }

  /**
   * Generate UUID for item row
   */
  const generateUUID = (length = 20) => {
    return crypto.randomUUID
      ? crypto.randomUUID().substring(0, length)
      : Math.random()
          .toString(36)
          .substring(2, 2 + length)
  }

  /**
   * Clean up internal state on unmount
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
    // ===== STATE =====
    invoiceDoc,
    items,
    posProfile,
    posOpeningShift,
    stockSettings,
    customer,
    customerInfo,
    discountAmount,
    additionalDiscountPercentage,
    totalTax,
    posOffers,
    posCoupons,
    floatPrecision,
    currencyPrecision,
    invoicePostingDate,
    postingDate,
    quickReturnValue,
    invoiceType,
    invoiceTypes,
    returnDoc,
    allItems,

    // ===== INTERNAL STATE (exported for debugging) =====
    _itemOperationTimer,
    _updatingFromAPI,
    _offersCache,
    _offersProcessing,
    _couponCache,
    _autoUpdateTimer,

    // ===== COMPUTED =====
    readonly,
    hasItems,
    hasValidPayments,
    defaultPaymentMode,
    canPrintInvoice,
    dynamicHeaders,

    // ===== METHODS =====
    resetInvoiceState,
    loadInvoice,
    newInvoice,
    clearInvoice,
    setCustomer,
    setPosProfile,
    generateUUID,
    cleanup,
  }
}
