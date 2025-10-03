<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div>
    <v-card
      class="selection mx-auto grey lighten-5 pa-1"
      style="max-height: 76vh; height: 76vh"
    >
      <v-progress-linear
        :active="loading"
        :indeterminate="loading"
        absolute
        top
        color="info"
      ></v-progress-linear>
      <div class="overflow-y-auto px-2 pt-2" style="max-height: 75vh">
        <v-row v-if="invoice_doc" class="px-1 py-0">
          <v-col cols="7">
            <v-text-field
              variant="outlined"
              color="primary"
              label="Total Paid"
              background-color="white"
              hide-details
              :model-value="formatCurrency(total_payments)"
              readonly
              :prefix="currencySymbol(invoice_doc.currency)"
              dense
            ></v-text-field>
          </v-col>
          <v-col cols="5">
            <v-text-field
              variant="outlined"
              color="primary"
              label="Remaining"
              background-color="white"
              hide-details
              :model-value="formatCurrency(diff_payment)"
              readonly
              :prefix="currencySymbol(invoice_doc.currency)"
              dense
            ></v-text-field>
          </v-col>

          <v-col cols="7" v-if="diff_payment < 0 && !invoice_doc.is_return">
            <v-text-field
              variant="outlined"
              color="primary"
              label="Remaining Amount"
              background-color="white"
              v-model="paid_change"
              @input="set_paid_change()"
              :prefix="currencySymbol(invoice_doc.currency)"
              :rules="paid_change_rules"
              dense
              readonly
              type="number"
            ></v-text-field>
          </v-col>

          <v-col cols="5" v-if="diff_payment < 0 && !invoice_doc.is_return">
            <v-text-field
              variant="outlined"
              color="primary"
              label="Change Amount"
              background-color="white"
              hide-details
              :model-value="formatCurrency(credit_change)"
              readonly
              :prefix="currencySymbol(invoice_doc.currency)"
              dense
            ></v-text-field>
          </v-col>
        </v-row>
        <v-divider></v-divider>

        <div v-if="is_cashback">
          <v-row
            class="pyments px-1 py-0"
            v-for="payment in invoice_doc.payments"
            :key="payment.name"
          >
            <v-col cols="6">
              <v-text-field
                dense
                variant="outlined"
                color="primary"
                label="Amount"
                background-color="white"
                hide-details
                :model-value="formatCurrency(payment.amount)"
                @change="
                  setFormatedCurrency(payment, 'amount', null, true, $event)
                "
                :rules="[isNumber]"
                :prefix="currencySymbol(invoice_doc.currency)"
                @focus="set_rest_amount(payment.idx)"
                :readonly="invoice_doc.is_return ? true : false"
              ></v-text-field>
            </v-col>
            <v-col
              :cols="
                6
                  ? (payment.type != 'Phone' ||
                      payment.amount == 0 ||
                      !request_payment_field)
                  : 3
              "
            >
              <v-btn
                block
                class=""
                color="primary"
                dark
                @click="set_full_amount(payment.idx)"
                >{{ payment.mode_of_payment }}</v-btn
              >
            </v-col>
            <v-col
              v-if="
                payment.type == 'Phone' &&
                payment.amount > 0 &&
                request_payment_field
              "
              :cols="3"
              class="pl-1"
            >
              <v-btn
                block
                class=""
                color="success"
                dark
                :disabled="payment.amount == 0"
                @click="
                  (phone_dialog = true),
                    (payment.amount = flt(payment.amount, 0))
                "
              >
                Request
              </v-btn>
            </v-col>
          </v-row>
        </div>

        <v-row
          class="pyments px-1 py-0"
          v-if="
            invoice_doc &&
            available_pioints_amount > 0 &&
            !invoice_doc.is_return
          "
        >
          <v-col cols="7">
            <v-text-field
              dense
              variant="outlined"
              color="primary"
              label="Pay from Customer Points"
              background-color="white"
              hide-details
              v-model="loyalty_amount"
              type="number"
              :prefix="currencySymbol(invoice_doc.currency)"
            ></v-text-field>
          </v-col>
          <v-col cols="5">
            <v-text-field
              dense
              outlined
              color="primary"
              label="Customer Points Balance"
              background-color="white"
              hide-details
              :model-value="formatFloat(available_pioints_amount)"
              :prefix="currencySymbol(invoice_doc.currency)"
              disabled
            ></v-text-field>
          </v-col>
        </v-row>

        <v-row
          class="pyments px-1 py-0"
          v-if="
            invoice_doc &&
            available_customer_credit > 0 &&
            !invoice_doc.is_return &&
            redeem_customer_credit
          "
        >
          <v-col cols="7">
            <v-text-field
              dense
              variant="outlined"
              disabled
              color="primary"
              label="Redeemed Customer Credit"
              background-color="white"
              hide-details
              v-model="redeemed_customer_credit"
              type="number"
              :prefix="currencySymbol(invoice_doc.currency)"
            ></v-text-field>
          </v-col>
          <v-col cols="5">
            <v-text-field
              dense
              variant="outlined"
              color="primary"
              label="Cash Credit Balance"
              background-color="white"
              hide-details
              :model-value="formatCurrency(available_customer_credit)"
              :prefix="currencySymbol(invoice_doc.currency)"
              disabled
            ></v-text-field>
          </v-col>
        </v-row>
        <v-divider></v-divider>


        <v-divider></v-divider>
        <v-row class="px-1 py-0" align="start" no-gutters>
          <v-col
            cols="6"
            v-if="
              pos_profile.posa_allow_write_off_change &&
              diff_payment > 0 &&
              !invoice_doc.is_return
            "
          >
            <v-switch
              class="my-0 py-0"
              v-model="is_write_off_change"
              flat
              label="Is it a write-off amount?"
            ></v-switch>
          </v-col>
          <v-col
            cols="4"
            v-if="pos_profile.posa_allow_credit_sale && !invoice_doc.is_return"
          >
            <v-switch
              v-model="is_credit_sale"
              variant="flat"
              label="Is it a credit sale?"
              class="my-0 py-0"
            ></v-switch>
          </v-col>
          <v-col
            cols="4"
            v-if="!invoice_doc.is_return && pos_profile.posa_use_customer_credit"
          >
            <v-switch
              v-model="redeem_customer_credit"
              flat
              label="Use Customer Credit"
              class="my-0 py-0"
              @change="get_available_credit($event.target.value)"
            ></v-switch>
          </v-col>
          <v-col
            cols="4"
          >
            <v-btn
              block
              large
              color="primary"
              dark
              :disabled="vaildatPayment"
              @click="emitPrintRequest"
            >Print Invoice</v-btn>
          </v-col>
          <v-col
            cols="6"
            v-if="invoice_doc.is_return && pos_profile.posa_use_cashback"
          >
            <v-switch
              v-model="is_cashback"
              flat
              label="Is it a cash refund?"
              class="my-0 py-0"
            ></v-switch>
          </v-col>
          <v-col cols="6" v-if="is_credit_sale">
            <v-menu ref="date_menu" v-model="date_menu" :close-on-content-click="false" transition="scale-transition">
              <template v-slot:activator="{ props: { on, attrs } }">
                <v-text-field
                  v-model="invoice_doc.due_date"
                  label="Due Date"
                  readonly
                  variant="outlined"
                  density="compact"
                  hide-details
                  v-bind="attrs"
                  v-on="on"
                  color="primary"
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
          </v-col>
        </v-row>
        <div
          v-if="
            invoice_doc &&
            available_customer_credit > 0 &&
            !invoice_doc.is_return &&
            redeem_customer_credit
          "
        >
          <v-row v-for="(row, idx) in customer_credit_dict" :key="idx">
            <v-col cols="4">
              <div class="pa-2 py-3">{{ row.credit_origin }}</div>
            </v-col>
            <v-col cols="4">
              <v-text-field
                dense
                variant="outlined"
                color="primary"
                label="Available Credit"
                background-color="white"
                hide-details
                :model-value="formatCurrency(row.total_credit)"
                disabled
                :prefix="currencySymbol(invoice_doc.currency)"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                dense
                variant="outlined"
                color="primary"
                label="Credit to Redeem"
                background-color="white"
                hide-details
                type="number"
                v-model="row.credit_to_redeem"
                :prefix="currencySymbol(invoice_doc.currency)"
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
        <v-divider></v-divider>
        <v-row class="pb-0 mb-2" align="start">
        </v-row>
      </div>
    </v-card>

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
    invoiceType: "Invoice",
    pos_settings: "",
    customer_info: "",
    quick_return: false,
    selected_return_payment_idx: null,
    readonly: false,
  }),

  computed: {
    total_payments() {
      let total = parseFloat(this.invoice_doc.loyalty_amount);
      if (this.invoice_doc && this.invoice_doc.payments) {
        this.invoice_doc.payments.forEach((payment) => {
          total += this.flt(payment.amount);
        });
      }

      total += this.flt(this.redeemed_customer_credit);

      if (!this.is_cashback) total = 0;

      return this.flt(total, this.currency_precision);
    },
    diff_payment() {
      let diff_payment = this.flt(
        this.invoice_doc.grand_total -
          this.total_payments,
        this.currency_precision
      );
      this.paid_change = -diff_payment;
      return diff_payment;
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
      return payments.find((payment) => payment.default == 1);
    },
    back_to_invoice() {
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
        method: "posawesome.posawesome.api.invoice.submit_invoice",
        args: {
          data: data,
          invoice: this.invoice_doc,
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
      // For quick return, save the index of the selected method
      if (this.quick_return || this.invoice_doc.is_return) {
        this.selected_return_payment_idx = idx;
        this.invoice_doc.payments.forEach((payment) => {
          payment.amount = payment.idx === idx ? this.invoice_doc.total : 0;
        });
      } else {
        this.invoice_doc.payments.forEach((payment) => {
          payment.amount = payment.idx == idx ? this.invoice_doc.grand_total : 0;
        });
      }
    },
    set_rest_amount(idx) {
      this.invoice_doc.payments.forEach((payment) => {
        if (
          payment.idx == idx &&
          payment.amount == 0 &&
          this.diff_payment > 0
        ) {
          payment.amount = this.diff_payment;
        }
      });
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
      if (!vm.invoice_doc) {
        return;
      }
      frappe.call({
        method: "posawesome.posawesome.api.customer.get_customer_addresses",
        args: { customer: vm.invoice_doc.customer },
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
          method: "posawesome.posawesome.api.posapp.create_payment_request",
          args: {
            doc: vm.invoice_doc,
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
        
        // Ensure payments array exists
        if (!this.invoice_doc.payments || !Array.isArray(this.invoice_doc.payments)) {
          evntBus.emit("show_mesage", {
            text: "No payments array in invoice document",
            color: "error",
          });
          this.invoice_doc.payments = [];
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
          this.is_return = true;
          invoice_doc.payments.forEach((payment) => {
            payment.amount = 0;
            payment.base_amount = 0;
          });
        }
        this.loyalty_amount = 0;
        this.get_addresses();
      });
      evntBus.on("register_pos_profile", (data) => {
        this.pos_profile = data.pos_profile;
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