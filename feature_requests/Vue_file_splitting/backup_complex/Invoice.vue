<template>
  <div class="invoice-container">
    <!-- Customer Section Slot -->
    <InvoiceItemsTable
      ref="itemsTableRef"
      :items="state.items.value"
      :headers="state.dynamicHeaders.value"
      :readonly="state.readonly.value"
      :pos-profile="state.posProfile.value"
      :invoice-doc="state.invoiceDoc.value"
      :float-precision="state.floatPrecision.value"
      :currency-precision="state.currencyPrecision.value"
      @qty-change="handleQtyChange"
      @qty-input="handleQtyInput"
      @rate-change="handleRateChange"
      @discount-change="handleDiscountChange"
      @item-removed="handleItemRemoved"
    >
      <template #customer>
        <Customer></Customer>
      </template>
    </InvoiceItemsTable>

    <!-- Financial Summary -->
    <InvoiceFinancialSummary
      :invoice-doc="state.invoiceDoc.value"
      :additional-discount-percentage="state.additionalDiscountPercentage.value"
      :pos-profile="state.posProfile.value"
      :is-readonly="state.readonly.value"
      @discount-updated="handleDiscountUpdated"
    />

    <!-- Action Buttons -->
    <InvoiceActionButtons
      :has-items="state.hasItems.value"
      :can-print="state.canPrintInvoice.value"
      :is-readonly="state.readonly.value"
      :is-payment-visible="isPaymentVisible"
      :allow-return="Boolean(state.posProfile.value?.posa_allow_return)"
      :allow-quick-return="Boolean(state.posProfile.value?.posa_allow_quick_return)"
      @print-clicked="printInvoice"
      @pay-clicked="showPayment"
      @return-clicked="openReturns"
      @quick-return-clicked="quickReturn"
      @cancel-clicked="cancelInvoice"
    />
  </div>
</template>

<script>
import { evntBus } from '../../bus'
import { API_MAP } from '../../api_mapper'
import Customer from './Customer.vue'
import InvoiceItemsTable from './InvoiceItemsTable.vue'
import InvoiceFinancialSummary from './InvoiceFinancialSummary.vue'
import InvoiceActionButtons from './InvoiceActionButtons.vue'
import { useInvoiceState } from '../../composables/useInvoiceState'
import { useInvoiceSync } from '../../composables/useInvoiceSync'
import { useInvoiceItemOperations } from '../../composables/useInvoiceItemOperations'

