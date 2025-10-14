<template>
  <!-- ===== COMPACT PAYMENTS COMPONENT ===== -->
  <div class="payments-container">
    <!-- Fixed Back Button -->
    <button class="back-button-fixed" @click="back_to_invoice" title="Back to Invoice">
      <v-icon size="18">mdi-arrow-left</v-icon>
      <span class="back-text">Back</span>
    </button>

    <v-card class="payments-card" style="max-height: 76vh; height: 76vh">
      <v-progress-linear
        :active="loading"
        :indeterminate="loading"
        absolute
        top
        color="info"
      ></v-progress-linear>
      
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
            <v-switch
              class="compact-switch"
              v-model="is_write_off_change"
              flat
              label="Is it a write-off amount?"
              hide-details
              density="compact"
            ></v-switch>
          </div>
          <div
            class="option-switch"
            v-if="pos_profile.posa_allow_credit_sale && !invoice_doc.is_return"
          >
            <v-switch
            class="compact-switch"
              v-model="is_credit_sale"
              variant="flat"
              label="Is it a credit sale?"
              hide-details
              density="compact"
            ></v-switch>
          </div>
          <div
            class="option-switch"
            v-if="!invoice_doc.is_return && pos_profile.posa_use_customer_credit"
          >
            <v-switch
            class="compact-switch"
              v-model="redeem_customer_credit"
              flat
              label="Use Customer Credit"
              hide-details
              density="compact"
              @change="get_available_credit($event.target.value)"
            ></v-switch>
          </div>
          <div
            class="option-switch"
            v-if="invoice_doc.is_return && pos_profile.posa_use_cashback"
          >
            <v-switch
              v-model="is_cashback"
              flat
              label="Is it a cash refund?"
              hide-details
              density="compact"
            ></v-switch>
          </div>
          <div class="option-date" v-if="is_credit_sale">
            <label>Due Date</label>
            <v-menu ref="date_menu" v-model="date_menu" :close-on-content-click="false" transition="scale-transition">
              <template v-slot:activator="{ props: { on, attrs } }">
                <v-text-field
                  v-model="invoice_doc.due_date"
                  readonly
                  variant="outlined"
                  density="compact"
                  hide-details
                  v-bind="attrs"
                  v-on="on"
                  color="primary"
                  class="compact-date-field"
                ></v-text-field>
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
    </v-card>

    <!-- Phone Dialog -->
    <div>
      <v-dialog v-model="phone_dialog" max-width="400px">
        <v-card>
          <v-card-title>
            <span class="headline primary--text">Confirm Phone Number</span>
          </v-card-title>
          <v-card-text class="pa-0">
            <v-container>
              <v-text-field
                dense
                variant="outlined"
                color="primary"
                label="Phone Number"
                background-color="white"
                hide-details
                v-model="invoice_doc.contact_mobile"
                type="number"
              ></v-text-field>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="error" dark @click="phone_dialog = false">Close</v-btn>
            <v-btn color="primary" dark @click="request_payment">Request</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from "../../bus";
