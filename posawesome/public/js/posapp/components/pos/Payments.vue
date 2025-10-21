<template>
  <!-- ===== COMPACT PAYMENTS COMPONENT ===== -->
  <div class="payments-container">
    <!-- Fixed Back Button -->
    <button class="back-button-fixed" @click="back_to_invoice" title="Back to Invoice">
      <i class="mdi mdi-arrow-left back-icon"></i>
      <span class="back-text">Back</span>
    </button>

    <div class="card payments-card" style="max-height: 76vh; height: 76vh">
      <div v-if="loading" class="custom-progress-linear">
        <div class="progress-bar"></div>
      </div>
      
      <div class="payments-scroll" style="max-height: 75vh">
        <!-- Payment Summary Section -->
        <div v-if="invoice_doc" class="payment-summary">
          <div class="summary-row">
            <div class="summary-field-large">
              <label>Total Paid</label>
              <div class="field-display success-display">
                <span class="currency">{{ currencySymbol(invoice_doc.currency) }}</span>
                <span class="value">{{ formatCurrency(total_payments) }}</span>
              </div>
            </div>
            <div class="summary-field-small">
              <label>Remaining</label>
              <div class="field-display warning-display">
                <span class="currency">{{ currencySymbol(invoice_doc.currency) }}</span>
                <span class="value">{{ formatCurrency(diff_payment) }}</span>
              </div>
            </div>
          </div>

          <div class="summary-row" v-if="diff_payment < 0 && !invoice_doc.is_return">
            <div class="summary-field-large">
              <label>Remaining Amount</label>
              <div class="field-input-wrapper">
                <span class="currency-prefix">{{ currencySymbol(invoice_doc.currency) }}</span>
                <input
                  type="number"
                  class="compact-input readonly-input"
                  v-model="paid_change"
                  @input="set_paid_change()"
                  readonly
                />
              </div>
            </div>
            <div class="summary-field-small">
              <label>Change Amount</label>
              <div class="field-display info-display">
                <span class="currency">{{ currencySymbol(invoice_doc.currency) }}</span>
                <span class="value">{{ formatCurrency(credit_change) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="section-divider"></div>

        <!-- Payment Methods Section -->
        <div v-if="is_cashback" class="payment-methods">
          <div
            class="payment-method-row"
            v-for="payment in invoice_doc.payments"
            :key="payment.name"
          >
            <div class="payment-amount">
              <label>Amount</label>
              <div class="field-input-wrapper">
                <span class="currency-prefix">{{ currencySymbol(invoice_doc.currency) }}</span>
                <input
                  type="text"
                  class="compact-input"
                  :value="formatCurrency(payment.amount)"
                  @change="setFormatedCurrency(payment, 'amount', null, true, $event)"
                  @focus="set_rest_amount(payment.idx)"
                  :readonly="invoice_doc.is_return ? true : false"
                  placeholder="0.00"
                />
              </div>
            </div>
            <button
              class="payment-method-btn"
              :class="{ 'has-request': payment.type == 'Phone' && payment.amount > 0 && request_payment_field }"
              @click="set_full_amount(payment.idx)"
            >
              {{ payment.mode_of_payment }}
            </button>
            <button
              v-if="payment.type == 'Phone' && payment.amount > 0 && request_payment_field"
              class="request-btn"
              :disabled="payment.amount == 0"
              @click="(phone_dialog = true), (payment.amount = flt(payment.amount, 0))"
            >
              Request
            </button>
          </div>
        </div>

        <!-- Loyalty Points Section -->
        <div
          class="payment-loyalty"
          v-if="invoice_doc && available_pioints_amount > 0 && !invoice_doc.is_return"
        >
          <div class="loyalty-row">
            <div class="loyalty-field-large">
              <label>Pay from Customer Points</label>
              <div class="field-input-wrapper">
                <span class="currency-prefix">{{ currencySymbol(invoice_doc.currency) }}</span>
                <input
                  type="number"
                  class="compact-input"
                  v-model="loyalty_amount"
                  placeholder="0.00"
                />
              </div>
            </div>
            <div class="loyalty-field-small">
              <label>Points Balance</label>
              <div class="field-display disabled-display">
                <span class="currency">{{ currencySymbol(invoice_doc.currency) }}</span>
                <span class="value">{{ formatFloat(available_pioints_amount) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Customer Credit Section -->
        <div
          class="payment-credit"
          v-if="invoice_doc && available_customer_credit > 0 && !invoice_doc.is_return && redeem_customer_credit"
        >
          <div class="credit-row">
            <div class="credit-field-large">
              <label>Redeemed Customer Credit</label>
              <div class="field-display disabled-display">
                <span class="currency">{{ currencySymbol(invoice_doc.currency) }}</span>
                <span class="value">{{ formatCurrency(redeemed_customer_credit) }}</span>
              </div>
            </div>
            <div class="credit-field-small">
              <label>Cash Credit Balance</label>
              <div class="field-display disabled-display">
                <span class="currency">{{ currencySymbol(invoice_doc.currency) }}</span>
                <span class="value">{{ formatCurrency(available_customer_credit) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="section-divider"></div>

        <!-- Options Section (Switches) -->
        <div class="payment-options">
          <div
            class="option-switch"
            v-if="pos_profile.posa_allow_write_off_change && diff_payment > 0 && !invoice_doc.is_return"
          >
            <label class="custom-switch">
              <input 
                type="checkbox" 
                v-model="is_write_off_change"
              />
              <span class="switch-slider"></span>
              <span class="switch-label">Is it a write-off amount?</span>
            </label>
          </div>
          <div
            class="option-switch"
            v-if="pos_profile.posa_allow_credit_sale && !invoice_doc.is_return"
          >
            <label class="custom-switch">
              <input 
                type="checkbox" 
                v-model="is_credit_sale"
              />
              <span class="switch-slider"></span>
              <span class="switch-label">Is it a credit sale?</span>
            </label>
          </div>
          <div
            class="option-switch"
            v-if="!invoice_doc.is_return && pos_profile.posa_use_customer_credit"
          >
            <label class="custom-switch">
              <input 
                type="checkbox" 
                v-model="redeem_customer_credit"
                @change="get_available_credit($event.target.checked)"
              />
              <span class="switch-slider"></span>
              <span class="switch-label">Use Customer Credit</span>
            </label>
          </div>
          <div
            class="option-switch"
            v-if="invoice_doc.is_return && pos_profile.posa_use_cashback"
          >
            <label class="custom-switch">
              <input 
                type="checkbox" 
                v-model="is_cashback"
              />
              <span class="switch-slider"></span>
              <span class="switch-label">Is it a cash refund?</span>
            </label>
          </div>
          <div class="option-date" v-if="is_credit_sale">
            <label>Due Date</label>
            <v-menu ref="date_menu" v-model="date_menu" :close-on-content-click="false" transition="scale-transition">
              <template v-slot:activator="{ props: { on, attrs } }">
                <div class="text-field-wrapper" v-bind="attrs" v-on="on">
                  <input
                    type="text"
                    class="custom-text-field date-field"
                    v-model="invoice_doc.due_date"
                    readonly
                    placeholder="Select date"
                  />
                </div>
              </template>
              <v-date-picker
                v-model="invoice_doc.due_date"
                :no-title="true"
                scrollable
                color="primary"
                :min="frappe.datetime.now_date()"
                @update:model-value="date_menu = false"
              ></v-date-picker>
            </v-menu>
          </div>

        </div>

        <!-- Credit Details Section -->
        <div
          class="credit-details"
          v-if="invoice_doc && available_customer_credit > 0 && !invoice_doc.is_return && redeem_customer_credit"
        >
          <div class="credit-detail-row" v-for="(row, idx) in customer_credit_dict" :key="idx">
            <div class="credit-origin">
              {{ row.credit_origin }}
            </div>
            <div class="credit-available">
              <label>Available Credit</label>
              <div class="field-display disabled-display">
                <span class="currency">{{ currencySymbol(invoice_doc.currency) }}</span>
                <span class="value">{{ formatCurrency(row.total_credit) }}</span>
              </div>
            </div>
            <div class="credit-redeem">
              <label>Credit to Redeem</label>
              <div class="field-input-wrapper">
                <span class="currency-prefix">{{ currencySymbol(invoice_doc.currency) }}</span>
                <input
                  type="number"
                  class="compact-input"
                  v-model="row.credit_to_redeem"
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="section-divider"></div>
      </div>
    </div>

    <!-- Phone Dialog -->
    <div v-if="phone_dialog" class="custom-modal-overlay" @click="phone_dialog = false">
      <div class="custom-modal" @click.stop>
        <div class="card">
          <div class="card-header">
            <span class="card-title">Confirm Phone Number</span>
            <button class="modal-close-btn" @click="phone_dialog = false">×</button>
          </div>
          <div class="card-body">
            <div class="form-container">
              <div class="text-field-wrapper">
                <label class="text-field-label">Phone Number</label>
                <input
                  type="number"
                  class="custom-text-field"
                  v-model="invoice_doc.contact_mobile"
                  placeholder="Enter phone number"
                />
              </div>
            </div>
          </div>
          <div class="card-footer">
            <div class="spacer"></div>
            <button class="btn btn-error" @click="phone_dialog = false">Close</button>
            <button class="btn btn-primary" @click="request_payment">Request</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from "../../bus";
import format from "../../format";
import { API_MAP } from "../../api_mapper.js";

const EVENT_NAMES = {
  SHOW_PAYMENT: 'show_payment',
  SET_CUSTOMER_READONLY: 'set_customer_readonly',
  SHOW_MESSAGE: 'show_mesage',
  SET_LAST_INVOICE: 'set_last_invoice',
  NEW_INVOICE: 'new_invoice',
  INVOICE_SUBMITTED: 'invoice_submitted',
  PAYMENTS_UPDATED: 'payments_updated',
  FREEZE: 'freeze',
  UNFREEZE: 'unfreeze',
  OPEN_EDIT_CUSTOMER: 'open_edit_customer',
  OPEN_NEW_ADDRESS: 'open_new_address',
  TOGGLE_QUICK_RETURN: 'toggle_quick_return',
  SEND_INVOICE_DOC_PAYMENT: 'send_invoice_doc_payment',
  REGISTER_POS_PROFILE: 'register_pos_profile',
  ADD_THE_NEW_ADDRESS: 'add_the_new_address',
  UPDATE_CUSTOMER: 'update_customer',
  SET_POS_SETTINGS: 'set_pos_settings',
  SET_CUSTOMER_INFO_TO_EDIT: 'set_customer_info_to_edit',
  UPDATE_DUE_DATE: 'update_due_date'
};

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],

  // ===== DATA =====
  data() {
    return {
      loading: false,
      pos_profile: "",
      invoice_doc: "",
      customer: "",
      loyalty_amount: 0,
      is_credit_sale: 0,
      is_write_off_change: 0,
      date_menu: false,
      addresses: [],
      paid_change: 0,
      paid_change_rules: [],
      is_return: false,
      is_cashback: true,
      redeem_customer_credit: false,
      customer_credit_dict: [],
      phone_dialog: false,
      pos_settings: "",
      customer_info: "",
      quick_return: false,
      selected_return_payment_idx: null
    };
  },

  // ===== COMPUTED =====
  computed: {
    total_payments() {
      let total = parseFloat(this.invoice_doc.loyalty_amount || 0);
      
      if (this.invoice_doc?.payments) {
        this.invoice_doc.payments.forEach(payment => {
          total += this.flt(payment.amount || 0);
        });
      }

      total += this.flt(this.redeemed_customer_credit || 0);

      if (!this.is_cashback) total = 0;

      return this.flt(total, this.currency_precision);
    },

    diff_payment() {
      const target_amount = flt(this.invoice_doc.rounded_total) || flt(this.invoice_doc.grand_total);
      const diff_payment = this.flt(
        target_amount - this.total_payments,
        this.currency_precision
      );
      this.paid_change = -diff_payment;
      return diff_payment >= 0 ? diff_payment : 0;
    },

    credit_change() {
      const change = -this.diff_payment;
      if (this.paid_change > change) return 0;
      return this.flt(this.paid_change - change, this.currency_precision);
    },

    available_pioints_amount() {
      if (!this.customer_info?.loyalty_points) return 0;
      return this.customer_info.loyalty_points * this.customer_info.conversion_factor;
    },

    available_customer_credit() {
      return this.customer_credit_dict.reduce((total, row) => total + row.total_credit, 0);
    },

    redeemed_customer_credit() {
      return this.customer_credit_dict.reduce((total, row) => {
        const credit = flt(row.credit_to_redeem);
        if (!credit) row.credit_to_redeem = 0;
        return total + credit;
      }, 0);
    },

    vaildatPayment() {
      return !this.invoice_doc || !this.invoice_doc.payments;
    },

    request_payment_field() {
      return this.invoice_doc?.payments?.some(payment => payment.type === 'Phone') || false;
    }
  },

  // ===== METHODS =====
  methods: {
    showMessage(text, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { text, color });
    },

    emitPrintRequest() {
      this.$emit('request-print');
    },

    exposeSubmit(print = true, autoMode = false) {
      this.submit(undefined, autoMode, print);
    },

    autoPayWithDefault(invoice_doc) {
      this.invoice_doc = invoice_doc;
      const defaultPayment = this.getDefaultPayment();
      if (defaultPayment) {
        const total = this.flt(invoice_doc.rounded_total) || this.flt(invoice_doc.grand_total);
        defaultPayment.amount = this.flt(total, this.currency_precision);
      }
      this.exposeSubmit(true, true);
    },

    getDefaultPayment() {
      const payments = Array.isArray(this.invoice_doc?.payments) ? this.invoice_doc.payments : [];
      return payments.find(payment => payment.default == 1) || payments[0] || null;
    },

    back_to_invoice() {
      evntBus.emit(EVENT_NAMES.SHOW_PAYMENT, "false");
      evntBus.emit(EVENT_NAMES.SET_CUSTOMER_READONLY, false);
    },

    async submit(event, autoMode = false, print = false) {
      if (event && typeof event.preventDefault === "function") {
        event.preventDefault();
      }
      try {
        await this.refreshInvoiceDoc();
      } catch (error) {
        console.warn(error?.message ||"Failed to refresh invoice before submit");
      }

      if (this.invoice_doc?.docstatus === 1) {
        if (print) {
          this.load_print_page();
        }
        this.showMessage("Invoice has already been submitted", "info");
        evntBus.emit(EVENT_NAMES.SET_LAST_INVOICE, this.invoice_doc.name);
        evntBus.emit(EVENT_NAMES.NEW_INVOICE, "false");
        this.back_to_invoice();
        return;
      }

      if (autoMode) {
        const defaultPayment = this.getDefaultPayment();
        if (!defaultPayment) {
          this.showMessage("No default payment method in POS profile", "error");
          return;
        }
        const total = this.flt(this.invoice_doc.rounded_total) || this.flt(this.invoice_doc.grand_total);
        defaultPayment.amount = this.flt(total, this.currency_precision);
      }

      this.submit_invoice(print, autoMode);
    },

    submit_invoice(print, autoMode, retrying = false) {
      if (this.quick_return) {
        this.invoice_doc.is_return = 1;
        
        let total = 0;
        this.invoice_doc.items.forEach(item => {
          item.qty = -1 * Math.abs(item.qty);
          item.stock_qty = -1 * Math.abs(item.stock_qty || item.qty);
          item.amount = -1 * Math.abs(item.amount);
          item.net_amount = -1 * Math.abs(item.net_amount || item.amount);
          total += item.amount;
        });
        
        this.invoice_doc.total = total;
        this.invoice_doc.net_total = total;
        this.invoice_doc.grand_total = total;
        this.invoice_doc.rounded_total = total;
        this.invoice_doc.base_total = total;
        this.invoice_doc.base_net_total = total;
        this.invoice_doc.base_grand_total = total;
        
        if (typeof this.selected_return_payment_idx === 'number') {
          this.invoice_doc.payments.forEach(payment => {
            payment.amount = payment.idx === this.selected_return_payment_idx ? total : 0;
          });
        } else {
          if (this.invoice_doc.payments?.length > 0) {
            this.invoice_doc.payments[0].amount = total;
          }
        }
        
        this.quick_return = false;
      }

      let totalPayedAmount = 0;
      this.invoice_doc.payments.forEach(payment => {
        payment.amount = flt(payment.amount);
        totalPayedAmount += payment.amount;
      });
      
      const targetAmount = flt(this.invoice_doc.rounded_total) || flt(this.invoice_doc.grand_total);
      const difference = Math.abs(totalPayedAmount - targetAmount);
      
      if (difference > 0.05) {
        this.showMessage(`Payment mismatch: Total ${totalPayedAmount} vs Target ${targetAmount}`, "error");
        return;
      }

      if (this.invoice_doc.is_return && totalPayedAmount == 0) {
        this.invoice_doc.is_pos = 0;
      }

      if (this.customer_credit_dict.length) {
        this.customer_credit_dict.forEach(row => {
          row.credit_to_redeem = flt(row.credit_to_redeem);
        });
      }

      const data = {
        total_change: !this.invoice_doc.is_return ? -this.diff_payment : 0,
        paid_change: !this.invoice_doc.is_return ? this.paid_change : 0,
        credit_change: -this.credit_change,
        redeemed_customer_credit: this.redeemed_customer_credit,
        customer_credit_dict: this.customer_credit_dict,
        is_cashback: this.is_cashback
      };

      if (autoMode) {
        this.load_print_page();
        this.showMessage("Invoice printed using default payment method", "success");
        evntBus.emit(EVENT_NAMES.NEW_INVOICE, "false");
        this.back_to_invoice();
        return;
      }

      frappe.call({
        method: API_MAP.SALES_INVOICE.SUBMIT,
        args: {
          data: data,
          invoice: {
            name: this.invoice_doc.name,
            customer: this.invoice_doc.customer,
            is_return: this.invoice_doc.is_return,
            is_pos: this.invoice_doc.is_pos,
            payments: this.invoice_doc.payments,
            loyalty_amount: this.invoice_doc.loyalty_amount,
            redeem_loyalty_points: this.invoice_doc.redeem_loyalty_points,
            loyalty_points: this.invoice_doc.loyalty_points,
            write_off_amount: this.invoice_doc.write_off_amount,
            write_off_outstanding_amount_automatically: this.invoice_doc.write_off_outstanding_amount_automatically,
            contact_mobile: this.invoice_doc.contact_mobile,
            contact_person: this.invoice_doc.contact_person,
            contact_email: this.invoice_doc.contact_email,
            due_date: this.invoice_doc.due_date,
            delivery_date: this.invoice_doc.delivery_date,
            address_display: this.invoice_doc.address_display,
            shipping_address_name: this.invoice_doc.shipping_address_name,
            customer_address: this.invoice_doc.customer_address,
            shipping_address: this.invoice_doc.shipping_address
          }
        },
        async: true,
        callback: (r) => {
          if (r.message) {
            if (print) {
              this.load_print_page();
            }
            evntBus.emit(EVENT_NAMES.SET_LAST_INVOICE, this.invoice_doc.name);
            this.showMessage(`Invoice ${r.message.name} submitted successfully`, "success");
            frappe.utils.play_sound("submit");
            this.addresses = [];
            evntBus.emit(EVENT_NAMES.NEW_INVOICE, "false");
            evntBus.emit(EVENT_NAMES.INVOICE_SUBMITTED);
            this.back_to_invoice();
          } else {
            this.showMessage("Failed to submit invoice", "error");
          }
        },
        error: (err) => {
          const errorMsg = err?.message || "";
          const isTimestampError = typeof errorMsg === "string" && errorMsg.includes("Document has been modified");

          if (!retrying && isTimestampError) {
            this.refreshInvoiceDoc()
              .then(() => {
                this.submit_invoice(print, autoMode, true);
              })
              .catch(() => {
                this.showMessage("Invoice was modified elsewhere, please try again", "warning");
              });
            return;
          }

          this.showMessage(err?.message || "Failed to submit invoice", "error");
        }
      });
    },

    refreshInvoiceDoc() {
      if (!this.invoice_doc?.name) {
        return Promise.resolve();
      }

      const shouldMergeLocalPayments = this.invoice_doc.docstatus === 0;
      const localPayments = shouldMergeLocalPayments && this.invoice_doc.payments
        ? this.invoice_doc.payments.map(payment => ({ ...payment }))
        : [];

      return new Promise((resolve, reject) => {
        frappe.call({
          method: API_MAP.FRAPPE.CLIENT_GET,
          args: {
            doctype: "Sales Invoice",
            name: this.invoice_doc.name
          },
          async: true,
          callback: (res) => {
            if (res.message) {
              const freshDoc = res.message;

              if (shouldMergeLocalPayments && freshDoc.docstatus === 0) {
                const mergedPayments = (freshDoc.payments || []).map(payment => {
                  const localMatch = localPayments.find(localPayment => {
                    if (localPayment.idx !== undefined && payment.idx !== undefined) {
                      return payment.idx === localPayment.idx;
                    }
                    return payment.mode_of_payment === localPayment.mode_of_payment;
                  });

                  return localMatch ? { ...payment, amount: localMatch.amount } : payment;
                });

                const seen = new Set(
                  mergedPayments.map(payment => `${payment.mode_of_payment || ""}__${payment.idx || ""}`)
                );

                localPayments.forEach(localPayment => {
                  const key = `${localPayment.mode_of_payment || ""}__${localPayment.idx || ""}`;
                  if (!seen.has(key) && flt(localPayment.amount)) {
                    mergedPayments.push(localPayment);
                  }
                });

                freshDoc.payments = mergedPayments;
              }

              this.invoice_doc = freshDoc;
              resolve();
            } else {
              reject(new Error("Failed to refresh invoice"));
            }
          },
          error: (err) => reject(err)
        });
      });
    },

    set_full_amount(idx) {
      const isReturn = !!this.invoice_doc.is_return;
      const total = this.invoice_doc.rounded_total || this.invoice_doc.grand_total;
      
      this.invoice_doc.payments.forEach(p => {
        p.amount = 0;
        if (p.base_amount !== undefined) p.base_amount = 0;
      });
      
      const payment = this.invoice_doc.payments.find(p => p.idx == idx);
      if (payment) {
        payment.amount = isReturn ? -Math.abs(total) : total;
        if (payment.base_amount !== undefined) payment.base_amount = payment.amount;
      }
      
      evntBus.emit(EVENT_NAMES.PAYMENTS_UPDATED, JSON.parse(JSON.stringify(this.invoice_doc.payments)));
    },

    set_rest_amount(idx) {
      const isReturn = !!this.invoice_doc.is_return;
      const invoice_total = flt(this.invoice_doc.rounded_total) || flt(this.invoice_doc.grand_total);
      const total_payments = this.total_payments;
      const actual_remaining = this.flt(invoice_total - total_payments, this.currency_precision);
      
      const payment = this.invoice_doc.payments.find(p => p.idx === idx);
      if (!payment || this.flt(payment.amount) !== 0) {
        return;
      }
      
      if (actual_remaining > 0) {
        let amount = actual_remaining;
        if (isReturn) amount = -Math.abs(amount);
        
        payment.amount = amount;
        if (payment.base_amount !== undefined) {
          payment.base_amount = isReturn ? -Math.abs(amount) : amount;
        }
        evntBus.emit(EVENT_NAMES.PAYMENTS_UPDATED, JSON.parse(JSON.stringify(this.invoice_doc.payments)));
      } else if (actual_remaining < 0) {
        let excess_amount = Math.abs(actual_remaining);
        if (isReturn) excess_amount = -Math.abs(excess_amount);
        
        payment.amount = excess_amount;
        if (payment.base_amount !== undefined) {
          payment.base_amount = isReturn ? -Math.abs(excess_amount) : excess_amount;
        }
        evntBus.emit(EVENT_NAMES.PAYMENTS_UPDATED, JSON.parse(JSON.stringify(this.invoice_doc.payments)));
      }
    },

    clear_all_amounts() {
      this.invoice_doc.payments.forEach(payment => {
        payment.amount = 0;
      });
    },

    load_print_page() {
      const print_format = this.pos_profile.print_format_for_online || this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url = `${frappe.urllib.get_base_url()}/printview?doctype=Sales%20Invoice&name=${this.invoice_doc.name}&trigger_print=1&format=${print_format}&no_letterhead=${letter_head}`;
      
      const printWindow = window.open(url, "Print");
      printWindow.addEventListener("load", function () {
        printWindow.print();
        setTimeout(() => printWindow.close(), 1000);
      }, true);
    },

    validate_due_date() {
      const today = frappe.datetime.now_date();
      const parse_today = Date.parse(today);
      const new_date = Date.parse(this.invoice_doc.due_date);
      
      if (new_date < parse_today) {
        setTimeout(() => {
          this.invoice_doc.due_date = today;
        }, 0);
      }
    },

    shortPay(e) {
      if (e.key === "x" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.submit();
      }
    },

    set_paid_change() {
      if (!this.paid_change) this.paid_change = 0;

      this.paid_change_rules = [];
      const change = -this.diff_payment;
      
      if (this.paid_change > change) {
        this.paid_change_rules = ["Paid change cannot be greater than total change!"];
        this.credit_change = 0;
      }
    },

    get_available_credit(e) {
      this.clear_all_amounts();
      
      if (!e) {
        this.customer_credit_dict = [];
        return;
      }

      frappe.call({
        method: API_MAP.CUSTOMER.GET_CUSTOMER_CREDIT,
        args: {
          customer_id: this.invoice_doc.customer,
          company: this.pos_profile.company
        },
        callback: (r) => {
          const data = r.message;
          
          if (!data?.length) {
            this.customer_credit_dict = [];
            return;
          }

          const amount = this.invoice_doc.grand_total;
          let remainAmount = amount;

          data.forEach(row => {
            if (remainAmount > 0) {
              row.credit_to_redeem = remainAmount >= row.total_credit ? row.total_credit : remainAmount;
              remainAmount -= row.credit_to_redeem;
            } else {
              row.credit_to_redeem = 0;
            }
          });

          this.customer_credit_dict = data;
        }
      });
    },

    get_addresses() {
      const customer = this.invoice_doc?.customer || this.customer;
      
      if (!customer) {
        this.addresses = [];
        return;
      }
      
      frappe.call({
        method: API_MAP.CUSTOMER.GET_ADDRESSES,
        args: { customer_id: customer },
        async: true,
        callback: (r) => {
          this.addresses = r.exc ? [] : r.message;
        }
      });
    },

    addressFilter(item, queryText) {
      const searchText = queryText.toLowerCase();
      const fields = [
        item.address_title,
        item.address_line1,
        item.address_line2,
        item.city,
        item.name
      ];

      return fields.some(field => 
        field?.toLowerCase().includes(searchText)
      );
    },

      // Open dialog to create new address
    new_address() {
      evntBus.emit(EVENT_NAMES.OPEN_NEW_ADDRESS, this.invoice_doc.customer);
    },

    //  Request payment (disabled feature)
    request_payment() {
      this.phone_dialog = false;
      
      if (!this.invoice_doc.contact_mobile) {
        this.showMessage("Please enter customer phone number", "error");
        evntBus.emit(EVENT_NAMES.OPEN_EDIT_CUSTOMER);
        this.back_to_invoice();
        return;
      }

      evntBus.emit(EVENT_NAMES.FREEZE, { title: "Please wait for payment..." });
      
      this.invoice_doc.payments.forEach(payment => {
        payment.amount = flt(payment.amount);
      });

      evntBus.emit(EVENT_NAMES.UNFREEZE);
      this.showMessage("Payment request feature has been disabled", "info");
    }
  },

  // ===== LIFECYCLE HOOKS =====
  mounted() {
    this.$nextTick(() => {
      evntBus.on(EVENT_NAMES.TOGGLE_QUICK_RETURN, (value) => {
        this.quick_return = value;
      });

      evntBus.on(EVENT_NAMES.SEND_INVOICE_DOC_PAYMENT, (invoice_doc) => {
        this.invoice_doc = invoice_doc;
        
        if (!Array.isArray(this.invoice_doc.payments)) {
          this.showMessage("No payments array in invoice document", "error");
          this.invoice_doc.payments = [];
        } else {
          this.invoice_doc.payments.forEach((payment, index) => {
            if (!payment.idx) payment.idx = index + 1;
          });
        }
        
        const default_payment = this.invoice_doc.payments.find(payment => payment.default == 1);
        this.is_credit_sale = 0;
        this.is_write_off_change = 0;

        if (default_payment && !invoice_doc.is_return) {
          const total = this.flt(invoice_doc.rounded_total) || this.flt(invoice_doc.grand_total);
          default_payment.amount = this.flt(total, this.currency_precision);
        }

        if (invoice_doc.is_return) {
          this.is_return = true;
          const total = invoice_doc.rounded_total || invoice_doc.grand_total;
          
          invoice_doc.payments.forEach(payment => {
            payment.amount = 0;
            if (payment.base_amount !== undefined) payment.base_amount = 0;
          });

          if (default_payment) {
            const neg = -Math.abs(total);
            default_payment.amount = neg;
            if (default_payment.base_amount !== undefined) default_payment.base_amount = neg;
          }
        }

        this.loyalty_amount = 0;
        this.get_addresses();
      });

      evntBus.on(EVENT_NAMES.REGISTER_POS_PROFILE, (data) => {
        this.pos_profile = data.pos_profile;
        if (data.pos_profile?.customer) {
          this.customer = data.pos_profile.customer;
          this.get_addresses();
        }
      });

      evntBus.on(EVENT_NAMES.ADD_THE_NEW_ADDRESS, (data) => {
        this.addresses.push(data);
        this.$forceUpdate();
      });
    });

    evntBus.on(EVENT_NAMES.UPDATE_CUSTOMER, (customer) => {
      if (this.customer != customer) {
        this.customer_credit_dict = [];
        this.redeem_customer_credit = false;
        this.is_cashback = true;
      }
    });

    evntBus.on(EVENT_NAMES.SET_POS_SETTINGS, (data) => {
      this.pos_settings = data;
    });

    evntBus.on(EVENT_NAMES.SET_CUSTOMER_INFO_TO_EDIT, (data) => {
      this.customer_info = data;
    });
    
    evntBus.on(EVENT_NAMES.UPDATE_DUE_DATE, (date) => {
      if (this.invoice_doc) {
        this.invoice_doc.due_date = date;
      }
    });
  },

  created() {
    document.addEventListener("keydown", this.shortPay.bind(this));
  },

  beforeDestroy() {
    // Clean up all event listeners
    const events = [
      EVENT_NAMES.TOGGLE_QUICK_RETURN,
      EVENT_NAMES.SEND_INVOICE_DOC_PAYMENT,
      EVENT_NAMES.REGISTER_POS_PROFILE,
      EVENT_NAMES.ADD_THE_NEW_ADDRESS,
      EVENT_NAMES.UPDATE_CUSTOMER,
      EVENT_NAMES.SET_POS_SETTINGS,
      EVENT_NAMES.SET_CUSTOMER_INFO_TO_EDIT,
      EVENT_NAMES.UPDATE_DUE_DATE,
      'update_invoice_coupons',
      'update_delivery_date'
    ];

    events.forEach(event => evntBus.$off(event));
  },

  destroyed() {
    document.removeEventListener("keydown", this.shortPay);
  },

  // ===== WATCHERS =====
  watch: {
    loyalty_amount(value) {
      if (value > this.available_pioints_amount) {
        this.invoice_doc.loyalty_amount = 0;
        this.invoice_doc.redeem_loyalty_points = 0;
        this.invoice_doc.loyalty_points = 0;
        this.showMessage(
          `Cannot enter points greater than available balance ${this.available_pioints_amount}`,
          "error"
        );
      } else {
        this.invoice_doc.loyalty_amount = this.flt(this.loyalty_amount);
        this.invoice_doc.redeem_loyalty_points = 1;
        this.invoice_doc.loyalty_points = this.flt(this.loyalty_amount) / this.customer_info.conversion_factor;
      }
    },

    is_credit_sale(value) {
      if (value == 1 && Array.isArray(this.invoice_doc?.payments)) {
        this.invoice_doc.payments.forEach(payment => {
          payment.amount = 0;
          payment.base_amount = 0;
        });
      }
    },

    is_write_off_change(value) {
      if (value == 1) {
        this.invoice_doc.write_off_amount = this.diff_payment;
        this.invoice_doc.write_off_outstanding_amount_automatically = 1;
      } else {
        this.invoice_doc.write_off_amount = 0;
        this.invoice_doc.write_off_outstanding_amount_automatically = 0;
      }
    },

    redeemed_customer_credit(value) {
      if (value > this.available_customer_credit) {
        this.showMessage(
          `Customer credit can be redeemed up to ${this.available_customer_credit}`,
          "error"
        );
      }
    }
  }
};
</script>

<style scoped>
/* SHARED LABEL STYLES */
.summary-field-large label,
.summary-field-small label,
.payment-amount label,
.loyalty-field-large label,
.loyalty-field-small label,
.credit-field-large label,
.credit-field-small label,
.credit-available label,
.credit-redeem label,
.option-date label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin: 0;
  padding: 0 2px;
  line-height: 1;
}

/* CONTAINER STYLES */
.payments-container {
  width: 100%;
  height: 100%;
  position: relative;
}

/* Card Components */
.card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1976d2;
}

.card-body {
  padding: 16px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
}

/* Spacer */
.spacer {
  flex: 1;
}

/* Form Container */
.form-container {
  padding: 0;
}

/* Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.2s;
  line-height: 1.5;
  margin: 0 4px;
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn:active {
  transform: translateY(0);
}

.btn-primary {
  background: linear-gradient(135deg, #1976d2 0%, #1e88e5 100%);
  border-color: #1565c0;
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);
}

.btn-error {
  background: linear-gradient(135deg, #f44336 0%, #e53935 100%);
  border-color: #d32f2f;
  color: white;
}

.btn-error:hover {
  background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%);
}

.payments-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%) !important;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.payments-scroll {
  overflow-y: auto;
  overflow-x: hidden;
  padding: 6px;
}

/* Professional Scrollbar */
.payments-scroll::-webkit-scrollbar {
  width: 6px;
}

.payments-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.payments-scroll::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  border-radius: 3px;
}

