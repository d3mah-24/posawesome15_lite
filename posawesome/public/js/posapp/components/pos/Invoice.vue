<template>
  <div>
    <div class="cards py-0 grey lighten-5 d-flex flex-column flex-grow-1" style="min-height: 0">
      <!-- Compact Customer Section -->
      <div class="compact-customer-section">
        <Customer></Customer>
      </div>

      <div class="my-0 py-0 invoice-items-scrollable">
        <table class="invoice-table elevation-0" style="width: 600px">
          <thead>
            <tr>
              <th
                v-for="header in dynamicHeaders"
                :key="header.key"
                :style="{ width: header.width, textAlign: header.align }"
                class="table-header-cell"
              >
                {{ header.title }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in items"
              :key="item.posa_row_id"
              class="table-row"
            >
              <!-- Item Name Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'item_name')" class="table-cell">
                <div style="width: 120px">
                  <p class="mb-0">{{ item.item_name }}</p>
                </div>
              </td>

              <!-- Quantity Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'qty')" class="table-cell">
                <div class="compact-qty-controls">
                  <button
                    class="qty-btn minus-btn"
                    @click="decreaseQuantity(item)"
                    :disabled="!(item.qty && item.qty > 0)"
                    type="button"
                  >
                    <span class="btn-icon">−</span>
                  </button>
                  <input
                    type="number"
                    v-model.number="item.qty"
                    @input="onQtyInput(item)"
                    @change="onQtyChange(item)"
                    @blur="onQtyChange(item)"
                    class="compact-qty-input"
                    placeholder="0"
                  />
                  <button
                    class="qty-btn plus-btn"
                    @click="increaseQuantity(item)"
                    type="button"
                  >
                    <span class="btn-icon">+</span>
                  </button>
                </div>
              </td>

              <!-- UOM Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'uom')" class="table-cell">
                {{ item.uom }}
              </td>

              <!-- Price List Rate Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'price_list_rate')" class="table-cell">
                <div class="compact-price-display">
                  <span class="amount-value">
                    {{ formatCurrency(item.price_list_rate) }}
                  </span>
                </div>
              </td>

              <!-- Rate (Discounted Price) Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'rate')" class="table-cell">
                <div class="compact-rate-wrapper">
                  <input
                    type="text"
                    :value="formatCurrency(item.rate)"
                    @change="setItemRate(item, $event)"
                    @blur="setItemRate(item, $event)"
                    @keyup.enter="setItemRate(item, $event)"
                    :disabled="
                      Boolean(
                        item.posa_is_offer ||
                          item.posa_is_replace ||
                          item.posa_offer_applied ||
                          invoice_doc?.is_return
                      )
                    "
                    class="compact-rate-input"
                    placeholder="0.00"
                  />
                </div>
              </td>

              <!-- Discount Percentage Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'discount_percentage')" class="table-cell">
                <div
                  class="compact-discount-wrapper"
                  :class="{ 'has-discount': item.discount_percentage > 0 }"
                >
                  <input
                    type="number"
                    :value="formatFloat(item.discount_percentage || 0)"
                    @change="setDiscountPercentage(item, $event)"
                    @blur="setDiscountPercentage(item, $event)"
                    @keyup.enter="setDiscountPercentage(item, $event)"
                    :disabled="
                      Boolean(
                        item.posa_is_offer ||
                          item.posa_is_replace ||
                          item.posa_offer_applied ||
                          !pos_profile?.posa_allow_user_to_edit_item_discount ||
                          invoice_doc?.is_return
                      )
                    "
                    class="compact-discount-input"
                    placeholder="0"
                    min="0"
                    :max="pos_profile?.posa_item_max_discount_allowed || 100"
                    step="0.01"
                  />
                  <span class="discount-suffix">%</span>
                </div>
              </td>

              <!-- Discount Amount Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'discount_amount')" class="table-cell">
                <div class="compact-discount-amount">
                  <span
                    class="amount-value"
                    :class="{ 'has-value': getDiscountAmount(item) > 0 }"
                  >
                    {{ formatCurrency(getDiscountAmount(item)) }}
                  </span>
                </div>
              </td>

              <!-- Total Amount Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'amount')" class="table-cell">
                <div class="compact-total-amount">
                  <span class="amount-value">
                    {{
                      formatCurrency(
                        flt(item.qty, float_precision) *
                          flt(item.rate, currency_precision)
                      )
                    }}
                  </span>
                </div>
              </td>

              <!-- Actions Column -->
              <td v-if="dynamicHeaders.find(h => h.key === 'actions')" class="table-cell">
                <div class="flex justify-end">
                  <button
                    :disabled="Boolean(item.posa_is_offer || item.posa_is_replace)"
                    class="delete-item-btn error-btn-small"
                    @click.stop="remove_item(item)"
                    title="Delete item"
                  >
                    <i class="mdi mdi-delete"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>      <!-- Compact Payment Controls Card -->
      <div class="payment-controls-card">
        <!-- Financial Summary Row -->
        <div class="financial-summary">
          <div class="summary-field readonly-field">
            <label>Total Qty</label>
            <div class="field-value">
              {{ formatFloat(invoice_doc?.total_qty || 0) }}
            </div>
          </div>
  
          <div class="summary-field editable-field">
            <label>inv_disc%</label>
            <input
              type="number"
              v-model.number="additional_discount_percentage"
              @blur="update_discount_umount"
              ref="percentage_discount"
              step="0.01"
              min="0"
              :max="pos_profile?.posa_invoice_max_discount_allowed || 100"
              :disabled="
                Boolean(
                  offer_discount_percentage > 0||
                  !pos_profile ||
                    !pos_profile?.posa_allow_user_to_edit_additional_discount ||
                    invoice_doc?.is_return
                )
              "
              class="field-input discount-input"
              placeholder="0.00"
            />
          </div>
  
          <div class="summary-field readonly-field warning-field">
            <label>items_dis</label>
            <div class="field-value">
              {{ currencySymbol(pos_profile?.currency) }}{{ formatCurrency(invoice_doc?.posa_item_discount_total || 0) }}
            </div>
          </div>
  
          <div class="summary-field readonly-field">
            <label>before_disc</label>
            <div class="field-value">
              {{ currencySymbol(pos_profile?.currency) }}{{ formatCurrency(invoice_doc?.total || 0) }}
            </div>
          </div>
  
          <div class="summary-field readonly-field">
            <label>net_total</label>
            <div class="field-value">
              {{ currencySymbol(pos_profile?.currency) }}{{ formatCurrency(invoice_doc?.net_total) }}
            </div>
          </div>
  
          <div class="summary-field readonly-field info-field">
            <label>tax</label>
            <div class="field-value">
              {{ currencySymbol(pos_profile?.currency) }}{{ formatCurrency(invoice_doc?.total_taxes_and_charges) }}
            </div>
          </div>
  
          <div class="summary-field readonly-field success-field grand-total">
            <label>grand_total</label>
            <div class="field-value">
              {{ currencySymbol(pos_profile?.currency) }}{{ formatCurrency(invoice_doc?.grand_total) }}
            </div>
          </div>
        </div>
  
        <!-- Action Buttons Row -->
        <div class="action-buttons">
          <button
            class="action-btn primary-btn"
            :disabled="!hasItems || !hasChosenPayment"
            @click="printInvoice"
            title="Print after choosing a payment method"
          >
            <i class="mdi mdi-printer action-icon"></i>
            <span>Print</span>
          </button>
  
          <button
            class="action-btn success-btn"
            :disabled="!hasItems || is_payment||isUpdatingTotals"
            @click="show_payment"
          >
            <i class="mdi mdi-cash-multiple action-icon"></i>
            <span>Pay</span>
          </button>
  
          <button
            class="action-btn secondary-btn"
            :disabled="!pos_profile?.posa_allow_return"
            @click="open_returns"
          >
            <i class="mdi mdi-keyboard-return action-icon"></i>
            <span>Return</span>
          </button>
  
          <button
            class="action-btn purple-btn"
            :disabled="!pos_profile?.posa_allow_quick_return"
            @click="quick_return"
          >
            <i class="mdi mdi-flash action-icon"></i>
            <span>Quick Return</span>
          </button>
  
          <button class="action-btn error-btn" @click="cancel_invoice">
            <i class="mdi mdi-close-circle action-icon"></i>
            <span>Cancel</span>
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  // ===== IMPORTS =====
  import { evntBus } from "../../bus";
  import format from "../../format";
  import Customer from "./Customer.vue";
  import { API_MAP } from "../../api_mapper.js";
  
  // ===== COMPONENT =====
  export default {
    name: "Invoice",
  
    mixins: [format],
  
    components: {
      Customer,
    },
  
    props: {
      is_payment: {
        type: Boolean,
        default: false,
      },
      offerApplied: {
        type: Object,
        default: null,
      },
      offerRemoved: {
        type: Boolean,
        default: false,
      },
    },
  
    // ===== DATA =====
    data() {
      return {
        pos_profile: null,
        pos_opening_shift: null,
        stock_settings: null,
        invoice_doc: null,
        return_doc: null,
        customer: "",
        customer_info: {},
        discount_amount: 0,
        additional_discount_percentage: 0,
        offer_discount_percentage: 0,
        total_tax: 0,
        items: [],
        posa_offers: [],
        posa_coupons: [],
        discount_percentage_offer_name: null,
        float_precision: 2,
        currency_precision: 2,
        invoice_posting_date: false,
        posting_date: frappe.datetime.nowdate(),
        quick_return_value: false,

        isUpdatingTotals: false,
        // Simple State Management
        _itemOperationTimer: null,
        _updatingFromAPI: false,
  
        // Table Headers Configuration
        items_headers: [
          {
            title: "i_name",
            align: "start",
            sortable: true,
            key: "item_name",
            width: "12%",
          },
          {
            title: "Qty",
            key: "qty",
            align: "center",
            width: "11%",
          },
          {
            title: "Uom",
            key: "uom",
            align: "center",
            width: "10%",
          },
          {
            title: "list_price",
            key: "price_list_rate",
            align: "center",
            width: "12%",
          },
          {
            title: "dis_price",
            key: "rate",
            align: "center",
            width: "12%",
          },
          {
            title: "dis_%",
            key: "discount_percentage",
            align: "center",
            width: "13%",
          },
          {
            title: "dis_amount",
            key: "discount_amount",
            align: "center",
            width: "12%",
          },
          {
            title: "Total",
            key: "amount",
            align: "center",
            width: "13%",
          },
          {
            title: "Delete",
            key: "actions",
            align: "end",
            sortable: false,
            width: "5%",
          },
        ],
      };
    },
  
    // ===== COMPUTED =====
    computed: {
      dynamicHeaders() {
        let headers = [...this.items_headers];
  
        if (!this.pos_profile?.posa_display_discount_percentage) {
          headers = headers.filter(
            (header) => header.key !== "discount_percentage"
          );
        }
  
        if (!this.pos_profile?.posa_display_discount_amount) {
          headers = headers.filter((header) => header.key !== "discount_amount");
        }
  
        if (!this.pos_profile?.posa_allow_user_to_edit_item_discount) {
          headers = headers.filter((header) => header.key !== "rate");
        }
  
        return headers;
      },
      readonly() {
        return this.invoice_doc?.is_return || false;
      },
      defaultPaymentMode() {
        const invoicePayments =
          this.invoice_doc && Array.isArray(this.invoice_doc?.payments)
            ? this.invoice_doc?.payments
            : [];
        const profilePayments =
          this.pos_profile && Array.isArray(this.pos_profile?.payments)
            ? this.pos_profile?.payments
            : [];
        const payments = invoicePayments.length
          ? invoicePayments
          : profilePayments;
  
        // First try to find a payment marked as default
        let defaultRow = payments.find((payment) => payment.default == 1);
  
        // If no default payment is found, use the first payment as default
        if (!defaultRow && payments.length > 0) {
          defaultRow = payments[0];
        }
  
        return defaultRow ? defaultRow.mode_of_payment : null;
      },
      canPrintInvoice() {
        if (this.readonly || !this.items?.length) return false;
        return this.hasValidPayments() || !!this.defaultPaymentMode;
      },
      hasItems() {
        return this.items && this.items.length > 0;
      },
      hasChosenPayment() {
        return this.hasValidPayments();
      },
    },
  
    methods: {
      onQtyChange(item) {
        const newQty = Number(item.qty) || 0;
        item.qty = newQty;
        item.amount = this.calculateItemAmount(item);
        this.debouncedItemOperation("qty-change");
      },
  
      onQtyInput(item) {
        // Handle input events - use same logic as onQtyChange but without debounce
        this.isUpdatingTotals = true; // تعيين حالة تحديث المجاميع إلى true
        this.onQtyChange(item);
      },
  
      increaseQuantity(item) {
        item.qty = (Number(item.qty) || 0) + 1;
        item.amount = this.calculateItemAmount(item);
        evntBus.emit("item_updated", item);
        this.isUpdatingTotals = true;
      },
  
      decreaseQuantity(item) {
        const newQty = Math.max(0, (Number(item.qty) || 0) - 1);
        if (newQty === 0) {
          this.remove_item(item);
        } else {
          item.qty = newQty;
          item.amount = this.calculateItemAmount(item);
          evntBus.emit("item_updated", item);
          this.isUpdatingTotals = true;
        }
      },
  
      getDiscountAmount(item) {
        if (!item) return 0;
        if (item.discount_amount) return flt(item.discount_amount) || 0;
  
        const basePrice = flt(item.price_list_rate) || flt(item.rate) || 0;
        const discountPercentage = flt(item.discount_percentage) || 0;
        return discountPercentage > 0 && basePrice > 0
          ? flt((basePrice * discountPercentage) / 100) || 0
          : 0;
      },
  
      quick_return() {
        if (
          !this.pos_profile?.posa_allow_quick_return ||
          !this.customer ||
          !this.items.length
        ) {
          return;
        }
        this.quick_return_value = !this.quick_return_value;
        evntBus.emit("toggle_quick_return", this.quick_return_value);
      },
  
      remove_item(item) {
        const index = this.items.findIndex(
          (el) => el.posa_row_id == item.posa_row_id
        );
        if (index >= 0) {
          this.items.splice(index, 1);
          if (this.items.length === 0 && this.invoice_doc?.name) {
            this.delete_draft_invoice();
          } else {
            evntBus.emit("item_removed", item);
          }
        }
      },
  
      async add_item(item) {
        if (!item?.item_code) return;
  
        const new_item = Object.assign({}, item);
        new_item.uom = new_item.uom || new_item.stock_uom || "Nos";
  
        const existing_item = this.items.find(
          (existing) =>
            existing.item_code === new_item.item_code &&
            existing.uom === new_item.uom
        );
  
        if (existing_item) {
          existing_item.qty = flt(existing_item.qty) + flt(new_item.qty);
          existing_item.amount = this.calculateItemAmount(existing_item);
          this.isUpdatingTotals = true;
        } else {
          new_item.posa_row_id = this.generateRowId();
          new_item.posa_offers = "[]";
          new_item.posa_offer_applied = 0;
          new_item.posa_is_offer = 0;
          new_item.posa_is_replace = 0;
          new_item.is_free_item = 0;
          new_item.amount = this.calculateItemAmount(new_item);
          this.items.push(new_item);
          this.isUpdatingTotals = true;
        }
  
        if (this.items.length === 1 && !this.invoice_doc?.name) {
          this.create_draft_invoice();
        } else {
          evntBus.emit("item_added", existing_item || new_item);
          if (existing_item) {
            this.isUpdatingTotals = true;
          }
        }
      },
      generateRowId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
      },
  
      calculateItemAmount(item) {
        return flt(item.rate * item.qty, this.currency_precision);
      },
  
      resetInvoiceState() {
        this.invoiceType = "Invoice";
        this.invoiceTypes = ["Invoice"];
        this.posting_date = frappe.datetime.nowdate();
        this.items = [];
        this.posa_offers = [];
        this.posa_coupons = [];
        this.discount_amount = 0;
        this.additional_discount_percentage = 0;
        evntBus.emit("update_invoice_type", this.invoiceType);
        evntBus.emit("set_pos_coupons", []);
        // Clear invoice doc display in navbar
        evntBus.emit("update_invoice_doc", null);
      },
  
      hasValidPayments(invoice_doc = null) {
        const doc = invoice_doc || this.invoice_doc;
        return doc?.payments?.some((p) => this.flt(p.amount) > 0) || false;
      },
  
      async create_draft_invoice() {
        try {
          const doc = this.get_invoice_doc("draft");
          const result = await this.create_invoice(doc);
  
          if (result) {
            this.invoice_doc = result;
            this.isUpdatingTotals = false;
          } else {
            this.invoice_doc = null;
            this.items = [];
            this.isUpdatingTotals = false;
          }
        } catch (error) {
          // Draft creation failed - continue with current state
          this.isUpdatingTotals = false;
        }
      },
      create_invoice(doc) {
        const vm = this;
        return new Promise((resolve, reject) => {
          frappe.call({
            method: API_MAP.SALES_INVOICE.CREATE,
            args: {
              data: doc,
            },
            async: true,
            callback: function (r) {
              console.log("API Response (Create Invoice):", r);
              if (r.message !== undefined) {
                if (r.message === null) {
                  vm.invoice_doc = null;
                  vm.items = [];
                  resolve(null);
                } else {
                  vm.invoice_doc = r.message;
  
                  // Emit event for navbar to update invoice display
                  evntBus.emit("update_invoice_doc", vm.invoice_doc);
  
                  // Update posa_offers from backend response
                  if (r.message.posa_offers) {
                    vm.posa_offers = r.message.posa_offers;
  
                    const appliedOffers = vm.posa_offers.filter(
                      (offer) => offer.offer_applied
                    );
                    if (appliedOffers.length > 0) {
                      evntBus.emit("update_pos_offers", appliedOffers);
                    }
                  }
                  vm._processOffers();
                  
                }
              } else {
                reject(new Error("Failed to create invoice"));
              }
            },
            error: function (err) {
              reject(err);
            },
          });
        });
      },
  
      async auto_update_invoice(doc = null, reason = "auto") {
        console.log("Auto-updating invoice, reason:", reason);
        console.log("Auto-updating invoice, doc:", doc);
        
        if (this.invoice_doc?.submitted_for_payment) {
          return;
        }
  
        if (!doc && this.items.length === 0 && !this.invoice_doc?.name) {
          return;
        }
  
        const payload = doc || this.get_invoice_doc(reason);
  
        try {
          let result;
  
          if (!this.invoice_doc?.name && this.items.length > 0) {
            result = await this.create_invoice(payload);
          } else if (this.invoice_doc?.name) {
            result = await this.update_invoice(payload);
          } else {
            return null;
          }
  
          if (!result) {
            this.invoice_doc = null;
            this.items = [];
            return null;
          }
  
          if (result && Array.isArray(result.items)) {
            // Set flag to prevent watcher loop
            this._updatingFromAPI = true;
  
            // Merge API items with local items
            this.mergeItemsFromAPI(result.items);
  
            // Reset flag after update
            this.$nextTick(() => {
              this._updatingFromAPI = false;
            });
          }
  
          // Always update invoice_doc with API response
          if (result) {
            if (result.name && !this.invoice_doc?.name) {
              evntBus.emit("show_mesage", {
                text: "Draft created",
                color: "success",
              });
            }
  
            // Update invoice_doc with latest totals from server
            this.invoice_doc = {
              ...this.invoice_doc,
              ...result,
              items:
                this.items.length > (result.items?.length || 0)
                  ? this.items
                  : result.items || [],
            };
          }
  
          this._updatingFromAPI = false;
          return result;
        } catch (error) {
          if (
            error?.message &&
            error.message.includes("Document has been modified")
          ) {
            try {
              await this.reload_invoice();
            } catch (reloadError) {
              // Invoice reload failed after conflict - continue with current data
            }
            return;
          }
  
          evntBus.emit("show_mesage", {
            text: "Auto-saving draft failed",
            color: "error",
          });
  
          this._updatingFromAPI = false;
          throw error;
        }
      },
  
      queue_auto_save(reason = "auto") {
        if (this.invoice_doc?.submitted_for_payment) {
          return Promise.resolve();
        }
  
        // Skip auto-save if no items and no invoice doc
        if (this.items.length === 0 && !this.invoice_doc?.name) {
          return Promise.resolve();
        }
  
        // Simple: just send update immediately
        const doc = this.get_invoice_doc(reason);
        return this.auto_update_invoice(doc, reason);
      },
  
      async reload_invoice() {
        if (this.invoice_doc && this.invoice_doc?.name) {
          try {
            const result = await frappe.call({
              method: "frappe.client.get",
              args: {
                doctype: "Sales Invoice",
                name: this.invoice_doc?.name,
              },
            });
  
            if (result.message) {
              this.invoice_doc = result.message;
              if (result.message.items) {
                this.items = result.message.items;
              }
            }
          } catch (error) {}
        }
      },
  
      debounced_auto_update(reason = "auto") {
        if (this._autoUpdateTimer) {
          clearTimeout(this._autoUpdateTimer);
        }
  
        this._autoUpdateTimer = setTimeout(() => {
          this.queue_auto_save(reason);
        }, 500);
      },
  
      cancel_invoice() {
        if (this.invoice_doc && this.invoice_doc?.name) {
          frappe.call({
            method: "frappe.client.delete",
            args: {
              doctype: "Sales Invoice",
              name: this.invoice_doc?.name,
            },
            callback: (r) => {
              if (r.message) {
                evntBus.emit("show_mesage", {
                  text: "Draft cancelled",
                  color: "success",
                });
              }
            },
          });
        }
  
        this.resetInvoiceState();
        this.customer = this.pos_profile?.customer;
        this.invoice_doc = "";
        this.return_doc = "";
        evntBus.emit("set_customer_readonly", false);
        evntBus.emit("show_payment", "false");
      },
  
      delete_draft_invoice() {
        const name = this.invoice_doc && this.invoice_doc?.name;
        const reset = () => {
          this.reset_invoice_session();
        };
  
        if (!name) {
          reset();
          return;
        }
  
        frappe
          .call({
            method: API_MAP.SALES_INVOICE.DELETE,
            args: { invoice_name: name },
          })
          .then(reset)
          .catch(reset);
      },
  
      reset_invoice_session() {
        this.resetInvoiceState();
        this.return_doc = null;
        this.invoice_doc = "";
        this.customer = this.pos_profile?.customer || this.customer;
        evntBus.emit("new_invoice", "false");
      },
  
      new_invoice(data = {}) {
        let old_invoice = null;
        evntBus.emit("set_customer_readonly", false);
        this.posa_offers = [];
        this.posa_coupons = [];
        this.return_doc = "";
        evntBus.emit("set_pos_coupons", []);
  
        const doc = this.get_invoice_doc();
        if (doc.name) {
          old_invoice = this.update_invoice(doc);
        } else {
          if (doc.items.length) {
            old_invoice = this.update_invoice(doc);
          }
        }
        if (!data.name && !data.is_return) {
          this.items = [];
          this.customer = this.pos_profile?.customer;
          this.invoice_doc = "";
          this.discount_amount = 0;
          this.additional_discount_percentage = 0;
          this.invoiceType = "Invoice";
          this.invoiceTypes = ["Invoice"];
          evntBus.emit("update_invoice_type", this.invoiceType);
        } else {
          if (data.is_return) {
            evntBus.emit("set_customer_readonly", true);
            this.invoiceType = "Return";
            this.invoiceTypes = ["Return"];
            evntBus.emit("update_invoice_type", this.invoiceType);
          }
          this.invoice_doc = data;
          this.items = data.items || [];
  
          // Update items with POS-specific fields if needed
          this.items.forEach((item) => {
            if (!item.posa_row_id) {
              item.posa_row_id = this.makeid(20);
            }
          });
          
          
          this.posa_offers = data.posa_offers || [];
          this.items.forEach((item) => {
            item.base_rate = item.base_rate || item.price_list_rate;
            if (!item.posa_row_id) {
              item.posa_row_id = this.makeid(20);
            }
            if (item.batch_no) {
              this.set_batch_qty(item, item.batch_no);
            }
          });
          this.setCustomer(data.customer);
          this.posting_date = data.posting_date || frappe.datetime.nowdate();
          this.discount_amount = data.discount_amount;
          
          this.additional_discount_percentage =
            data.additional_discount_percentage;
          this.items.forEach((item) => {
            if (item.serial_no) {
              item.serial_no_selected = [];
              const serial_list = item.serial_no.split("\n");
              serial_list.forEach((element) => {
                if (element.length) {
                  item.serial_no_selected.push(element);
                }
              });
              item.serial_no_selected_count = item.serial_no_selected.length;
            }
          });
        }
        return old_invoice;
      },
  
      get_invoice_doc(reason = "auto") {
        const isPaymentFlow = reason === "payment" || reason === "print";
        const doc = {};
  
        // Always create a new invoice if no invoice exists or if we have items but no invoice name
        if (
          this.invoice_doc &&
          this.invoice_doc?.name &&
          !this.invoice_doc?.submitted_for_payment
        ) {
          doc.name = this.invoice_doc?.name;
        } else if (this.items.length > 0) {
          // Create new invoice when we have items but no existing invoice
        }
  
        doc.doctype = "Sales Invoice";
        doc.is_pos = 1;
        doc.ignore_pricing_rule = 1;
        doc.company = this.pos_profile?.company;
        doc.pos_profile = this.pos_profile?.name;
        doc.currency = this.pos_profile?.currency;
        doc.naming_series = this.pos_profile?.naming_series;
        doc.customer = this.customer;
        doc.posting_date = this.posting_date;
        doc.posa_pos_opening_shift = this.pos_opening_shift
          ? this.pos_opening_shift.name
          : null;
  
        doc.items = this.get_invoice_items_minimal();
  
        doc.discount_amount = flt(this.discount_amount);
        doc.additional_discount_percentage = flt(
          this.additional_discount_percentage
        );
  
        if (isPaymentFlow) {
          doc.payments = this.get_payments();
        }
  
        if (this.invoice_doc) {
          doc.is_return = this.invoice_doc?.is_return;
          doc.return_against = this.invoice_doc?.return_against;
        }
  
        return doc;
      },
  
      get_invoice_items_minimal() {
        return this.items.map((item) => ({
          item_code: item.item_code,
          qty: item.qty || 1,
          rate: item.rate || item.price_list_rate || 0,
          price_list_rate: item.price_list_rate || 0, // MUST send this so ERPNext can calculate discount_amount
          uom: item.uom || item.stock_uom,
          serial_no: item.serial_no,
          discount_percentage: item.discount_percentage || 0,
          // Don't send discount_amount - let ERPNext calculate it from price_list_rate + discount_percentage
          batch_no: item.batch_no,
        }));
      },
  
      get_payments() {
        let payments = [];
  
        // إذا كانت هناك مدفوعات موجودة في الفاتورة الحالية
        if (
          this.invoice_doc &&
          Array.isArray(this.invoice_doc?.payments) &&
          this.invoice_doc?.payments.length
        ) {
          payments = this.invoice_doc.payments.map((p) => ({
            amount: this.flt(p.amount),
            mode_of_payment: p.mode_of_payment,
            default: p.default,
            account: p.account || "",
            idx: p.idx,
          }));
        } else if (
          this.pos_profile &&
          Array.isArray(this.pos_profile?.payments)
        ) {
          let hasDefault = false;
  
          this.pos_profile?.payments.forEach((payment, index) => {
            if (payment.default) hasDefault = true;
            payments.push({
              amount: 0,
              mode_of_payment: payment.mode_of_payment,
              default: payment.default,
              account: payment.account || "",
              idx: index + 1,
            });
          });
  
          if (!hasDefault && payments.length > 0) payments[0].default = 1;
        }
  
        // --- إضافة معالجة التقريب ---
        const totalTarget = this.rounded_total || this.grand_total;
        let totalPayments = payments.reduce((sum, p) => sum + p.amount, 0);
        let diff = totalPayments - totalTarget;
  
        if (
          Math.abs(diff) >= 0.01 &&
          Math.abs(diff) <= 1.0 &&
          payments.length > 0
        ) {
          payments[0].amount = this.flt(payments[0].amount - diff);
        }
  
        return payments;
      },
  
      update_invoice(doc) {
        const vm = this;
        return new Promise((resolve, reject) => {
          // Ensure we have an invoice name for updates
          if (!doc.name) {
            reject(new Error("Invoice name required for updates"));
            return;
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
                  vm.invoice_doc = null;
                  vm.items = [];
                  resolve(null);
                } else {
                  vm.invoice_doc = r.message;
                  
                  // Update posa_offers from backend response
                  if (r.message.posa_offers) {
                    vm.posa_offers = r.message.posa_offers;
                    
                    // Handle Transaction-level Percentage Discount Offers
                    let transactionDiscount = 0;
                    const appliedTransactionOffer = vm.posa_offers.find(
                        (offer) => offer.offer_applied 
                    );
                    
                    if (appliedTransactionOffer) {
                        transactionDiscount = flt(appliedTransactionOffer.discount_percentage);
                        vm.additional_discount_percentage = transactionDiscount;
                        // Store the origin of the discount
                        vm.offer_discount_percentage = transactionDiscount; 
                      
                        
                    } else if (vm.offer_discount_percentage > 0) {
                        // If the offer was applied but is now removed, clear it.
                        vm.offer_discount_percentage = 0;
                    }

                    
                    // Emit event for navbar to update invoice display
                    evntBus.emit("update_invoice_doc", vm.invoice_doc);
  
                    const appliedOffers = vm.posa_offers.filter(
                      (offer) => offer.offer_applied
                    );
                    
                    if (appliedOffers.length > 0) {
                      evntBus.emit("update_pos_offers", appliedOffers);
                    }
                  }
  
                  resolve(vm.invoice_doc);
                }
              } else {
                reject(new Error("Failed to update invoice"));
              }
            },
            error: function (err) {
              if (
                err.message &&
                err.message.includes("Document has been modified")
              ) {
                vm.reload_invoice()
                  .then(() => resolve(vm.invoice_doc))
                  .catch((reloadError) => reject(reloadError));
              } else {
                reject(err);
              }
            },
          });
        });
      },
  
      async process_invoice() {
        const doc = this.get_invoice_doc("payment");
  
        try {
          const result = await this.update_invoice(doc);
          return result;
        } catch (error) {
          evntBus.emit("show_mesage", {
            text: "Processing failed",
            color: "error",
          });
          throw error;
        }
      },
  
      async show_payment() {
        if (this.readonly) return;
  
        evntBus.emit("show_loading", { text: "Loading...", color: "info" });
  
        try {
          const invoice_doc = await this.process_invoice();
  
          // Add default payment method if no payments exist
          if (!invoice_doc?.payments || invoice_doc?.payments.length === 0) {
            // Adding default payment
            try {
              const defaultPayment = await frappe.call({
                method: API_MAP.POS_PROFILE.GET_DEFAULT_PAYMENT,
                args: {
                  pos_profile: this.pos_profile?.name,
                  company:
                    this.pos_profile?.company ||
                    frappe.defaults.get_user_default("Company"),
                },
              });
  
              if (defaultPayment.message) {
                invoice_doc.payments = [
                  {
                    mode_of_payment: defaultPayment.message.mode_of_payment,
                    amount: flt(invoice_doc?.grand_total),
                    account: defaultPayment.message.account,
                    default: 1,
                  },
                ];
                // Default payment added
  
                // Save default payment to server
                try {
                  await frappe.call({
                    method: API_MAP.SALES_INVOICE.UPDATE,
                    args: {
                      invoice_data: invoice_doc,
                    },
                  });
                  // Default payment saved
                } catch (error) {
                  // Payment save failed
                }
              }
            } catch (error) {
              // Payment get failed
            }
          }
  
          evntBus.emit("send_invoice_doc_payment", invoice_doc);
          evntBus.emit("show_payment", "true");
  
          this.posa_offers = [];
          this.posa_coupons = [];
  
          if (this.pos_profile?.posa_clear_customer_after_payment) {
            this.setCustomer(this.pos_profile?.customer);
          }
  
          evntBus.emit("invoice_session_reset");
          evntBus.emit("hide_loading");
        } catch (error) {
          evntBus.emit("hide_loading");
          evntBus.emit("show_mesage", {
            text: "Error preparing invoice: " + error.message,
            color: "error",
          });
        }
      },
  
      open_returns() {
        if (!this.pos_profile?.posa_allow_return) return;
  
        evntBus.emit("open_returns", {
          pos_profile: this.pos_profile,
          pos_opening_shift: this.pos_opening_shift || null,
        });
      },
  
      close_payments() {
        evntBus.emit("show_payment", "false");
      },
  
      setCustomer(customer) {
        this.customer = customer;
        this.close_payments();
        evntBus.emit("set_customer", this.customer);
        if (this.invoice_doc) {
          this.invoice_doc.contact_person = "";
          this.invoice_doc.contact_email = "";
          this.invoice_doc.contact_mobile = "";
        }
        this.fetch_customer_details();
      },
  
      fetch_customer_details() {
        const vm = this;
        if (this.customer) {
          frappe.call({
            method: API_MAP.CUSTOMER.GET_CUSTOMER,
            args: {
              customer_id: vm.customer,
            },
            async: false,
            callback: (r) => {
              const message = r.message;
              if (!r.exc) {
                vm.customer_info = {
                  ...message,
                };
                evntBus.emit("set_customer_info_to_edit", vm.customer_info);
              }
              vm.update_price_list();
            },
          });
        }
      },
  
      get_price_list() {
        let price_list = this.pos_profile?.selling_price_list;
        if (this.customer_info && this.pos_profile) {
          const { customer_price_list, customer_group_price_list } =
            this.customer_info;
          const pos_price_list = this.pos_profile?.selling_price_list;
          if (customer_price_list && customer_price_list != pos_price_list) {
            price_list = customer_price_list;
          } else if (
            customer_group_price_list &&
            customer_group_price_list != pos_price_list
          ) {
            price_list = customer_group_price_list;
          }
        }
        return price_list;
      },
  
      setDiscountPercentage(item, event) {
        
        let dis_percent = parseFloat(event.target.value) || 0;
  
        // Apply max discount limit
        const maxDiscount =
          this.pos_profile?.posa_item_max_discount_allowed || 100;
  
        if (dis_percent < 0) dis_percent = 0;
        if (dis_percent > maxDiscount) {
          dis_percent = maxDiscount;
          evntBus.emit("show_mesage", {
            text: `Maximum discount applied: ${maxDiscount}%`,
            color: "info",
          });
        }
  
        item.discount_percentage = dis_percent;
  
        const list_price = flt(item.price_list_rate) || 0;
        if (list_price > 0) {
          if (dis_percent > 0) {
            const dis_amount = (list_price * dis_percent) / 100;
            item.rate = flt(list_price - dis_amount, this.currency_precision); // dis_price
          } else {
            item.rate = list_price; // dis_price = list_price when no discount
          }
          // Calculate total amount
          item.amount = this.calculateItemAmount(item);
        }
  
        this.debouncedItemOperation("discount-change");
      },
  
      setItemRate(item, event) {
        let dis_price = parseFloat(event.target.value) || 0;
        const list_price = flt(item.price_list_rate) || 0;
  
        if (dis_price < 0) dis_price = 0;
  
        // Don't allow dis_price higher than list_price
        if (dis_price > list_price) {
          dis_price = list_price;
          evntBus.emit("show_mesage", {
            text: "Price exceeds limit",
            color: "error",
          });
        }
  
        // Calculate dis_% from price difference
        let dis_percent = 0;
        if (list_price > 0) {
          dis_percent = ((list_price - dis_price) / list_price) * 100;
        }
  
        // Apply max discount limit
        const maxDiscount =
          this.pos_profile?.posa_item_max_discount_allowed || 100;
  
        if (dis_percent > maxDiscount) {
          // Adjust dis_price to respect max discount
          const max_dis_amount = (list_price * maxDiscount) / 100;
          dis_price = flt(list_price - max_dis_amount, this.currency_precision);
          dis_percent = maxDiscount;
  
          evntBus.emit("show_mesage", {
            text: `Maximum discount applied: ${maxDiscount}%`,
            color: "info",
          });
        }
  
        item.rate = dis_price;
        item.discount_percentage = flt(dis_percent, 2);
        item.amount = this.calculateItemAmount(item);
  
        this.debouncedItemOperation("rate-change");
      },
  
      update_price_list() {
        let price_list = this.get_price_list();
        if (price_list == this.pos_profile?.selling_price_list) {
          price_list = null;
        }
        evntBus.emit("update_customer_price_list", price_list);
      },
  
      update_discount_umount() {
        
        // Simplified: just validate and set, server will recalculate
        if (!this.pos_profile?.posa_allow_user_to_edit_additional_discount) {
          this.additional_discount_percentage =
            this.invoice_doc?.additional_discount_percentage || 0;
          return;
        }
  
        const value = flt(this.additional_discount_percentage) || 0;
        const maxDiscount =
          this.pos_profile?.posa_invoice_max_discount_allowed || 100;
  
        if (value < 0) {
          this.additional_discount_percentage = 0;
        } else if (value > maxDiscount) {
          this.additional_discount_percentage = maxDiscount;
          evntBus.emit("show_mesage", {
            text: `Maximum invoice discount is ${maxDiscount}%`,
            color: "info",
          });
        }
  
        this.debouncedItemOperation("invoice-discount-change");
      },
  
      set_serial_no(item) {
        if (!item.has_serial_no) return;
        item.serial_no = "";
        item.serial_no_selected.forEach((element) => {
          item.serial_no += element + "\n";
        });
        item.serial_no_selected_count = item.serial_no_selected.length;
        if (item.serial_no_selected_count != item.stock_qty) {
          item.qty = item.serial_no_selected_count;
          // Vue 3 reactive update - no need for $set
          this.$forceUpdate();
        }
      },
  
      set_batch_qty(item, value, update = true) {
        if (!item.batch_no_data || !Array.isArray(item.batch_no_data)) {
          return;
        }
  
        const vm = this;
        frappe.call({
          method: API_MAP.ITEM.PROCESS_BATCH_SELECTION,
          args: {
            item_code: item.item_code,
            current_item_row_id: item.posa_row_id,
            existing_items_data: this.items,
            batch_no_data: item.batch_no_data,
            preferred_batch_no: value || null,
          },
          async: false,
          callback: function (r) {
            if (r.message && r.message.success) {
              const result = r.message;
              const selectedBatch = result.selected_batch;
  
              item.batch_no = selectedBatch.batch_no;
              item.actual_batch_qty = selectedBatch.actual_batch_qty;
              item.batch_no_expiry_date = selectedBatch.expiry_date;
              item.batch_no_data = result.batch_data;
  
              if (selectedBatch.batch_price) {
                item.batch_price = selectedBatch.batch_price;
                item.price_list_rate = selectedBatch.batch_price;
                item.rate = selectedBatch.batch_price;
              } else if (update) {
                item.batch_price = null;
                vm.update_item_detail(item);
              }
  
              // Trigger reactivity without full re-render
              vm.$nextTick();
            } else {
              item.batch_no = null;
              item.actual_batch_qty = null;
              item.batch_no_expiry_date = null;
              item.batch_price = null;
              item.batch_no_data = r.message?.batch_data || [];
  
              if (r.message?.message) {
                evntBus.emit("show_mesage", {
                  text: r.message.message,
                  color: "warning",
                });
              }
  
              // Use nextTick instead of forceUpdate
              vm.$nextTick();
            }
          },
          error: function (err) {
            evntBus.emit("show_mesage", {
              text: "خطأ في اختيار الباتش: " + (err.message || "خطأ غير معروف"),
              color: "error",
            });
          },
        });
      },
  
      shortOpenPayment(e) {
        if (e.key === "s" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          this.show_payment();
        }
      },
  
      shortDeleteFirstItem(e) {
        if (e.key === "d" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          this.remove_item(this.items[0]);
        }
      },
  
      shortOpenFirstItem(e) {
        if (e.key === "a" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          this.expanded = [];
          this.expanded.push(this.items[0]);
        }
      },
  
      shortSelectDiscount(e) {
        if (e.key === "z" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          this.$refs.discount.focus();
        }
      },
  
      makeid(length) {
        return crypto.randomUUID
          ? crypto.randomUUID().substring(0, length)
          : Math.random()
              .toString(36)
              .substring(2, 2 + length);
      },
  
      checkOfferIsAppley(item, offer) {
        
        let applied = false;
  
        // Handle null or undefined posa_offers
        if (!item.posa_offers) {
          return false;
        }
  
        try {
          const item_offers = JSON.parse(item.posa_offers);
          if (!Array.isArray(item_offers)) {
            return false;
          }
  
          for (const row_id of item_offers) {
            const exist_offer = this.posa_offers.find(
              (el) => row_id == el.row_id
            );
            if (exist_offer && exist_offer.offer_name == offer.name) {
              applied = true;
              break;
            }
          }
        } catch (error) {
          return false;
        }
  
        return applied;
      },
  
      mergeItemsFromAPI(apiItems) {
        // Preserve price_list_rate and other display fields when merging API response
        if (apiItems && Array.isArray(apiItems) && apiItems.length > 0) {
          // Create a simple map by item_code (since item_code never repeats in invoice)
          const localItemsByCode = new Map();
  
          this.items.forEach((item) => {
            localItemsByCode.set(item.item_code, item);
          });
  
          // Merge API items with local items, preserving price_list_rate
          this.items = apiItems.map((apiItem) => {
            // Find local item by item_code (simple & reliable)
            const localItem = localItemsByCode.get(apiItem.item_code);
  
            // If local item exists, preserve price_list_rate from it
            if (localItem?.price_list_rate && !apiItem.price_list_rate) {
              apiItem.price_list_rate = localItem.price_list_rate;
            }
  
            // Also preserve base_rate if needed
            if (localItem?.base_rate && !apiItem.base_rate) {
              apiItem.base_rate = localItem.base_rate;
            }
  
            // Preserve posa_row_id from local if API doesn't have it
            if (localItem?.posa_row_id && !apiItem.posa_row_id) {
              apiItem.posa_row_id = localItem.posa_row_id;
            }
  
            return apiItem;
          });
        }
      },
  
      debouncedItemOperation(operation = "item-operation") {
        // Clear existing timer
        if (this._itemOperationTimer) {
          clearTimeout(this._itemOperationTimer);
        }
  
        // Wait 1 second after user stops, then send update
        this._itemOperationTimer = setTimeout(() => {
          this.sendInvoiceUpdate();
        }, 1000); // 1 second delay
      },
  
      sendInvoiceUpdate() {
        if (!this.invoice_doc?.name) return;
  
        // Sending update to server
  
        const doc = this.get_invoice_doc("item-update");
  
        this.auto_update_invoice(doc, "item-update")
          .then(() => {
            this.isUpdatingTotals = false;
          })
          .catch((error) => {
            this.isUpdatingTotals = false;
          });
      },
  
      handleOffers() {
      console.log("Handling offers for invoice:", this.invoice_doc?.name, "with items:", this.items);
      
        if (this.invoice_doc?.name && this.items && this.items.length > 1) {
          this._processOffers();
        }
      },
  
      _processOffers() {
        if (!this.invoice_doc?.name) return;
  
        // Skip offers processing if no items or only one item
        if (!this.items || this.items.length <= 1) {
          return;
        }
  
        // Check cache first (cache for 30 seconds)
        const cacheKey = `${this.invoice_doc?.name}_${this.items.length}`;
        const now = Date.now();
  
        if (
          this._offersCache &&
          this._offersCache.key === cacheKey &&
          now - this._offersCache.timestamp < 30000
        ) {
          // Using cached offers
          this.updatePosOffers(this._offersCache.data);
          return;
        }
  
        // Prevent multiple simultaneous calls
        if (this._offersProcessing) {
          // Already processing offers
          return;
        }
  
        this._offersProcessing = true;
  
        frappe.call({
          method: API_MAP.POS_OFFER.GET_APPLICABLE_OFFERS,
          args: {
            invoice_name: this.invoice_doc?.name,
          },
          callback: (r) => {
            this._offersProcessing = false;
  
            if (r.message) {
              // Cache the results
              this._offersCache = {
                key: cacheKey,
                data: r.message,
                timestamp: now,
              };
  
              this.updatePosOffers(r.message);
            }
          },
          error: (r) => {
            this._offersProcessing = false;
          },
        });
      },
  
      getItemFromRowID(row_id) {
        const item = this.items.find((el) => el.posa_row_id == row_id);
        return item;
      },
  
      checkOfferCoupon(offer) {
        if (!offer.coupon_based) {
          offer.coupon = null;
          return true;
        }
  
        if (!this._couponCache) {
          this._couponCache = new Map();
          this.posa_coupons.forEach((coupon) => {
            this._couponCache.set(coupon.pos_offer, coupon.coupon);
          });
        }
  
        const coupon = this._couponCache.get(offer.name);
        if (coupon) {
          offer.coupon = coupon;
          return true;
        }
  
        return false;
      },
  
      getItemOffer(offer) {
        // Deprecated: item-level offer processing is handled server-side automatically
        return null;
      },
  
      updatePosOffers(offers) {
        
        evntBus.emit("update_pos_offers", offers);
      },
  
      updateInvoiceOffers(offers) {
        
        this.posa_offers = offers || [];
      },
  
      removeApplyOffer(invoiceOffer) {
        
        const index = this.posa_offers.findIndex(
          (el) => el.row_id === invoiceOffer.row_id
        );
        if (index > -1) {
          this.posa_offers.splice(index, 1);
        }
      },
  
      applyNewOffer(offer) {
        
        const newOffer = {
          offer_name: offer.name,
          row_id: offer.row_id,
          apply_on: offer.apply_on,
          offer: offer.offer,
          items: JSON.stringify(offer.items),
          give_item: offer.give_item,
          give_item_row_id: offer.give_item_row_id,
          offer_applied: offer.offer_applied,
          coupon_based: offer.coupon_based,
          coupon: offer.coupon,
        };
        this.posa_offers.push(newOffer);
      },
  
      printInvoice() {
        if (!this.invoice_doc || !this.defaultPaymentMode) return;
  
        evntBus.emit("show_loading", { text: "Processing...", color: "info" });
  
        this.process_invoice()
          .then((invoice_doc) => {
            if (!this.hasValidPayments(invoice_doc)) {
              evntBus.emit("show_payment", "true");
              evntBus.emit("hide_loading");
              return;
            }
  
            // Use Frappe's built-in submit
            frappe.call({
              method: "frappe.client.submit",
              args: {
                doc: invoice_doc,
              },
              callback: (r) => {
                evntBus.emit("hide_loading");
  
                if (r.message?.name) {
                  const print_format = this.pos_profile?.print_format;
  
                  // Open print window directly
                  const print_url = frappe.urllib.get_full_url(
                    `/printview?doctype=Sales%20Invoice&name=${r.message.name}&format=${print_format}&trigger_print=1&no_letterhead=0`
                  );
  
                  window.open(print_url);
  
                  evntBus.emit("set_last_invoice", r.message.name);
                  evntBus.emit("show_mesage", {
                    text: `Invoice ${r.message.name} submitted`,
                    color: "success",
                  });

                  this.resetInvoiceState();
                  this.invoice_doc = null;
                  evntBus.emit("new_invoice", "false");
                  evntBus.emit("invoice_submitted");
                } else {
                  evntBus.emit("show_mesage", {
                    text: "Submit failed",
                    color: "error",
                  });
                }
              },
              error: (err) => {
                evntBus.emit("hide_loading");
                evntBus.emit("show_mesage", {
                  text: err?.message || "Failed to submit",
                  color: "error",
                });
              },
            });
          })
          .catch((error) => {
            evntBus.emit("hide_loading");
            evntBus.emit("show_mesage", {
              text: "Failed to prepare invoice: " + error.message,
              color: "error",
            });
          });
      },
  
      update_item_detail(item) {
        // Update item details from allItems data when customer changes
        if (!item || !item.item_code || !this.allItems) {
          return;
        }
  
        try {
          // Find updated item data from allItems
          const updatedItem = this.allItems.find(
            (allItem) => allItem.item_code === item.item_code
          );
  
          if (updatedItem) {
            // Update relevant fields while preserving POS-specific data
            const fieldsToUpdate = [
              "price_list_rate",
              "rate",
              "base_rate",
              "currency",
              "actual_qty",
              "item_name",
              "stock_uom",
              "item_group",
              "serial_no_data",
              "batch_no_data",
              "item_uoms",
            ];
  
            fieldsToUpdate.forEach((field) => {
              if (updatedItem.hasOwnProperty(field)) {
                item[field] = updatedItem[field];
              }
            });
  
            // Mark as detail synced to avoid repeated updates
            item._detailSynced = true;
          }
        } catch (error) {
          // Item detail update failed - continue with current data
        }
      },
    },
  
    created() {
      // Register event listeners in created() to avoid duplicate registrations
      
      evntBus.on("register_pos_profile", (data) => {
        this.pos_profile = data.pos_profile;
        this.setCustomer(data.pos_profile?.customer);
        this.pos_opening_shift = data.pos_opening_shift;
        this.stock_settings = data.stock_settings;
        this.float_precision =
          frappe.defaults.get_default("float_precision") || 2;
        this.currency_precision =
          frappe.defaults.get_default("currency_precision") || 2;
        this.invoiceType = "Invoice";
        evntBus.emit("update_invoice_type", this.invoiceType);
      });
      evntBus.on("add_item", (item) => {
        this.add_item(item);
      });
      evntBus.on("update_customer", (customer) => {
        this.setCustomer(customer);
      });
      evntBus.on("fetch_customer_details", () => {
        this.fetch_customer_details();
      });
      evntBus.on("new_invoice", () => {
        this.invoice_doc = "";
        this.cancel_invoice();
      });
      evntBus.on("load_invoice", (data) => {
        
        this.new_invoice(data);
  
        if (this.invoice_doc?.is_return) {
          this.discount_amount = -data.discount_amount;
          this.additional_discount_percentage =
            -data.additional_discount_percentage;
          this.return_doc = data;
        } else {
          evntBus.emit("set_pos_coupons", data.posa_coupons);
        }
      });
  
      evntBus.on("set_offers", (data) => {
        console.log("check offere data ", data);
        
        this.posOffers = data;
      });
      evntBus.on("update_invoice_offers", (data) => {
        
        this.updateInvoiceOffers(data);
      });
      evntBus.on("update_invoice_coupons", (data) => {
        this.posa_coupons = data;
        this.debouncedItemOperation();
      });
      evntBus.on("set_all_items", (data) => {
        this.allItems = data;
        this.items.forEach((item) => {
          this.update_item_detail(item);
        });
      });
      evntBus.on("load_return_invoice", (data) => {
        this.new_invoice(data.invoice_doc);
  
        // Handle return_doc data only if it exists (for returns against specific invoices)
        if (data.return_doc) {
          this.discount_amount = -data.return_doc.discount_amount || 0;
          this.additional_discount_percentage =
            -data.return_doc.additional_discount_percentage || 0;
          this.return_doc = data.return_doc;
        } else {
          // Free return without reference invoice
          this.discount_amount = 0;
          this.additional_discount_percentage = 0;
          this.return_doc = null;
        }
  
        // Force update to ensure computed properties are recalculated
        this.$nextTick(() => {
          this.$forceUpdate();
        });
      });
  
      // Event-driven approach for items changes
      evntBus.on("item_added", (item) => {
        // Item added event
        this.debouncedItemOperation("item-added");
      });
  
      evntBus.on("item_removed", (item) => {
        // Item removed event
        this.debouncedItemOperation("item-removed");
      });
  
      evntBus.on("item_updated", (item) => {
        // Item updated event
        this.debouncedItemOperation("item-updated");
      });
  
      this.$nextTick(() => {
        // Component mounted
      });
      evntBus.on("send_invoice_doc_payment", (doc) => {
        this.invoice_doc = doc;
      });
      evntBus.on("payments_updated", (payments) => {
        if (this.invoice_doc) {
          this.invoice_doc.payments = payments || [];
          this.$forceUpdate();
        }
      });
      evntBus.on("request_invoice_print", () => {
        if (!this.canPrintInvoice()) {
          evntBus.emit("show_mesage", {
            text: "Please select a payment method before printing",
            color: "warning",
          });
          return;
        }
        this.printInvoice();
      });
    },
    mounted() {
      // DOM-related initialization (keyboard shortcuts)
      
      // Store bound function references so we can remove them later
      this._boundShortOpenPayment = this.shortOpenPayment.bind(this);
      this._boundShortDeleteFirstItem = this.shortDeleteFirstItem.bind(this);
      this._boundShortOpenFirstItem = this.shortOpenFirstItem.bind(this);
      this._boundShortSelectDiscount = this.shortSelectDiscount.bind(this);
      
      // Add event listeners with stored bound functions
      document.addEventListener("keydown", this._boundShortOpenPayment);
      document.addEventListener("keydown", this._boundShortDeleteFirstItem);
      document.addEventListener("keydown", this._boundShortOpenFirstItem);
      document.addEventListener("keydown", this._boundShortSelectDiscount);
    },
    beforeUnmount() {
      // Clean up ALL event listeners to prevent memory leaks
      
      // Clean up document event listeners using stored bound functions
      document.removeEventListener("keydown", this._boundShortOpenPayment);
      document.removeEventListener("keydown", this._boundShortDeleteFirstItem);
      document.removeEventListener("keydown", this._boundShortOpenFirstItem);
      document.removeEventListener("keydown", this._boundShortSelectDiscount);
      
      // Clean up event bus listeners
      evntBus.off("register_pos_profile");
      evntBus.off("add_item");
      evntBus.off("update_customer");
      evntBus.off("fetch_customer_details");
      evntBus.off("new_invoice");
      evntBus.off("load_invoice");
      evntBus.off("set_offers");
      evntBus.off("update_invoice_offers");
      evntBus.off("update_invoice_coupons");
      evntBus.off("set_all_items");
      evntBus.off("load_return_invoice");
      evntBus.off("item_added");
      evntBus.off("item_removed");
      evntBus.off("item_updated");
      evntBus.off("send_invoice_doc_payment");
      evntBus.off("payments_updated");
      evntBus.off("request_invoice_print");

      // Clear ALL timers to prevent memory leaks
      if (this._itemOperationTimer) {
        clearTimeout(this._itemOperationTimer);
        this._itemOperationTimer = null;
      }
      if (this._autoUpdateTimer) {
        clearTimeout(this._autoUpdateTimer);
        this._autoUpdateTimer = null;
      }
    },
    // ===== SECTION 6: WATCH =====
    watch: {
      discount_amount() {
        if (this.invoice_doc && this.invoice_doc?.name) {
          this.debouncedItemOperation("discount-amount-change");
        }
      },
      offerApplied: {
        handler(newVal, oldVal) {
          if (newVal && newVal.discount_percentage) {
            
            // Update both discount fields
            this.additional_discount_percentage = parseFloat(newVal.discount_percentage);
            this.offer_discount_percentage = parseFloat(newVal.discount_percentage);
            
            // Trigger backend sync
            this.$nextTick(() => {
              this.update_discount_umount();
            });
          } else if (newVal === null && oldVal !== null) {
            // Offer was reset to null (preparing for new application)
          }
        },
        deep: true,
        immediate: false
      },
      offerRemoved: {
        handler(newVal) {
          if (newVal === true) {
            // Reset discount fields
            this.additional_discount_percentage = 0;
            this.offer_discount_percentage = 0;
            
            // Trigger backend sync
            this.$nextTick(() => {
              this.update_discount_umount();
            });
          }
        },
        immediate: false
      },
    },
  };
  </script>
  
  <style scoped>
  /* .border_line_bottom {
    border-bottom: 1px solid lightgray;
  } */
  
  .disable-events {
    pointer-events: none;
  }
  
  /* ===== COMPACT CUSTOMER SECTION ===== */
  .compact-customer-section {
    padding: 4px 6px;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 0;
  }
  
  /* Old customer container - keep for compatibility */
  .customer-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-top: 10px;
  }
  
  /* Invoice number display styling */
  .invoice-number-display {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: #f5f5f5;
    height: 100%;
    min-height: 56px;
    font-size: 14px;
  }
  
  .invoice-number-text {
    flex: 1;
    font-weight: bold;
    line-height: 1.2;
  }
  
  /* Regular invoice styling - dark blue */
  .regular-invoice .invoice-number-text {
    color: #1976d2 !important;
    font-weight: bold !important;
  }
  
  /* Return invoice styling - dark red */
  .return-invoice .invoice-number-text {
    color: #d32f2f !important;
    font-weight: bold !important;
  }
  
  /* No invoice styling - italic gray */
  .no-invoice .invoice-number-text {
    color: #757575 !important;
    font-weight: normal !important;
    font-style: italic !important;
  }
  
  /* Global compact styling to match 75% zoom appearance */
  .v-application {
    font-size: 0.75rem !important;
  }
  
  .v-btn {
    font-size: 0.7rem !important;
    padding: 4px 8px !important;
    min-height: 24px !important;
  }
  
  .v-text-field {
    font-size: 0.7rem !important;
  }
  
  .v-text-field .v-field {
    min-height: 28px !important;
  }
  
  .v-text-field .v-field__input {
    padding: 4px 8px !important;
    font-size: 0.7rem !important;
  }
  
  .v-data-table {
    font-size: 0.7rem !important;
    overflow: auto !important;
  }
  
  .v-data-table .v-data-table__wrapper table {
    font-size: 0.75rem !important;
  }
  
  /* Consistent table formatting */
  .v-data-table .v-data-table__wrapper table th,
  .v-data-table .v-data-table__wrapper table td {
    padding: 4px 6px !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    line-height: 1.2 !important;
  }
  
  .v-data-table .v-data-table__wrapper table th {
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    background-color: #f5f5f5 !important;
    height: 28px !important;
  }
  
  /* RTL text direction for item name column */
  .v-data-table .v-data-table__wrapper table th:last-child,
  .v-data-table .v-data-table__wrapper table td:last-child {
    text-align: right !important;
    direction: rtl !important;
  }
  
  /* ===== PROFESSIONAL COMPACT TABLE DESIGN ===== */
  .invoice-items-scrollable {
    border-collapse: collapse;
    flex: 1 1 auto !important;
    max-height: calc(100vh - 170px) !important;
    overflow-y: auto !important;
    overflow-x: auto !important;
  }
  
  /* Ultra-compact table layout */
  .invoice-items-scrollable .v-data-table__wrapper table {
    table-layout: auto !important;
    width: 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    border-spacing: 0 !important;
    border-collapse: collapse !important;
    overflow: auto;
  }
  
  /* Zero spacing table cells with borders */
  .invoice-items-scrollable .v-data-table__wrapper table th,
  .invoice-items-scrollable .v-data-table__wrapper table td {
    white-space: normal !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    box-sizing: border-box !important;
    font-size: 0.7rem !important;
    margin: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    line-height: 1.1 !important;
    padding: 2px 4px !important;
    border-collapse: collapse !important;
  }
  
  /* Item name column takes remaining space */
  .invoice-items-scrollable .v-data-table__wrapper table th:last-child,
  .invoice-items-scrollable .v-data-table__wrapper table td:last-child {
    white-space: normal !important;
    word-wrap: break-word !important;
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    text-overflow: clip !important;
    overflow-wrap: break-word !important;
  }
  
  /* Completely remove scrollbars */
  .invoice-items-scrollable .v-data-table__wrapper {
    overflow-x: hidden !important;
    overflow-y: auto !important;
    width: 100% !important;
    max-width: 100% !important;
    max-height: calc(100vh - 170px) !important;
    box-sizing: border-box !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
  }
  
  /* Ultra-compact spacing - Professional */
  .invoice-items-scrollable .v-data-table__wrapper table {
    border-spacing: 0 !important;
    border-collapse: collapse !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    table-layout: auto !important;
  }
  
  .invoice-items-scrollable .v-data-table__wrapper table tr td,
  .invoice-items-scrollable .v-data-table__wrapper table tr th {
    margin: 0 !important;
    padding: 1px 1px !important;
    border: none !important;
    box-sizing: border-box !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    line-height: 1.1 !important;
  }
  
  /* Additional fixes for container distortion */
  .invoice-items-scrollable .v-data-table {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
    border: none !important;
    flex: 1 1 auto !important;
    display: flex !important;
    flex-direction: column !important;
    min-height: 0 !important;
    border: 1px solid #ccc !important;
  }
  
  /* Remove any borders from table wrapper only - NOT from cells */
  .invoice-items-scrollable .v-data-table,
  .invoice-items-scrollable .v-data-table__wrapper {
    border: none !important;
    outline: none !important;
  }
  
  .invoice-items-scrollable .v-data-table .v-data-table__wrapper {
    max-width: 100%px !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
  }
  
  /* Ensure proper column distribution */
  .invoice-items-scrollable .v-data-table__wrapper table colgroup col {
    width: auto !important;
  }
  
  /* Fix for item name column */
  .invoice-items-scrollable .v-data-table__wrapper table th:last-child,
  .invoice-items-scrollable .v-data-table__wrapper table td:last-child {
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    flex: 1 !important;
  }
  
  /* Compact Quantity Controls Container */
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
  
  .compact-qty-controls:hover {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    box-shadow: 0 1px 4px rgba(25, 118, 210, 0.2);
  }
  
  /* Compact Quantity Input */
  .compact-qty-input {
    flex: 1;
    width: 100%;
    min-width: 0;
    border: 1px solid #1976d2;
    background: white;
    outline: none;
    font-size: 0.75rem;
    font-weight: 700;
    color: #1976d2;
    text-align: center;
    padding: 2px 4px;
    border-radius: 3px;
    line-height: 1.2;
    height: 20px;
    appearance: textfield;
    -moz-appearance: textfield;
  }
  
  .compact-qty-input::-webkit-inner-spin-button,
  .compact-qty-input::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  
  .compact-qty-input:focus {
    border-color: #0d47a1;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.15);
    background: #e3f2fd;
  }
  
  .compact-qty-input:hover {
    border-color: #1565c0;
    background: #f5f5f5;
  }
  
  .compact-qty-input::placeholder {
    color: #bbb;
    font-weight: 400;
  }
  
  /* Compact Quantity Buttons */
  .qty-btn {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    min-width: 20px;
    padding: 0;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0;
    position: relative;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  }
  
  .qty-btn .btn-icon {
    font-size: 0.85rem;
    font-weight: 700;
    line-height: 1;
    display: block;
  }
  
  /* Minus Button - Orange/Warning */
  .qty-btn.minus-btn {
    background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
    color: white;
  }
  
  .qty-btn.minus-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #f57c00 0%, #e65100 100%);
    box-shadow: 0 2px 6px rgba(245, 124, 0, 0.4);
  }
  
  .qty-btn.minus-btn:active:not(:disabled) {
    box-shadow: 0 1px 2px rgba(245, 124, 0, 0.3);
  }
  
  .qty-btn.minus-btn:disabled {
    background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
    color: #9e9e9e;
    cursor: not-allowed;
    box-shadow: none;
    opacity: 0.6;
  }
  
  /* Plus Button - Green/Success */
  .qty-btn.plus-btn {
    background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
    color: white;
  }
  
  .qty-btn.plus-btn:hover {
    background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
    box-shadow: 0 2px 6px rgba(56, 142, 60, 0.4);
  }
  
  .qty-btn.plus-btn:active {
    box-shadow: 0 1px 2px rgba(56, 142, 60, 0.3);
  }
  
  /* Ultra-compact delete button */
  .delete-item-btn {
    width: 16px !important;
    height: 16px !important;
    min-width: 16px !important;
    min-height: 16px !important;
    line-height: 1 !important;
    padding: 0 !important;
    border-radius: 2px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
  }
  
  .delete-item-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: background 0.2s;
  }
  
  .delete-item-btn:hover:not(:disabled) {
    background: rgba(244, 67, 54, 0.1);
  }
  
  .delete-item-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .delete-item-btn .mdi {
    font-size: 12px;
    color: #f44336;
  }
  
  .error-btn-small {
    background: transparent;
    border: none;
    color: #f44336;
  }
  
  /* Compact Rate Input Field */
  .compact-rate-wrapper {
    display: flex;
    align-items: center;
    gap: 2px;
    padding: 2px 4px;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border: 1px solid #1976d2;
    border-radius: 4px;
    min-width: 70px;
    max-width: 90px;
  }
  
  .compact-rate-wrapper:hover {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-color: #1565c0;
    box-shadow: 0 1px 4px rgba(25, 118, 210, 0.2);
  }
  
  .compact-rate-wrapper:focus-within {
    border-color: #0d47a1;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.15);
    background: white;
  }
  
  .currency-prefix {
    font-size: 0.65rem;
    font-weight: 700;
    color: #1976d2;
    white-space: nowrap;
    flex-shrink: 0;
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
    line-height: 1.2;
  }
  
  .compact-rate-input:disabled {
    color: #999;
    cursor: not-allowed;
    opacity: 0.6;
  }
  
  .compact-rate-input::placeholder {
    color: #bbb;
    font-weight: 400;
  }
  
  /* Compact Discount Input Field */
  .compact-discount-wrapper {
    display: flex;
    align-items: center;
    gap: 2px;
    padding: 2px 4px;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border: 1px solid #1976d2;
    border-radius: 4px;
    min-width: 55px;
    max-width: 75px;
  }
  
  .compact-discount-wrapper.has-discount {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    border-color: #ff9800;
  }
  
  .compact-discount-wrapper:hover {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-color: #1565c0;
    box-shadow: 0 1px 4px rgba(25, 118, 210, 0.2);
  }
  
  .compact-discount-wrapper.has-discount:hover {
    background: linear-gradient(135deg, #ffe0b2 0%, #ffcc80 100%);
    border-color: #f57c00;
    box-shadow: 0 1px 4px rgba(255, 152, 0, 0.3);
  }
  
  .compact-discount-wrapper:focus-within {
    border-color: #0d47a1;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.15);
    background: white;
  }
  
  .compact-discount-wrapper.has-discount:focus-within {
    border-color: #e65100;
    box-shadow: 0 0 0 2px rgba(255, 152, 0, 0.15);
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
    line-height: 1.2;
    appearance: textfield;
    -moz-appearance: textfield;
  }
  
  .compact-discount-wrapper.has-discount .compact-discount-input {
    color: #f57c00;
    font-weight: 700;
  }
  
  .compact-discount-input::-webkit-inner-spin-button,
  .compact-discount-input::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  
  .compact-discount-input:disabled {
    color: #999;
    cursor: not-allowed;
    opacity: 0.6;
  }
  
  .compact-discount-input::placeholder {
    color: #bbb;
    font-weight: 400;
  }
  
  .discount-suffix {
    font-size: 0.65rem;
    font-weight: 700;
    color: #1976d2;
    white-space: nowrap;
    flex-shrink: 0;
  }
  
  .compact-discount-wrapper.has-discount .discount-suffix {
    color: #f57c00;
  }
  
  /* Compact Discount Amount Display */
  .compact-discount-amount {
    display: flex;
    align-items: center;
    gap: 3px;
    padding: 3px 6px;
    background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
    border-radius: 4px;
    min-width: 60px;
  }
  
  .compact-discount-amount .amount-currency {
    font-size: 0.65rem;
    font-weight: 600;
    color: #666;
  }
  
  .compact-discount-amount .amount-value {
    font-size: 0.75rem;
    font-weight: 600;
    color: #757575;
  }
  
  .compact-discount-amount .amount-value.has-value {
    color: #ff9800;
    font-weight: 700;
  }
  
  .compact-discount-amount:hover .amount-value.has-value {
    color: #f57c00;
  }
  
  /* Compact Total Amount Display */
  .compact-total-amount {
    display: flex;
    align-items: center;
    gap: 3px;
    padding: 3px 6px;
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    border-radius: 4px;
    border: 1px solid #4caf50;
    min-width: 70px;
  }
  
  .compact-total-amount:hover {
    background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
    border-color: #388e3c;
    box-shadow: 0 1px 4px rgba(76, 175, 80, 0.3);
  }
  
  .compact-total-amount .amount-currency {
    font-size: 0.65rem;
    font-weight: 700;
    color: #2e7d32;
  }
  
  .compact-total-amount .amount-value {
    font-size: 0.8rem;
    font-weight: 700;
    color: #1b5e20;
  }
  
  /* Compact Price Display */
  .compact-price-display {
    display: flex;
    align-items: center;
    gap: 3px;
    padding: 3px 6px;
    background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
    border-radius: 4px;
    min-width: 65px;
  }
  
  .compact-price-display:hover {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    box-shadow: 0 1px 3px rgba(25, 118, 210, 0.2);
  }
  
  .compact-price-display .amount-currency {
    font-size: 0.65rem;
    font-weight: 600;
    color: #1976d2;
  }
  
  .compact-price-display .amount-value {
    font-size: 0.75rem;
    font-weight: 600;
    color: #1976d2;
  }
  
  .compact-price-display .amount-value.discounted-price {
    color: #f44336;
    font-weight: 700;
    text-decoration: line-through;
    text-decoration-color: #f44336;
    text-decoration-thickness: 2px;
  }
  
  /* Optimized buttons in payment section for cashier screens */
  .cards.mb-0.mt-3.py-1.px-0.grey.lighten-5 .v-btn {
    font-size: 0.75rem !important;
    padding: 6px 12px !important;
    min-height: 28px !important;
  }
  
  /* Optimized text fields in payment section */
  .cards.mb-0.mt-3.py-1.px-0.grey.lighten-5 .v-text-field .v-field {
    min-height: 30px !important;
  }
  
  .cards.mb-0.mt-3.py-1.px-0.grey.lighten-5 .v-text-field .v-field__input {
    padding: 6px 10px !important;
    font-size: 0.8rem !important;
  }
  
  /* Ensure invoice discount field is editable */
  .cards.mb-0.mt-3.py-1.px-0.grey.lighten-5 .v-text-field input[type="number"] {
    pointer-events: auto !important;
    cursor: text !important;
  }
  
  @media (max-width: 1280px) {
    .quantity-input,
    .rate-input,
    .discount-input {
      max-height: 20px !important;
      min-height: 20px !important;
      font-size: 0.7rem !important;
    }
  
    .quantity-btn {
      min-width: 18px !important;
      width: 18px !important;
      height: 18px !important;
      font-size: 0.7rem !important;
    }
  }
  
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
    margin-bottom: 2px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
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
  
  .action-icon {
    font-size: 16px;
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
  
    .action-btn {
      height: 28px;
      font-size: 0.7rem;
    }
  
    .action-icon {
      font-size: 14px;
    }
  }
  
  /* ===== CUSTOM CHECKBOX ===== */
  .checkbox-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
  }
  
  .custom-checkbox {
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    width: 18px;
    height: 18px;
    border: 2px solid #1976d2;
    border-radius: 3px;
    outline: none;
    cursor: pointer;
    position: relative;
    background: white;
    transition: all 0.2s ease;
  }
  
  .custom-checkbox:checked {
    background: #1976d2;
    border-color: #1976d2;
  }
  
  .custom-checkbox:checked::after {
    content: "✓";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
  }
  
  .custom-checkbox:disabled {
    cursor: not-allowed;
    opacity: 0.6;
    background: #f5f5f5;
  }
  
  .custom-checkbox:disabled:checked {
    background: #9e9e9e;
    border-color: #9e9e9e;
  }
  
  .custom-checkbox:not(:disabled):hover {
    border-color: #1565c0;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
  }

  /* ===== INVOICE TABLE STYLES ===== */
  .invoice-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    font-size: 0.75rem;
  }

  .table-header-cell {
    background: linear-gradient(180deg,rgba(128, 166, 255, 1) 0%, rgba(128, 166, 255, 0.25) 50%);
    border-bottom: 1px solid #e0e0e0;
    padding: 8px 6px;
    font-weight: 600;
    font-size: 0.7rem;
    color: #424242;
    position: sticky;
    top: 0;
    z-index: 1;
  }

  .table-row {
    border-bottom: 1px solid #f1f1f1;
    transition: background-color 0.15s;
  }

  .table-row:hover {
    background: #fafafa;
  }

  .table-cell {
    padding: 6px;
    vertical-align: middle;
    border-right: 1px solid #f5f5f5;
  }

  .table-cell:last-child {
    border-right: none;
  }

  /* Compact table for POS */
  .invoice-items-scrollable {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
  }

  .elevation-0 {
    box-shadow: none;
  }
  </style>
  