import format from "../../format";
// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],
  data: () => ({
    loading: false,
    pos_profile: "",
    invoice_doc: "",
    customer: "", // Default customer from POS Profile
    loyalty_amount: 0,
    is_credit_sale: 0,
    is_write_off_change: 0,
    date_menu: false,
    po_date_menu: false,
    addresses: [],
    paid_change: 0,
    paid_change_rules: [],
    is_return: false,
    is_cashback: true,
    redeem_customer_credit: false,
    customer_credit_dict: [],
    phone_dialog: false,
    allow_print_in_dialog: false,
    invoiceType: "Invoice",
    pos_settings: "",
    customer_info: "",
    quick_return: false,
    selected_return_payment_idx: null,
    readonly: false,
  }),

  computed: {
    total_payments() {
      let total = parseFloat(this.invoice_doc.loyalty_amount || 0);
      if (this.invoice_doc && this.invoice_doc.payments) {
        this.invoice_doc.payments.forEach((payment) => {
          total += this.flt(payment.amount || 0);
        });
      }

      total += this.flt(this.redeemed_customer_credit || 0);

      if (!this.is_cashback) total = 0;

      return this.flt(total, this.currency_precision);
    },
    diff_payment() {
      const target_amount = flt(this.invoice_doc.rounded_total) || flt(this.invoice_doc.grand_total);
      let diff_payment = this.flt(
        target_amount - this.total_payments,
        this.currency_precision
      );
      this.paid_change = -diff_payment;
      // Match POS-Awesome-V15 behavior: return 0 if negative (overpaid)
      return diff_payment >= 0 ? diff_payment : 0;
    },
    credit_change() {
      let change = -this.diff_payment;
      if (this.paid_change > change) return 0;
      return this.flt(this.paid_change - change, this.currency_precision);
    },
    diff_lable() {
      let lable = this.diff_payment < 0 ? "Remaining" : "Pay Later";
      return lable;
    },
    available_pioints_amount() {
      let amount = 0;
      if (this.customer_info.loyalty_points) {
        amount =
          this.customer_info.loyalty_points *
          this.customer_info.conversion_factor;
      }
      return amount;
    },
    available_customer_credit() {
      let total = 0;
      this.customer_credit_dict.map((row) => {
        total += row.total_credit;
      });

      return total;
    },
    redeemed_customer_credit() {
      let total = 0;
      this.customer_credit_dict.map((row) => {
        if (flt(row.credit_to_redeem)) total += flt(row.credit_to_redeem);
        else row.credit_to_redeem = 0;
      });

      return total;
    },
    vaildatPayment() {
      if (!this.invoice_doc || !this.invoice_doc.payments) {
        return true;
      }
      return false;
    },
    request_payment_field() {
      // If there is a payment method of type Phone, enable the Request button
      if (this.invoice_doc && this.invoice_doc.payments) {
        return this.invoice_doc.payments.some(payment => payment.type === 'Phone');
      }
      return false;
    },
  },

  methods: {
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
        defaultPayment.amount = this.flt(invoice_doc.grand_total, this.currency_precision);
      }
      this.exposeSubmit(true, true);
    },
    getDefaultPayment() {
      const payments = (this.invoice_doc && Array.isArray(this.invoice_doc.payments)) ? this.invoice_doc.payments : [];
      
      // First try to find a payment marked as default
      let defaultPayment = payments.find((payment) => payment.default == 1);
      
      // If no default payment is found, use the first payment as default
      if (!defaultPayment && payments.length > 0) {
        defaultPayment = payments[0];
      }
      
      return defaultPayment;
    },
    back_to_invoice() {
      console.log('Payments.vue(back_to_invoice): Closed');
      evntBus.emit("show_payment", "false");
      evntBus.emit("set_customer_readonly", false);
    },
    async submit(event, autoMode = false, print = false) {
      if (event && typeof event.preventDefault === "function") {
        event.preventDefault();
      }

      try {
        await this.refreshInvoiceDoc();
      } catch (error) {
        // Failed to refresh invoice before submit
      }

      if (this.invoice_doc && this.invoice_doc.docstatus === 1) {
        if (print) {
          this.load_print_page();
        }
        evntBus.emit("show_mesage", {
          text: "Invoice has already been submitted",
          color: "info",
        });
        evntBus.emit("set_last_invoice", this.invoice_doc.name);
        evntBus.emit("new_invoice", "false");
        this.back_to_invoice();
        return;
      }

      if (autoMode) {
        const defaultPayment = this.getDefaultPayment();
        if (!defaultPayment) {
          evntBus.emit("show_mesage", {
            text: "No default payment method in POS profile",
            color: "error",
          });
          return;
        }
        defaultPayment.amount = this.flt(
          this.invoice_doc.grand_total,
          this.currency_precision
        );
      }

      this.submit_invoice(print, autoMode);
    },
    submit_invoice(print, autoMode, retrying = false) {
      // existing logic continues
    if (this.quick_return) {
      this.invoice_doc.is_return = true;
      let total = 0;
      this.invoice_doc.items.forEach(item => {
        item.qty = -1 * item.qty;
        item.amount = -1 * item.amount;
        total += item.amount;
      });
      this.invoice_doc.total = total;
      if (typeof this.selected_return_payment_idx === 'number') {
        this.invoice_doc.payments.forEach((payment) => {
          payment.amount = payment.idx === this.selected_return_payment_idx ? this.invoice_doc.total : 0;
        });
      } else {
        if (this.invoice_doc.payments.length > 0) {
            this.invoice_doc.payments[0].amount = this.invoice_doc.total;
        }
      }
      this.quick_return = false;
    }
      let totalPayedAmount = 0;
      this.invoice_doc.payments.forEach((payment) => {
        payment.amount = flt(payment.amount);
        totalPayedAmount += payment.amount;
      });
      
      // Validate payment amounts before submission against rounded total
      const targetAmount = flt(this.invoice_doc.rounded_total) || flt(this.invoice_doc.grand_total);
      const difference = Math.abs(totalPayedAmount - targetAmount);
      
      if (difference > 0.05) {
        evntBus.emit("show_mesage", {
          text: `Payment mismatch: Total ${totalPayedAmount} vs Target ${targetAmount}`,
          color: "error"
        });
        return;
      }
      if (this.invoice_doc.is_return && totalPayedAmount == 0) {
        this.invoice_doc.is_pos = 0;
      }
      if (this.customer_credit_dict.length) {
        this.customer_credit_dict.forEach((row) => {
          row.credit_to_redeem = flt(row.credit_to_redeem);
        });
      }
      let data = {};
      data["total_change"] = !this.invoice_doc.is_return ? -this.diff_payment : 0;
      data["paid_change"] = !this.invoice_doc.is_return ? this.paid_change : 0;
      data["credit_change"] = -this.credit_change;
      data["redeemed_customer_credit"] = this.redeemed_customer_credit;
      data["customer_credit_dict"] = this.customer_credit_dict;
      data["is_cashback"] = this.is_cashback;

      const vm = this;
      if (autoMode) {
        vm.load_print_page();
        evntBus.emit("show_mesage", {
          text: "Invoice printed using default payment method",
          color: "success",
        });
        evntBus.emit("new_invoice", "false");
        vm.back_to_invoice();
        return;
      }
        frappe.call({
          method: "posawesome.posawesome.api.sales_invoice.submit_invoice",
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
          },
        },
        async: true,
        callback: function (r) {
          if (r.message) {
            if (print) {
              vm.load_print_page();
            }
            evntBus.emit("set_last_invoice", vm.invoice_doc.name);
            evntBus.emit("show_mesage", {
              text: `Invoice ${r.message.name} submitted successfully`,
              color: "success",
            });
            frappe.utils.play_sound("submit");
            this.addresses = [];
            evntBus.emit("new_invoice", "false");
            evntBus.emit("invoice_submitted");
            vm.back_to_invoice();
          } else {
            evntBus.emit("show_mesage", {
              text: "Failed to submit invoice",
              color: "error",
            });
          }
        },
        error(err) {
          const errorMsg = err && err.message ? err.message : "";
          const isTimestampError =
            typeof errorMsg === "string" &&
            errorMsg.includes("Document has been modified");

          if (!retrying && isTimestampError) {
            vm.refreshInvoiceDoc()
              .then(() => {
                vm.submit_invoice(print, autoMode, true);
              })
              .catch(() => {
                evntBus.emit("show_mesage", {
                  text: "Invoice was modified elsewhere, please try again",
                  color: "warning",
                });
              });
            return;
          }

          evntBus.emit("show_mesage", {
            text: err?.message || "Failed to submit invoice",
            color: "error",
          });
        },
      });
    },
    refreshInvoiceDoc() {
      const vm = this;
      if (!vm.invoice_doc || !vm.invoice_doc.name) {
        return Promise.resolve();
      }

      const shouldMergeLocalPayments = vm.invoice_doc.docstatus === 0;
      const localPayments = shouldMergeLocalPayments && vm.invoice_doc.payments
        ? vm.invoice_doc.payments.map((payment) => ({ ...payment }))
        : [];

      return new Promise((resolve, reject) => {
        frappe.call({
          method: "frappe.client.get",
          args: {
            doctype: "Sales Invoice",
            name: vm.invoice_doc.name,
          },
          async: true,
          callback(res) {
            if (res.message) {
              const freshDoc = res.message;

              if (shouldMergeLocalPayments && freshDoc.docstatus === 0) {
                const mergedPayments = (freshDoc.payments || []).map((payment) => {
                  const localMatch = localPayments.find((localPayment) => {
                    if (
                      typeof localPayment.idx !== "undefined" &&
                      typeof payment.idx !== "undefined"
                    ) {
                      return payment.idx === localPayment.idx;
                    }
                    return payment.mode_of_payment === localPayment.mode_of_payment;
                  });

                  if (localMatch) {
                    return {
                      ...payment,
                      amount: localMatch.amount,
                    };
                  }

                  return payment;
                });

                const seen = new Set(
                  mergedPayments.map(
                    (payment) => `${payment.mode_of_payment || ""}__${payment.idx || ""}`
                  )
                );
                localPayments.forEach((localPayment) => {
                  const key = `${localPayment.mode_of_payment || ""}__${localPayment.idx || ""}`;
                  if (!seen.has(key) && flt(localPayment.amount)) {
                    mergedPayments.push(localPayment);
                  }
                });

                freshDoc.payments = mergedPayments;
              }

              vm.invoice_doc = freshDoc;
              resolve();
            } else {
              reject(new Error("Failed to refresh invoice"));
            }
          },
          error(err) {
            reject(err);
          },
        });
      });
    },
    set_full_amount(idx) {
      // Zero all payments first, then set only the chosen one
      const isReturn = !!this.invoice_doc.is_return;
      const total = this.invoice_doc.rounded_total || this.invoice_doc.grand_total;
      this.invoice_doc.payments.forEach((p) => {
        p.amount = 0;
        if (typeof p.base_amount !== 'undefined') p.base_amount = 0;
      });
      const payment = this.invoice_doc.payments.find((p) => p.idx == idx);
      if (payment) {
        payment.amount = isReturn ? -Math.abs(total) : total;
        if (typeof payment.base_amount !== 'undefined') payment.base_amount = payment.amount;
      }
      evntBus.emit('payments_updated', JSON.parse(JSON.stringify(this.invoice_doc.payments)));
    },
    set_rest_amount(idx) {
      // Enhanced behavior: Distribute excess payment amount when focusing on payment field
      const isReturn = !!this.invoice_doc.is_return;
      const invoice_total = flt(this.invoice_doc.rounded_total) || flt(this.invoice_doc.grand_total);
      const total_payments = this.total_payments;
      const actual_remaining = this.flt(invoice_total - total_payments, this.currency_precision);
      
      // Only fill if the focused payment field is empty and there's a remaining amount
      const payment = this.invoice_doc.payments.find(p => p.idx === idx);
      if (!payment || this.flt(payment.amount) !== 0) {
        return; // Don't fill if payment already has an amount
      }
      
      if (actual_remaining > 0) {
        // Fill with remaining amount if there's a balance to be paid
        let amount = actual_remaining;
        if (isReturn) {
          amount = -Math.abs(amount);
        }
        payment.amount = amount;
        if (payment.base_amount !== undefined) {
          payment.base_amount = isReturn ? -Math.abs(amount) : amount;
        }
        console.log('Payments.vue(set_rest_amount): Filled', amount);
        evntBus.emit('payments_updated', JSON.parse(JSON.stringify(this.invoice_doc.payments)));
      }
      else if (actual_remaining < 0) {
        // Handle excess payment distribution
        let excess_amount = Math.abs(actual_remaining);
        if (isReturn) {
          excess_amount = -Math.abs(excess_amount);
        }
        payment.amount = excess_amount;
        if (payment.base_amount !== undefined) {
          payment.base_amount = isReturn ? -Math.abs(excess_amount) : excess_amount;
        }
        console.log('Payments.vue(set_rest_amount): Excess', excess_amount);
        evntBus.emit('payments_updated', JSON.parse(JSON.stringify(this.invoice_doc.payments)));
      }
    },
    clear_all_amounts() {
      this.invoice_doc.payments.forEach((payment) => {
        payment.amount = 0;
      });
    },
    load_print_page() {
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        "/printview?doctype=Sales%20Invoice&name=" +
        this.invoice_doc.name +
        "&trigger_print=1" +
        "&format=" +
        print_format +
        "&no_letterhead=" +
        letter_head;
      const printWindow = window.open(url, "Print");
      printWindow.addEventListener(
        "load",
        function () {
          printWindow.print();
          // Auto-close print window after printing
          setTimeout(() => {
            printWindow.close();
          }, 1000);
        },
        true
      );
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
      let change = -this.diff_payment;
      if (this.paid_change > change) {
        this.paid_change_rules = [
          "Paid change cannot be greater than total change!",
        ];
        this.credit_change = 0;
      }
    },
    get_available_credit(e) {
      this.clear_all_amounts();
      if (e) {
        frappe
          .call("posawesome.posawesome.api.customer.get_available_credit", {
            customer: this.invoice_doc.customer,
            company: this.pos_profile.company,
          })
          .then((r) => {
            const data = r.message;
            if (data.length) {
              const amount =
                this.invoice_doc.grand_total;
              let remainAmount = amount;

              data.forEach((row) => {
                if (remainAmount > 0) {
                  if (remainAmount >= row.total_credit) {
                    row.credit_to_redeem = row.total_credit;
                    remainAmount = remainAmount - row.total_credit;
                  } else {
                    row.credit_to_redeem = remainAmount;
                    remainAmount = 0;
                  }
                } else {
                  row.credit_to_redeem = 0;
                }
              });

              this.customer_credit_dict = data;
            } else {
              this.customer_credit_dict = [];
            }
          });
      } else {
        this.customer_credit_dict = [];
      }
    },
    get_addresses() {
      const vm = this;
      // Use customer from invoice_doc if available, otherwise use default customer
      const customer = vm.invoice_doc && vm.invoice_doc.customer ? vm.invoice_doc.customer : vm.customer;
      
      if (!customer) {
        vm.addresses = [];
        return;
      }
      
      frappe.call({
        method: "posawesome.posawesome.api.customer.get_customer_addresses",
        args: { customer: customer },
        async: true,
        callback: function (r) {
          if (!r.exc) {
            vm.addresses = r.message;
          } else {
            vm.addresses = [];
          }
        },
      });
    },
    addressFilter(item, queryText, itemText) {
      const textOne = item.address_title
        ? item.address_title.toLowerCase()
        : "";
      const textTwo = item.address_line1
        ? item.address_line1.toLowerCase()
        : "";
      const textThree = item.address_line2
        ? item.address_line2.toLowerCase()
        : "";
      const textFour = item.city ? item.city.toLowerCase() : "";
      const textFifth = item.name.toLowerCase();
      const searchText = queryText.toLowerCase();
      return (
        textOne.indexOf(searchText) > -1 ||
        textTwo.indexOf(searchText) > -1 ||
        textThree.indexOf(searchText) > -1 ||
        textFour.indexOf(searchText) > -1 ||
        textFifth.indexOf(searchText) > -1
      );
    },
    new_address() {
      evntBus.emit("open_new_address", this.invoice_doc.customer);
    },
    request_payment() {
      this.phone_dialog = false;
      const vm = this;
      if (!this.invoice_doc.contact_mobile) {
        evntBus.emit("show_mesage", {
          text: "Please enter customer phone number",
          color: "error",
        });
        evntBus.emit("open_edit_customer");
        this.back_to_invoice();
        return;
      }
      evntBus.emit("freeze", {
        title: "Please wait for payment...",
      });
      this.invoice_doc.payments.forEach((payment) => {
        payment.amount = flt(payment.amount);
      });
      let formData = { ...this.invoice_doc };
      formData["total_change"] = -this.diff_payment;
      formData["paid_change"] = this.paid_change;
      formData["credit_change"] = -this.credit_change;
      formData["redeemed_customer_credit"] = this.redeemed_customer_credit;
      formData["customer_credit_dict"] = this.customer_credit_dict;
      formData["is_cashback"] = this.is_cashback;

      frappe
        .call({
          method: "posawesome.posawesome.api.sales_invoice.create_payment_request",
          args: {
            doc: {
              name: vm.invoice_doc.name,
              customer: vm.invoice_doc.customer,
              contact_mobile: vm.invoice_doc.contact_mobile,
              contact_person: vm.invoice_doc.contact_person,
              contact_email: vm.invoice_doc.contact_email,
              grand_total: vm.invoice_doc.grand_total,
              payments: vm.invoice_doc.payments,
              is_return: vm.invoice_doc.is_return
            },
          },
        })
        .then(({ message }) => {
          evntBus.emit("unfreeze");
          evntBus.emit("show_mesage", {
            text: message.message || "Payment request sent successfully",
            color: "success",
          });
        })
        .fail(() => {
          evntBus.emit("unfreeze");
          evntBus.emit("show_mesage", {
            text: "Payment request failed",
            color: "error",
          });
        });
    },
  },

  mounted() {
    this.$nextTick(() => {
      evntBus.on("toggle_quick_return", (value) => {
        this.quick_return = value;
    });
      evntBus.on("send_invoice_doc_payment", (invoice_doc) => {
        this.invoice_doc = invoice_doc;
        
        // Ensure payments array exists and has proper idx values
        if (!this.invoice_doc.payments || !Array.isArray(this.invoice_doc.payments)) {
          evntBus.emit("show_mesage", {
            text: "No payments array in invoice document",
            color: "error",
          });
          this.invoice_doc.payments = [];
        } else {
          // Ensure all payments have idx values
          this.invoice_doc.payments.forEach((payment, index) => {
            if (!payment.idx) {
              payment.idx = index + 1;
            }
          });
        }
        
        const default_payment = this.invoice_doc.payments.find(
          (payment) => payment.default == 1
        );
        this.is_credit_sale = 0;
        this.is_write_off_change = 0;
        if (default_payment && !invoice_doc.is_return) {
          default_payment.amount = this.flt(
            invoice_doc.grand_total,
            this.currency_precision
          );
        }
        if (invoice_doc.is_return) {
          // Align with Payments_new.vue: reset all payments then set default to negative full amount
          this.is_return = true;
          const total = invoice_doc.rounded_total || invoice_doc.grand_total;
          invoice_doc.payments.forEach((payment) => {
            payment.amount = 0;
            if (typeof payment.base_amount !== 'undefined') payment.base_amount = 0;
          });
          if (default_payment) {
            const neg = -Math.abs(total);
            default_payment.amount = neg;
            if (typeof default_payment.base_amount !== 'undefined') default_payment.base_amount = neg;
          }
        }
        this.loyalty_amount = 0;
        this.get_addresses();
      });
      evntBus.on("register_pos_profile", (data) => {
        this.pos_profile = data.pos_profile;
        // Set default customer from POS Profile
        if (data.pos_profile && data.pos_profile.customer) {
          this.customer = data.pos_profile.customer;
          // Load addresses for default customer
          this.get_addresses();
        }
      });
      evntBus.on("add_the_new_address", (data) => {
        this.addresses.push(data);
        this.$forceUpdate();
      });
    });
    evntBus.on("update_customer", (customer) => {
      if (this.customer != customer) {
        this.customer_credit_dict = [];
        this.redeem_customer_credit = false;
        this.is_cashback = true;
      }
    });
    evntBus.on("set_pos_settings", (data) => {
      this.pos_settings = data;
    });
    evntBus.on("set_customer_info_to_edit", (data) => {
      this.customer_info = data;
    });
    
    // Due date update handler
    evntBus.on("update_due_date", (date) => {
      if (this.invoice_doc) {
        this.invoice_doc.due_date = date;
      }
    });
  },
  created() {
    document.addEventListener("keydown", this.shortPay.bind(this));
  },
  beforeDestroy() {
    evntBus.$off("send_invoice_doc_payment");
    evntBus.$off("register_pos_profile");
    evntBus.$off("add_the_new_address");
    evntBus.$off("update_customer");
    evntBus.$off("set_pos_settings");
    evntBus.$off("set_customer_info_to_edit");
    evntBus.$off("update_invoice_coupons");
    evntBus.$off("update_delivery_date");
    evntBus.$off("update_due_date");
  },
  destroyed() {
    document.removeEventListener("keydown", this.shortPay);
  },
  watch: {
    loyalty_amount(value) {
      if (value > this.available_pioints_amount) {
        this.invoice_doc.loyalty_amount = 0;
        this.invoice_doc.redeem_loyalty_points = 0;
        this.invoice_doc.loyalty_points = 0;
        evntBus.emit("show_mesage", {
          text: `Cannot enter points greater than available balance ${this.available_pioints_amount}`,
          color: "error",
        });
      } else {
        this.invoice_doc.loyalty_amount = this.flt(this.loyalty_amount);
        this.invoice_doc.redeem_loyalty_points = 1;
        this.invoice_doc.loyalty_points =
          this.flt(this.loyalty_amount) / this.customer_info.conversion_factor;
      }
    },
    is_credit_sale(value) {
      if (value == 1 && this.invoice_doc && this.invoice_doc.payments && Array.isArray(this.invoice_doc.payments)) {
        this.invoice_doc.payments.forEach((payment) => {
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
        evntBus.emit("show_mesage", {
          text: `Customer credit can be redeemed up to ${this.available_customer_credit}`,
          color: "error",
        });
      }
    },
  },
};
</script>

<style scoped>
/* ===== ULTRA-COMPACT PAYMENTS COMPONENT STYLING ===== */

.payments-container {
  width: 100%;
  height: 100%;
  position: relative;
}

/* Fixed Back Button - Beautiful Design */
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

.back-button-fixed .v-icon {
  transition: transform 0.2s ease;
}

.back-button-fixed:hover .v-icon {
  transform: translateX(-2px);
}

.back-text {
  white-space: nowrap;
  line-height: 1;
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

/* Payment Summary Section */
.payment-summary {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-bottom: 2px;
}

.summary-row {
  display: flex;
  gap: 3px;
  align-items: flex-start;
}

.summary-field-large {
  flex: 1.4;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-field-small {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-field-large label,
.summary-field-small label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin: 0;
  padding: 0 2px;
  line-height: 1;
}

/* Field Display Styles */
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

/* Field Input Wrapper */
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

/* Payment Methods Section */
.payment-methods {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin: 2px 0;
}

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

.payment-amount label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 0 2px;
  line-height: 1;
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

.payment-loyalty {
  margin: 3px 0;
}

.loyalty-row {
  display: flex;
  gap: 3px;
  align-items: flex-start;
}

.loyalty-field-large {
  flex: 1.4;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.loyalty-field-small {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.loyalty-field-large label,
.loyalty-field-small label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 0 2px;
  line-height: 1;
}

/* Customer Credit Section */
.payment-credit {
  margin: 3px 0;
}

.credit-row {
  display: flex;
  gap: 3px;
  align-items: flex-start;
}

.credit-field-large {
  flex: 1.4;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.credit-field-small {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.credit-field-large label,
.credit-field-small label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 0 2px;
  line-height: 1;
}

/* Payment Options (Switches) Section */
.payment-options {
  display: flex;
  gap: 4px;
  margin: 3px 0;
  padding: 4px;
  background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
  border-radius: 4px;
}

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

.option-date label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 0 2px;
  line-height: 1;
}

/* Compact Switch Styling */
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

/* Credit Details Section */
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

.credit-available label,
.credit-redeem label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #e65100;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 0 2px;
  line-height: 1;
}

/* Responsive Design */
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
</style>