.payments-scroll::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
}

/* Section Divider */
.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #e0e0e0 50%, transparent 100%);
  margin: 4px 0;
}

/* BACK BUTTON */
.back-button-fixed {
  position: absolute;
  bottom: 12px;
  right: 12px;
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 4px;
  height: 26px;
  padding: 0 10px;
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(25, 118, 210, 0.3);
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.back-button-fixed:hover {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(25, 118, 210, 0.4);
}

.back-button-fixed:active {
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(25, 118, 210, 0.3);
}

.back-icon {
  color: white;
  font-size: 18px;
}

.back-button-fixed:hover .back-icon {
  transform: translateX(-2px);
}

.back-text {
  white-space: nowrap;
  line-height: 1;
}

/* SHARED ROW LAYOUT */
.summary-row,
.loyalty-row,
.credit-row {
  display: flex;
  gap: 3px;
  align-items: flex-start;
}

.summary-field-large,
.loyalty-field-large,
.credit-field-large {
  flex: 1.4;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-field-small,
.loyalty-field-small,
.credit-field-small {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* FIELD DISPLAY STYLES (SHARED) */
.field-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 3px 6px;
  border-radius: 3px;
  border: 1px solid #e0e0e0;
  background: white;
  min-height: 22px;
  transition: all 0.2s ease;
}

.field-display .currency {
  font-size: 0.6rem;
  font-weight: 600;
  color: #666;
  margin-right: 3px;
}

.field-display .value {
  font-size: 0.7rem;
  font-weight: 700;
  color: #333;
  flex: 1;
  text-align: right;
}

/* Display Variants */
.success-display {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border-color: #4caf50;
}

.success-display .value {
  color: #2e7d32;
}

.warning-display {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-color: #ff9800;
}

.warning-display .value {
  color: #e65100;
}

.info-display {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-color: #2196f3;
}

.info-display .value {
  color: #0d47a1;
}

.disabled-display {
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  border-color: #bdbdbd;
  opacity: 0.8;
}

.disabled-display .value {
  color: #757575;
}

/* FIELD INPUT WRAPPER (SHARED) */
.field-input-wrapper {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #1976d2;
  border-radius: 3px;
  padding: 1px 4px;
  min-height: 22px;
  transition: all 0.2s ease;
}

.field-input-wrapper:hover {
  border-color: #1565c0;
  box-shadow: 0 1px 3px rgba(25, 118, 210, 0.15);
}

.field-input-wrapper:focus-within {
  border-color: #0d47a1;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.12);
  background: #e3f2fd;
}

.currency-prefix {
  font-size: 0.6rem;
  font-weight: 600;
  color: #1976d2;
  margin-right: 3px;
  flex-shrink: 0;
}

.compact-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.7rem;
  font-weight: 700;
  color: #1976d2;
  text-align: right;
  padding: 1px;
  min-width: 0;
  line-height: 1.2;
}

.compact-input::placeholder {
  color: #90caf9;
  opacity: 0.6;
}

.compact-input::-webkit-inner-spin-button,
.compact-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.compact-input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}