export default {
  name: 'Invoice',

  components: {
    Customer,
    InvoiceItemsTable,
    InvoiceFinancialSummary,
    InvoiceActionButtons,
  },

  props: {
    is_payment: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      isPaymentVisible: false,
      itemOpsDebounceTimer: null,
    }
  },

  setup() {
    const state = useInvoiceState()
    const sync = useInvoiceSync()
    const itemOps = useInvoiceItemOperations()

    return { state, sync, itemOps }
  },

  methods: {
    // ===== ITEM OPERATIONS =====

    handleQtyInput(item) {
      this.itemOps.onQtyInput(item)
      this.debouncedItemOperation('qty-input')
    },

    handleQtyChange(item) {
      this.itemOps.onQtyChange(item)
      this.debouncedItemOperation('qty-change')
    },

    handleRateChange({ item, event }) {
      this.itemOps.setItemRate(item, event)
      this.debouncedItemOperation('rate-change')
    },

    handleDiscountChange({ item, event }) {
      this.itemOps.setDiscountPercentage(item, event)
      this.debouncedItemOperation('discount-change')
    },

    async handleItemRemoved(item) {
      const index = this.state.items.value.findIndex(
        (el) => el.posa_row_id == item.posa_row_id
      )
      if (index >= 0) {
        this.state.items.value.splice(index, 1)
        if (this.state.items.value.length === 0 && this.state.invoiceDoc.value?.name) {
          await this.deleteInvoiceOnEmpty()
        } else {
          evntBus.emit('item_removed', item)
          this.debouncedItemOperation('item-removed')
        }
      }
    },

    handleDiscountUpdated(value) {
      this.state.additionalDiscountPercentage.value = value
      this.debouncedItemOperation('invoice-discount-change')
    },

    debouncedItemOperation(reason = 'auto') {
      if (this.itemOpsDebounceTimer) {
        clearTimeout(this.itemOpsDebounceTimer)
      }

      this.itemOpsDebounceTimer = setTimeout(async () => {
        try {
          const doc = this.sync.getInvoiceDoc(this.state, reason)
          await this.sync.autoUpdateInvoice(doc, reason)
        } catch (error) {
          evntBus.emit('show_mesage', {
            text: 'Update failed: ' + (error.message || 'Unknown error'),
            color: 'error',
          })
        }
      }, 1000)
    },

    async deleteInvoiceOnEmpty() {
      try {
        if (this.state.invoiceDoc.value?.name) {
          await this.sync.deleteInvoice(this.state.invoiceDoc.value.name)
          this.state.clearInvoice()
        }
      } catch (error) {
        // Silently ignore delete errors
      }
    },

    // ===== INVOICE OPERATIONS =====

    async showPayment() {
      if (this.state.readonly.value) return

      evntBus.emit('show_loading', { text: 'Loading...', color: 'info' })

      try {
        const doc = this.sync.getInvoiceDoc(this.state, 'payment')
        const invoiceDoc = await this.sync.autoUpdateInvoice(doc, 'payment')

        if (!invoiceDoc) {
          evntBus.emit('hide_loading')
          return
        }

        // Add default payment if needed
        if (!invoiceDoc.payments || invoiceDoc.payments.length === 0) {
          try {
            const defaultPayment = await frappe.call({
              method: 'posawesome.posawesome.api.pos_profile.get_default_payment',
              args: {
                pos_profile: this.state.posProfile.value?.name,
                company:
                  this.state.posProfile.value?.company ||
                  frappe.defaults.get_user_default('Company'),
              },
            })

            if (defaultPayment.message) {
              invoiceDoc.payments = [
                {
                  mode_of_payment: defaultPayment.message.mode_of_payment,
                  amount: flt(invoiceDoc?.grand_total),
                  account: defaultPayment.message.account,
                  default: 1,
                },
              ]
            }
          } catch (error) {
            // Continue without default payment
          }
        }

        evntBus.emit('send_invoice_doc_payment', invoiceDoc)
        evntBus.emit('show_payment', 'true')

        this.state.posOffers.value = []
        this.state.posCoupons.value = []

        if (this.state.posProfile.value?.posa_clear_customer_after_payment) {
          this.state.setCustomer(this.state.posProfile.value?.customer)
        }

        evntBus.emit('invoice_session_reset')
        evntBus.emit('hide_loading')
      } catch (error) {
        evntBus.emit('hide_loading')
        evntBus.emit('show_mesage', {
          text: 'Error: ' + error.message,
          color: 'error',
        })
      }
    },

    openReturns() {
      if (!Boolean(this.state.posProfile.value?.posa_allow_return)) return

      evntBus.emit('open_returns', {
        pos_profile: this.state.posProfile.value,
        pos_opening_shift: this.state.posOpeningShift.value || null,
      })
    },

    quickReturn() {
      if (
        !Boolean(this.state.posProfile.value?.posa_allow_quick_return) ||
        !this.state.customer.value ||
        !this.state.items.value.length
      ) {
        return
      }
      this.state.quickReturnValue.value = !this.state.quickReturnValue.value
      evntBus.emit('toggle_quick_return', this.state.quickReturnValue.value)
    },

    async printInvoice() {
      if (!this.state.invoiceDoc.value || !this.state.defaultPaymentMode.value) return

      evntBus.emit('show_loading', { text: 'Processing...', color: 'info' })

      try {
        const doc = this.sync.getInvoiceDoc(this.state, 'print')
        const invoiceDoc = await this.sync.autoUpdateInvoice(doc, 'print')

        if (!this.hasValidPayments(invoiceDoc)) {
          evntBus.emit('show_payment', 'true')
          evntBus.emit('hide_loading')
          return
        }

        // Submit invoice
        frappe.call({
          method: 'frappe.client.submit',
          args: { doc: invoiceDoc },
          callback: (r) => {
            evntBus.emit('hide_loading')

            if (r.message?.name) {
              const print_format = this.state.posProfile.value?.print_format
              const print_url = frappe.urllib.get_full_url(
                `/printview?doctype=Sales%20Invoice&name=${r.message.name}&format=${print_format}&trigger_print=1&no_letterhead=0`
              )

              window.open(print_url)

              evntBus.emit('set_last_invoice', r.message.name)
              evntBus.emit('show_mesage', {
                text: `Invoice ${r.message.name} submitted`,
                color: 'success',
              })
              frappe.utils.play_sound('submit')

              this.state.resetInvoiceState()
              this.state.invoiceDoc.value = null
              evntBus.emit('new_invoice', 'false')
              evntBus.emit('invoice_submitted')
            } else {
              evntBus.emit('show_mesage', {
                text: 'Submit failed',
                color: 'error',
              })
            }
          },
          error: (err) => {
            evntBus.emit('hide_loading')
            evntBus.emit('show_mesage', {
              text: err?.message || 'Failed to submit',
              color: 'error',
            })
          },
        })
      } catch (error) {
        evntBus.emit('hide_loading')
        evntBus.emit('show_mesage', {
          text: 'Error: ' + error.message,
          color: 'error',
        })
      }
    },

    cancelInvoice() {
      if (this.state.invoiceDoc.value && this.state.invoiceDoc.value?.name) {
        frappe.call({
          method: 'frappe.client.delete',
          args: {
            doctype: 'Sales Invoice',
            name: this.state.invoiceDoc.value?.name,
          },
          callback: (r) => {
            if (r.message) {
              evntBus.emit('show_mesage', {
                text: 'Draft cancelled',
                color: 'success',
              })
            }
          },
        })
      }

      this.state.resetInvoiceState()
      this.state.customer.value = this.state.posProfile.value?.customer
      this.state.invoiceDoc.value = null
      evntBus.emit('set_customer_readonly', false)
      evntBus.emit('show_payment', 'false')
    },

    hasValidPayments(invoiceDoc = null) {
      const doc = invoiceDoc || this.state.invoiceDoc.value
      return doc?.payments?.some((p) => flt(p.amount) > 0) || false
    },

    // ===== EVENT BUS HANDLERS =====

    setupEventListeners() {
      evntBus.on('register_pos_profile', this.onRegisterPosProfile)
      evntBus.on('add_item', this.onAddItem)
      evntBus.on('update_customer', this.onUpdateCustomer)
      evntBus.on('fetch_customer_details', this.onFetchCustomerDetails)
      evntBus.on('new_invoice', this.onNewInvoice)
      evntBus.on('load_invoice', this.onLoadInvoice)
      evntBus.on('load_return_invoice', this.onLoadReturnInvoice)
      evntBus.on('update_invoice_offers', this.onUpdateInvoiceOffers)
      evntBus.on('update_invoice_coupons', this.onUpdateInvoiceCoupons)
      evntBus.on('set_all_items', this.onSetAllItems)
      evntBus.on('send_invoice_doc_payment', this.onSendInvoiceDocPayment)
      evntBus.on('payments_updated', this.onPaymentsUpdated)
      evntBus.on('request_invoice_print', this.onRequestInvoicePrint)
    },

    onRegisterPosProfile(data) {
      this.state.setPosProfile(data.pos_profile)
      this.state.posOpeningShift.value = data.pos_opening_shift
      this.state.stockSettings.value = data.stock_settings
      this.state.floatPrecision.value =
        frappe.defaults.get_default('float_precision') || 2
      this.state.currencyPrecision.value =
        frappe.defaults.get_default('currency_precision') || 2
      this.state.customer.value = data.pos_profile?.customer
    },

    onAddItem(item) {
      this.addItemToInvoice(item)
    },

    async addItemToInvoice(item) {
      if (!item?.item_code) return

      const newItem = Object.assign({}, item)
      newItem.uom = newItem.uom || newItem.stock_uom || 'Nos'

      const existingItem = this.state.items.value.find(
        (existing) =>
          existing.item_code === newItem.item_code &&
          existing.uom === newItem.uom
      )

      if (existingItem) {
        existingItem.qty = flt(existingItem.qty) + flt(newItem.qty)
        existingItem.amount = flt(existingItem.qty * existingItem.rate, this.state.currencyPrecision.value)
      } else {
        newItem.posa_row_id = this.state.generateUUID()
        newItem.posa_offers = '[]'
        newItem.posa_offer_applied = 0
        newItem.posa_is_offer = 0
        newItem.posa_is_replace = 0
        newItem.is_free_item = 0
        newItem.amount = flt(newItem.rate * newItem.qty, this.state.currencyPrecision.value)
        this.state.items.value.push(newItem)
      }

      if (this.state.items.value.length === 1 && !this.state.invoiceDoc.value?.name) {
        await this.createFirstInvoice()
      } else {
        evntBus.emit('item_added', existingItem || newItem)
        this.debouncedItemOperation('item-added')
      }
    },

    async createFirstInvoice() {
      try {
        const doc = this.sync.getInvoiceDoc(this.state, 'create')
        const result = await this.sync.createInvoice(doc)
        if (result) {
          this.state.invoiceDoc.value = result
        }
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Failed to create invoice',
          color: 'error',
        })
      }
    },

    onUpdateCustomer(customer) {
      this.state.setCustomer(customer)
      this.fetchCustomerDetails()
    },

    onFetchCustomerDetails() {
      this.fetchCustomerDetails()
    },

    fetchCustomerDetails() {
      if (!this.state.customer.value) return

      frappe.call({
        method: API_MAP.CUSTOMER.GET_CUSTOMER,
        args: { customer_id: this.state.customer.value },
        async: false,
        callback: (r) => {
          if (!r.exc && r.message) {
            this.state.customerInfo.value = r.message
            evntBus.emit('set_customer_info_to_edit', this.state.customerInfo.value)
            this.updatePriceList()
          }
        },
      })
    },

    updatePriceList() {
      let priceList = this.state.posProfile.value?.selling_price_list
      if (this.state.customerInfo.value && this.state.posProfile.value) {
        const { customer_price_list, customer_group_price_list } = this.state.customerInfo.value
        const posProfilePrice = this.state.posProfile.value?.selling_price_list
        if (customer_price_list && customer_price_list != posProfilePrice) {
          priceList = customer_price_list
        } else if (customer_group_price_list && customer_group_price_list != posProfilePrice) {
          priceList = customer_group_price_list
        }
      }
      evntBus.emit('update_customer_price_list', priceList)
    },

    onNewInvoice() {
      this.state.newInvoice()
    },

    onLoadInvoice(data) {
      this.state.loadInvoice(data)
      if (data.is_return) {
        this.state.discountAmount.value = -data.discount_amount
        this.state.additionalDiscountPercentage.value = -data.additional_discount_percentage
        this.state.returnDoc.value = data
      } else {
        evntBus.emit('set_pos_coupons', data.posa_coupons)
      }
    },

    onLoadReturnInvoice(data) {
      this.state.loadInvoice(data.invoice_doc)

      if (data.return_doc) {
        this.state.discountAmount.value = -data.return_doc.discount_amount || 0
        this.state.additionalDiscountPercentage.value = -data.return_doc.additional_discount_percentage || 0
        this.state.returnDoc.value = data.return_doc
      } else {
        this.state.discountAmount.value = 0
        this.state.additionalDiscountPercentage.value = 0
        this.state.returnDoc.value = null
      }
    },

    onUpdateInvoiceOffers(offers) {
      this.state.posOffers.value = offers || []

      const grandTotalOffer = offers?.find(
        (offer) => offer.offer === 'Grand Total' && offer.offer_applied
      )

      if (grandTotalOffer && grandTotalOffer.discount_percentage) {
        this.state.additionalDiscountPercentage.value = parseFloat(
          grandTotalOffer.discount_percentage || 0
        )
      } else {
        this.state.additionalDiscountPercentage.value = 0
      }

      if (this.state.invoiceDoc.value?.name) {
        this.debouncedItemOperation('offers-change')
      }
    },

    onUpdateInvoiceCoupons(data) {
      this.state.posCoupons.value = data
      this.debouncedItemOperation('coupons-change')
    },

    onSetAllItems(data) {
      this.state.allItems.value = data
    },

    onSendInvoiceDocPayment(doc) {
      this.state.invoiceDoc.value = doc
    },

    onPaymentsUpdated(payments) {
      if (this.state.invoiceDoc.value) {
        this.state.invoiceDoc.value.payments = payments || []
      }
    },

    onRequestInvoicePrint() {
      if (!this.state.canPrintInvoice.value) {
        evntBus.emit('show_mesage', {
          text: 'Please select a payment method before printing',
          color: 'warning',
        })
        return
      }
      this.printInvoice()
    },

    // ===== KEYBOARD SHORTCUTS =====

    setupKeyboardShortcuts() {
      document.addEventListener('keydown', this.onKeyDown)
    },

    onKeyDown(e) {
      if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault()
        this.showPayment()
      }
    },
  },

  mounted() {
    this.setupEventListeners()
    this.setupKeyboardShortcuts()
  },

  beforeUnmount() {
    // Clean up event listeners
    evntBus.$off('register_pos_profile', this.onRegisterPosProfile)
    evntBus.$off('add_item', this.onAddItem)
    evntBus.$off('update_customer', this.onUpdateCustomer)
    evntBus.$off('fetch_customer_details', this.onFetchCustomerDetails)
    evntBus.$off('new_invoice', this.onNewInvoice)
    evntBus.$off('load_invoice', this.onLoadInvoice)
    evntBus.$off('load_return_invoice', this.onLoadReturnInvoice)
    evntBus.$off('update_invoice_offers', this.onUpdateInvoiceOffers)
    evntBus.$off('update_invoice_coupons', this.onUpdateInvoiceCoupons)
    evntBus.$off('set_all_items', this.onSetAllItems)
    evntBus.$off('send_invoice_doc_payment', this.onSendInvoiceDocPayment)
    evntBus.$off('payments_updated', this.onPaymentsUpdated)
    evntBus.$off('request_invoice_print', this.onRequestInvoicePrint)

    document.removeEventListener('keydown', this.onKeyDown)

    // Clean up state
    this.state.cleanup()
    this.sync.cleanup()

    // Clear debounce timer
    if (this.itemOpsDebounceTimer) {
      clearTimeout(this.itemOpsDebounceTimer)
    }
  },
}
</script>

<style scoped>
.invoice-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  padding-bottom: 70px;
}
</style>