.readonly-input {
  color: #757575;
  cursor: not-allowed;
}

/* SECTION-SPECIFIC STYLES */
.payment-summary {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-bottom: 2px;
}

.payment-methods {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin: 2px 0;
}

.payment-loyalty {
  margin: 3px 0;
}

.payment-credit {
  margin: 3px 0;
}

.payment-options {
  display: flex;
  gap: 4px;
  margin: 3px 0;
  padding: 4px;
  background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
  border-radius: 4px;
}

.credit-details {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin: 3px 0;
  padding: 4px;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-radius: 4px;
  border: 1px solid #ff9800;
}

/* PAYMENT METHOD ROW */
.payment-method-row {
  display: flex;
  gap: 3px;
  align-items: flex-end;
}

.payment-amount {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.payment-method-btn {
  flex: 1;
  height: 22px;
  border: none;
  border-radius: 3px;
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
  font-size: 0.65rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(25, 118, 210, 0.25);
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 4px;
}

.payment-method-btn:hover {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(25, 118, 210, 0.35);
}

.payment-method-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(25, 118, 210, 0.25);
}

.payment-method-btn.has-request {
  flex: 0.7;
}

.request-btn {
  flex: 0.4;
  height: 22px;
  border: none;
  border-radius: 3px;
  background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
  color: white;
  font-size: 0.65rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(76, 175, 80, 0.25);
  transition: all 0.2s ease;
}

.request-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.35);
}

.request-btn:disabled {
  background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
  color: #9e9e9e;
  cursor: not-allowed;
  opacity: 0.6;
}

/* SWITCHES AND OPTIONS */
.option-switch {
  flex: 1 1 calc(50% - 2px);
  min-width: 130px;
}

.option-date {
  flex: 1 1 calc(50% - 2px);
  min-width: 130px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.compact-switch :deep(.v-label) {
  font-size: 0.65rem !important;
  color: #666 !important;
  line-height: 1.2 !important;
}

.compact-switch :deep(.v-input__control) {
  min-height: 20px !important;
}

.compact-switch :deep(.v-selection-control) {
  min-height: 20px !important;
}

.compact-date-field :deep(.v-field__input) {
  min-height: 22px !important;
  padding: 1px 6px !important;
  font-size: 0.7rem !important;
}

.compact-date-field :deep(.v-field) {
  min-height: 22px !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
/* CREDIT DETAILS */
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.credit-details label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #e65100;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 0 2px;
  line-height: 1;
}

.credit-detail-row {
  display: flex;
  gap: 3px;
  align-items: center;
}

.credit-origin {
  flex: 0.8;
  font-size: 0.7rem;
  font-weight: 600;
  color: #e65100;
  padding: 3px 6px;
  background: white;
  border-radius: 3px;
  border: 1px solid #ffcc80;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.credit-available {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.credit-redeem {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
/* RESPONSIVE DESIGN */
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

@media (max-width: 768px) {
  .summary-row,
  .loyalty-row,
  .credit-row {
    flex-direction: column;
  }
  
  .summary-field-large,
  .summary-field-small,
  .loyalty-field-large,
  .loyalty-field-small,
  .credit-field-large,
  .credit-field-small {
    flex: 1;
  }
  
  .payment-method-row {
    flex-wrap: wrap;
  }
  
  .payment-amount {
    flex: 1 1 100%;
  }
  
  .payment-method-btn,
  .request-btn {
    flex: 1 1 calc(50% - 2px);
  }
  
  .option-switch,
  .option-date {
    flex: 1 1 100%;
  }
}

/* ===== CUSTOM TEXT FIELD ===== */
.text-field-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.text-field-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 2px;
}

.custom-text-field {
  width: 100%;
  padding: 8px 12px;
  font-size: 0.85rem;
  color: #333;
  background: white;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  outline: none;
  transition: all 0.2s ease;
}

.custom-text-field:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.custom-text-field:hover:not(:disabled):not(:focus) {
  border-color: #999;
}

.custom-text-field:disabled,
.custom-text-field:read-only {
  background: #f5f5f5;
  cursor: not-allowed;
  color: #666;
}

.custom-text-field.date-field {
  cursor: pointer;
}

.custom-text-field.date-field:read-only {
  cursor: pointer;
  background: white;
}

.custom-text-field::placeholder {
  color: #999;
  font-size: 0.8rem;
}

/* Compact variant */
.custom-text-field.compact {
  padding: 6px 10px;
  font-size: 0.8rem;
}

/* Error state */
.text-field-wrapper.error .custom-text-field {
  border-color: #f44336;
}

.text-field-wrapper.error .text-field-label {
  color: #f44336;
}

/* ===== CUSTOM SWITCH ===== */
.custom-switch {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  user-select: none;
  gap: 12px;
}

.custom-switch input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  background: #ccc;
  border-radius: 24px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.switch-slider::before {
  content: "";
  position: absolute;
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.custom-switch input[type="checkbox"]:checked + .switch-slider {
  background: #1976d2;
}

.custom-switch input[type="checkbox"]:checked + .switch-slider::before {
  transform: translateX(20px);
}

.custom-switch input[type="checkbox"]:focus + .switch-slider {
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
}

.custom-switch:hover .switch-slider {
  opacity: 0.9;
}

.custom-switch input[type="checkbox"]:disabled + .switch-slider {
  opacity: 0.5;
  cursor: not-allowed;
}

.switch-label {
  font-size: 0.85rem;
  color: #333;
  font-weight: 500;
}

.custom-switch input[type="checkbox"]:disabled ~ .switch-label {
  color: #999;
}

/* Compact variant */
.custom-switch.compact .switch-slider {
  width: 36px;
  height: 20px;
}

.custom-switch.compact .switch-slider::before {
  height: 14px;
  width: 14px;
}

.custom-switch.compact input[type="checkbox"]:checked + .switch-slider::before {
  transform: translateX(16px);
}

.custom-switch.compact .switch-label {
  font-size: 0.8rem;
}

/* ===== CUSTOM PROGRESS LINEAR ===== */
.custom-progress-linear {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #e0e0e0;
  overflow: hidden;
  z-index: 10;
}

.custom-progress-linear .progress-bar {
  height: 100%;
  background: #1976d2;
  animation: progress-indeterminate 1.5s infinite linear;
  transform-origin: 0% 50%;
}

@keyframes progress-indeterminate {
  0% {
    transform: translateX(0) scaleX(0);
  }
  40% {
    transform: translateX(0) scaleX(0.4);
  }
  100% {
    transform: translateX(100%) scaleX(0.5);
  }
}

/* Thin variant for search */
.custom-progress-linear.search-progress {
  height: 2px;
}

/* ===== CUSTOM MODAL ===== */
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: modal-fade-in 0.2s ease;
}

.custom-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
  animation: modal-slide-in 0.3s ease;
}

.modal-close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #999;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.modal-close-btn:hover {
  background: #f5f5f5;
  color: #333;
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

/* Responsive modal */
@media (max-width: 600px) {
  .custom-modal {
    width: 95%;
    margin: 20px;
  }
}
</style>