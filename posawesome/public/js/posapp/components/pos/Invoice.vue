<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div>
    <v-card
      class="cards my-0 py-0 mt-1 grey lighten-5 d-flex flex-column flex-grow-1"
      style="min-height: 0;"
    >
  <v-row align="stretch" class="items px-2 py-0" no-gutters>
        <v-col cols="12" class="pr-1">
          <div class="customer-container">
            <Customer></Customer>
          </div>
        </v-col>
      </v-row>
      <v-row
        align="center"
        class="items px-2 py-0 mt-0 pt-0"
        v-if="pos_profile.posa_use_delivery_charges"
      >
        <v-col cols="8" class="pb-0 mb-0 pr-0 pt-0">
          <v-autocomplete
            dense
            clearable
            auto-select-first
            outlined
            color="primary"
            label="Delivery Charges"
            v-model="selcted_delivery_charges"
            :items="delivery_charges"
            item-title="name"
            return-object
            background-color="white"
            no-data-text="No delivery charges available"
            hide-details
            :filter="deliveryChargesFilter"
            :disabled="readonly"
            @change="update_delivery_charges"
          >
            <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props">
                  <v-list-item-title
                    class="primary--text subtitle-1"
                    v-html="item.name"
                  ></v-list-item-title>
                  <v-list-item-subtitle
                    v-html="`Price: ${item.rate}`"
                  ></v-list-item-subtitle>
                </v-list-item>
            </template>
          </v-autocomplete>
        </v-col>
        <v-col cols="4" class="pb-0 mb-0 pt-0">
          <v-text-field
            dense
            outlined
            color="primary"
            label="Delivery Charges Rate"
            background-color="white"
            hide-details
            :value="formatCurrency(delivery_charges_rate)"
            :prefix="currencySymbol(pos_profile.currency)"
            disabled
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row
        align="center"
        class="items px-2 py-0 mt-0 pt-0"
        v-if="pos_profile.posa_allow_change_posting_date"
      >
        <v-col
          v-if="pos_profile.posa_allow_change_posting_date"
          cols="4"
          class="pb-1"
        >
          <v-menu
            ref="invoice_posting_date"
            v-model="invoice_posting_date"
            :close-on-content-click="false"
            transition="scale-transition"
            dense
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="posting_date"
                label="Posting Date"
                readonly
                outlined
                dense
                background-color="white"
                clearable
                color="primary"
                hide-details
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="posting_date"
              no-title
              scrollable
              color="primary"
              :min="
                frappe.datetime.add_days(frappe.datetime.now_date(true), -7)
              "
              :max="frappe.datetime.add_days(frappe.datetime.now_date(true), 7)"
              @input="invoice_posting_date = false"
            >
            </v-date-picker>
          </v-menu>
        </v-col>
      </v-row>

  <div class="my-0 py-0 invoice-items-scrollable">
          <v-data-table
            :headers="dynamicHeaders"
            :items="items"
            item-key="posa_row_id"
            item-value="posa_row_id"
            class="elevation-0 invoice-table"
            hide-default-footer
            :items-per-page="-1"
            density="compact"
          >
            <template v-slot:item.qty="{ item }">
              <div class="quantity-controls">
                <v-btn
                  size="small"
                  variant="flat"
                  color="warning"
                  class="quantity-btn quantity-minus-btn"
                  @click="decreaseQuantity(item)"
                  :disabled="item.qty <= 0"
                >
                  −
                </v-btn>
              <input
                type="number"
                v-model.number="item.qty"
                @input="onQtyInput(item)"
                @change="onQtyChange(item)"
                @blur="onQtyChange(item)"
                class="quantity-input"
                placeholder="0"
              />
                <v-btn
                  size="small"
                  variant="flat"
                  color="success"
                  class="quantity-btn quantity-plus-btn"
                  @click="increaseQuantity(item)"
                >
                  +
                </v-btn>
              </div>
            </template>
              <template v-slot:item.rate="{ item }">
                <!-- Price input field -->
                <v-text-field
                  dense
                  variant="outlined"
                  color="primary"
                  background-color="white"
                  hide-details
                  :prefix="currencySymbol(pos_profile.currency)"
                  :model-value="formatCurrency(item.rate)"
                  @change="
                    [
                      setFormatedCurrency(
                        item,
                        'rate',
                        null,
                        false,
                        $event
                      ),
                    ]
                  "
                  @blur="
                    [
                      setFormatedCurrency(
                        item,
                        'rate',
                        null,
                        false,
                        $event
                      ),
                    ]
                  "
                  @keyup.enter="
                    [
                      setFormatedCurrency(
                        item,
                        'rate',
                        null,
                        false,
                        $event
                      ),
                    ]
                  "
                  :rules="[isNumber]"
                  id="rate"
                  :disabled="
                    !!item.posa_is_offer ||
                    !!item.posa_is_replace ||
                    !!item.posa_offer_applied ||
                    !!invoice_doc.is_return
                  "
                  style="min-width: 80px; max-width: 110px;"
                  class="rate-input"
                  placeholder="0.00"
                ></v-text-field>
              </template>
            <template v-slot:item.discount_percentage="{ item }">
              <v-text-field
                dense
                variant="outlined"
                :color="item.discount_percentage > 0 ? 'orange' : 'primary'"
                :background-color="item.discount_percentage > 0 ? '#FFF3E0' : 'white'"
                hide-details
                :model-value="formatFloat(item.discount_percentage || 0)"
                @change="setDiscountPercentage(item, $event)"
                @blur="setDiscountPercentage(item, $event)"
                @keyup.enter="setDiscountPercentage(item, $event)"
                :rules="[isNumber]"
                :disabled="
                  !!item.posa_is_offer ||
                  !!item.posa_is_replace ||
                  !!item.posa_offer_applied ||
                  !pos_profile.posa_allow_user_to_edit_item_discount ||
                  !!invoice_doc.is_return
                "
                style="min-width: 60px; max-width: 90px;"
                class="discount-input"
                placeholder="0.00"
                suffix="%"
                type="number"
                min="0"
                :max="pos_profile.posa_item_max_discount_allowed || 100"
                step="0.01"
                id="discount_percentage"
              ></v-text-field>
            </template>
            <template v-slot:item.discount_amount="{ item }">
              <div class="discount-amount-display" :class="{ 'discount-zero': !getDiscountAmount(item) || getDiscountAmount(item) <= 0 }">
                <span>{{ currencySymbol(pos_profile.currency) }}</span>
                {{ formatCurrency(getDiscountAmount(item)) }}
              </div>
            </template>
            <template v-slot:item.amount="{ item }"
              >{{ currencySymbol(pos_profile.currency) }}
              {{
                formatCurrency(
                  flt(item.qty, float_precision) *
                    flt(item.rate, currency_precision)
                )
              }}</template
            >
            <template v-slot:item.posa_is_offer="{ item }">
              <v-checkbox
                :model-value="!!item.posa_is_offer || !!item.posa_is_replace"
                :disabled="true"
              ></v-checkbox>
            </template>

            <template v-slot:item.actions="{ item }">
              <v-btn
                :disabled="!!item.posa_is_offer || !!item.posa_is_replace"
                icon
                color="error"
                size="small"
                class="delete-item-btn"
                @click.stop="remove_item(item)"
                title="Delete item"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
            <template v-slot:item.price_list_rate="{ item }">
              <div :class="{ 'discounted-price': flt(item.rate, currency_precision) < flt(item.base_rate, currency_precision) }">
                {{ formatCurrency(item.price_list_rate) }}
              </div>
            </template>
          </v-data-table>
      </div>
    </v-card>
    <v-card class="cards mb-0 mt-3 py-1 px-0 grey lighten-5" style="width: 100%; margin: 0;">
      <!-- Row 1: All Fields with Equal Width Distribution -->
      <v-row no-gutters align="center" class="ma-0">
        <v-col class="pa-0 ma-0 equal-width-field">
          <v-text-field
            :model-value="formatFloat(total_qty)"
            label="Total Quantity"
            variant="outlined"
            dense
            readonly
            hide-details
            color="accent"
            class="ma-0"
            style="margin: 0 1px !important;"
          ></v-text-field>
        </v-col>
        <v-col class="pa-0 ma-0 equal-width-field">
          <v-text-field
            v-model.number="additional_discount_percentage"
            @blur="update_discount_umount"
            label="Invoice Discount %"
            suffix="%"
            ref="percentage_discount"
            variant="outlined"
            dense
            color="warning"
            hide-details
            class="ma-0"
            style="margin: 0 1px !important;"
            type="number"
            step="0.01"
            min="0"
            :max="pos_profile.posa_invoice_max_discount_allowed || 100"
          ></v-text-field>
        </v-col>
        <v-col class="pa-0 ma-0 equal-width-field">
          <v-text-field
            :model-value="formatCurrency(total_items_discount_amount)"
            :prefix="currencySymbol(pos_profile.currency)"
            label="Items Discount"
            variant="outlined"
            dense
            color="warning"
            readonly
            hide-details
            class="ma-0"
            style="margin: 0 1px !important;"
          ></v-text-field>
        </v-col>
        <v-col class="pa-0 ma-0 equal-width-field">
          <v-text-field
            :model-value="formatCurrency(invoice_doc.total)"
            label="Total Before Discount"
            variant="outlined"
            dense
            readonly
            hide-details
            color="primary"
            :prefix="currencySymbol(pos_profile.currency)"
            class="ma-0"
            style="margin: 0 1px !important;"
          ></v-text-field>
        </v-col>
        <v-col class="pa-0 ma-0 equal-width-field">
          <v-text-field
            :model-value="formatCurrency(invoice_doc.net_total)"
            label="Net Total (No Tax)"
            variant="outlined"
            dense
            readonly
            hide-details
            color="secondary"
            :prefix="currencySymbol(pos_profile.currency)"
            class="ma-0"
            style="margin: 0 1px !important;"
          ></v-text-field>
        </v-col>
        <v-col class="pa-0 ma-0 equal-width-field">
          <v-text-field
            :model-value="formatCurrency(invoice_doc.total_taxes_and_charges)"
            label="Tax"
            variant="outlined"
            dense
            readonly
            hide-details
            color="info"
            :prefix="currencySymbol(pos_profile.currency)"
            class="ma-0"
            style="margin: 0 1px !important;"
          ></v-text-field>
        </v-col>
        <v-col class="pa-0 ma-0 equal-width-field">
          <v-text-field
            :model-value="formatCurrency(invoice_doc.grand_total)"
            label="Invoice Total"
            variant="outlined"
            dense
            readonly
            hide-details
            color="success"
            :prefix="currencySymbol(pos_profile.currency)"
            class="ma-0"
            style="margin: 0 1px !important;"
          ></v-text-field>
        </v-col>
      </v-row>

      <!-- Row 2: All Action Buttons in Single Row -->
      <v-row no-gutters class="mt-1 ma-0 action-buttons-row">
        <v-col class="action-button">
          <v-btn
            block
            color="primary"
            variant="flat"
            :disabled="!canPrintInvoice"
            @click="printInvoice"
          >
            Print Invoice
          </v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="success"
            variant="flat"
            @click="show_payment"
          >
            Pay
          </v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="secondary"
            dark
            :disabled="!pos_profile.posa_allow_return"
            @click="open_returns"
          >Return</v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="purple"
            dark
            variant="flat"
            :disabled="!pos_profile.posa_allow_quick_return"
            @click="quick_return"
          >Quick Return</v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="error"
            dark
            @click="cancel_invoice"
          >Cancel</v-btn>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from "../../bus";
import format from "../../format";
import Customer from "./Customer.vue";

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],
  components: { Customer },
  // ===== SECTION 3: DATA =====
  data() {
    return {
      pos_profile: "",
      pos_opening_shift: "",
      stock_settings: "",
      invoice_doc: "",
      return_doc: "",
      customer: "",
      customer_info: {},
      discount_amount: 0,
      additional_discount_percentage: 0,
      total_tax: 0,
      items: [],
      posOffers: [],
      posa_offers: [],
      posa_coupons: [],
      allItems: [],
      discount_percentage_offer_name: null,
      itemsPerPage: 1000,
      float_precision: 2,
      currency_precision: 2,
      new_line: false,
      delivery_charges: [],
      delivery_charges_rate: 0,
      selcted_delivery_charges: {},
      invoice_posting_date: false,
      posting_date: frappe.datetime.nowdate(),
      quick_return_value: false,
      _autoUpdateInProgress: false,
      _autoUpdateTimer: null,
      items_headers: [
        { title: "Delete", key: "actions", align: "center", sortable: false },
        { title: "Total", key: "amount", align: "center" },
        { title: "Disc. Amount", key: "discount_amount", align: "center" },
        { title: "Disc. %", key: "discount_percentage", align: "center" },
        { title: "After Disc.", key: "rate", align: "center" },
        { title: "Price", key: "price_list_rate", align: "center" },
        { title: "Unit", key: "uom", align: "center" },
        { title: "Qty", key: "qty", align: "center" },
        { title: "Item Name", align: "end", sortable: true, key: "item_name" },
      ],
      _cachedCalculations: new Map(),
      _lastCalculationTime: 0,
      _calculationDebounceTimer: null,
    };
  },

  // ===== SECTION 4: COMPUTED =====
  computed: {
    dynamicHeaders() {
      let headers = [...this.items_headers];
      
      if (!this.pos_profile?.posa_display_discount_percentage) {
        headers = headers.filter(header => header.key !== 'discount_percentage');
      }
      
      if (!this.pos_profile?.posa_display_discount_amount) {
        headers = headers.filter(header => header.key !== 'discount_amount');
      }
      
      if (!this.pos_profile?.posa_allow_user_to_edit_item_discount) {
        headers = headers.filter(header => header.key !== 'rate');
      }
      
      return headers;
    },
    readonly() {
      return this.invoice_doc?.is_return || false;
    },
    total_qty() {
      if (!this.invoice_doc?.items) return 0;
      return this.invoice_doc.items.reduce((sum, item) => sum + (item.qty || 0 ), 0);
    },
    Total() {
      return this.invoice_doc?.total || 0;
    },
    subtotal() {
      this.close_payments();
      return this.invoice_doc?.net_total || 0;
    },
    total_items_discount_amount() {
      return this.invoice_doc?.total_items_discount || 0;
    },
    TaxAmount() {
      return this.invoice_doc?.total_taxes_and_charges || 0;
    },
    DiscountAmount() {
      return this.invoice_doc?.discount_amount || 0;
    },
    GrandTotal() {
      return this.invoice_doc?.grand_total || 0;
    },
    defaultPaymentMode() {
      const invoicePayments = (this.invoice_doc && Array.isArray(this.invoice_doc.payments)) ? this.invoice_doc.payments : [];
      const profilePayments = (this.pos_profile && Array.isArray(this.pos_profile.payments)) ? this.pos_profile.payments : [];
      const payments = invoicePayments.length ? invoicePayments : profilePayments;
      const defaultRow = payments.find(payment => payment.default == 1);
      return defaultRow ? defaultRow.mode_of_payment : null;
    },
    canPrintInvoice() {
      if (this.readonly) return false;
      if (!this.items || !this.items.length) return false;
      const payments = (this.invoice_doc && Array.isArray(this.invoice_doc.payments)) ? this.invoice_doc.payments : [];
      const hasPositive = payments.some(payment => this.flt(payment.amount) > 0);
      if (hasPositive) return true;
      return !!this.defaultPaymentMode;
    },
  },

  // ===== SECTION 5: METHODS =====
  methods: {
    
    onQtyChange(item) {
      try {
        const newQty = Number(item.qty) || 0;
        item.qty = newQty;
        this.refreshTotals();
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "Error updating quantity",
          color: "error",
        });
      }
    },
    onQtyInput(item) {
      item.qty = Number(item.qty) || 0;
      // Just update the display, no need to recalculate discount
      this.refreshTotals();
    },
    refreshTotals() {
      this._cachedCalculations.clear();
      this.$forceUpdate();
    },
    
    increaseQuantity(item) {
      try {
        const currentQty = Number(item.qty) || 0;
        const newQty = currentQty + 1;
        
        item.qty = newQty;
        
        this._cachedCalculations.clear();
        this.$forceUpdate();
        
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "Error increasing quantity",
          color: "error",
        });
      }
    },
    
    decreaseQuantity(item) {
      try {
        const currentQty = Number(item.qty) || 0;
        const newQty = Math.max(0, currentQty - 1);
        
        item.qty = newQty;
        
        if (newQty === 0) {
          this.remove_item(item);
          return;
        }
        
        this._cachedCalculations.clear();
        this.$forceUpdate();
        
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "Error decreasing quantity",
          color: "error",
        });
      }
    },

    getDiscountAmount(item) {
      if (!item) return 0;
      
      if (item.discount_amount) {
        return flt(item.discount_amount) || 0;
      }

      const basePrice = flt(item.price_list_rate) || flt(item.rate) || 0;
      const discountPercentage = flt(item.discount_percentage) || 0;
      
      if (discountPercentage > 0 && basePrice > 0) {
        let result = 0;
        frappe.call({
          method: "posawesome.posawesome.api.invoice.calculate_item_discount_amount",
          args: {
            price_list_rate: basePrice,
            discount_percentage: discountPercentage
          },
          async: false,
          callback: (r) => {
            result = r.message || 0;
          }
        });
        return result;
      }
      
      return 0;
    },

    quick_return() {
      if (!this.pos_profile.posa_allow_quick_return) {
        evntBus.emit("show_mesage", {
          text: "Quick return is not enabled in POS profile",
          color: "error",
        });
        return;
      }
      
      if (!this.customer) {
        evntBus.emit("show_mesage", {
          text: "No customer!",
          color: "error",
        });
        return;
      }
      if (!this.items.length) {
        evntBus.emit("show_mesage", {
          text: "No items!",
          color: "error",
        });
        return;
      }
      if (!this.validate()) {
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
        
        if (this.items.length === 0 && this.invoice_doc && this.invoice_doc.name) {
          this.delete_draft_invoice();
        } else if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      }
    },

    add_one(item) {
      item.qty++;
      if (item.qty == 0) {
        this.remove_item(item);
      } else {
        this.$forceUpdate();
        
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      }
    },
    subtract_one(item) {
      item.qty--;
      if (item.qty == 0) {
        this.remove_item(item);
      } else {
        this.$forceUpdate();
        
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      }
    },

  add_item(item) {
      if (!item || !item.item_code) {
        evntBus.emit("show_mesage", {
          text: "Item data is incorrect or missing",
          color: "error",
        });
        return;
      }
      
      const new_item = Object.assign({}, item);
      
      if (!new_item.rate && !new_item.price_list_rate) {
        evntBus.emit("show_mesage", {
          text: `No price for item '${new_item.item_name || new_item.item_code}'`,
          color: "error",
        });
        return;
      }
      
      if (!new_item.uom) {
        new_item.uom = new_item.stock_uom || 'Nos';
      }
      
      const existing_item = this.items.find(existing => {
        const basicMatch = existing.item_code === new_item.item_code &&  existing.uom === new_item.uom;
        
        if (existing.batch_no || new_item.batch_no) {
          return basicMatch && existing.batch_no === new_item.batch_no;
        }
        return basicMatch;
      });
      
      if (existing_item) {
        const existing_idx = this.items.indexOf(existing_item);
        
        if (this.invoice_doc && this.invoice_doc.name) {
          frappe.call({
            method: "posawesome.posawesome.api.invoice.update_item_in_invoice",
            args: {
              invoice_name: this.invoice_doc.name,
              item_idx: existing_idx,
              qty: flt(existing_item.qty) + flt(new_item.qty) // Python will handle this
            },
            callback: (r) => {
              if (r.message) {
                this.invoice_doc = r.message;
                this.items = r.message.items;
              }
            }
          });
        } else {
          existing_item.qty = flt(existing_item.qty) + flt(new_item.qty);
        }
      } else {
        new_item.posa_row_id = this.generateRowId();
        new_item.posa_offers = "[]";
        new_item.posa_offer_applied = 0;
        new_item.posa_is_offer = 0;
        new_item.posa_is_replace = 0;
        new_item.is_free_item = 0;

        const rate = new_item.price_list_rate || new_item.rate || 0;
        
        if (this.invoice_doc && this.invoice_doc.name) {
          frappe.call({
            method: "posawesome.posawesome.api.invoice.add_item_to_invoice",
            args: {
              invoice_name: this.invoice_doc.name,
              item_code: new_item.item_code,
              qty: new_item.qty || 1,
              rate: rate,
              uom: new_item.uom
            },
            callback: (r) => {
              if (r.message) {
                this.invoice_doc = r.message;
                this.items = r.message.items;
              }
            }
          });
        } else {
          new_item.rate = rate;
          new_item.price_list_rate = rate;
          new_item.base_rate = rate;
          this.items.push(new_item);
        }
      }
      
      if (this.items.length === 1 && !this.invoice_doc) {
        this.create_draft_invoice();
      }
    },
    generateRowId() {
      return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    async create_draft_invoice() {
      try {
        const doc = this.get_invoice_doc();
        const result = await this.update_invoice(doc);
        
        if (result) {
          this.invoice_doc = result;
          evntBus.emit("show_mesage", {
            text: "Draft invoice created",
            color: "success",
          });
        }
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "Error creating draft invoice",
          color: "error",
        });
      }
    },

    async auto_update_invoice() {
      if (this.invoice_doc && this.invoice_doc.name && !this.invoice_doc.submitted_for_payment) {
        if (this._autoUpdateInProgress) {
          return;
        }
        
        this._autoUpdateInProgress = true;
        
        try {
          const doc = this.get_invoice_doc();
          const result = await this.update_invoice(doc);
          if (result) {
            this.invoice_doc = result;
            evntBus.emit("show_mesage", {
              text: "Draft invoice updated",
              color: "info",
            });
          }
        } catch (error) {
          if (error.message && error.message.includes('Document has been modified')) {
            try {
              await this.reload_invoice();
            } catch (reloadError) {
            }
            }
          } finally {
            setTimeout(() => {
              this._autoUpdateInProgress = false;
            }, 1000); // Wait one second before allowing another update
          }
      }
    },

    async reload_invoice() {
      if (this.invoice_doc && this.invoice_doc.name) {
        try {
          const result = await frappe.call({
            method: "frappe.client.get",
            args: {
              doctype: "Sales Invoice",
              name: this.invoice_doc.name
            }
          });
          
          if (result.message) {
              this.invoice_doc = result.message;
              if (result.message.items) {
              this.items = result.message.items;
            }
          }
        } catch (error) {
        }
      }
    },

    debounced_auto_update() {
      if (this._autoUpdateTimer) {
        clearTimeout(this._autoUpdateTimer);
      }
      
      this._autoUpdateTimer = setTimeout(() => {
        this.auto_update_invoice();
      }, 500);
    },

    get_new_item(item) {
      const new_item = { ...item };
      if (!item.qty) {
        item.qty = 1;
      }
      if (!item.posa_is_offer) {
        item.posa_is_offer = 0;
      }
      if (!item.posa_is_replace) {
        item.posa_is_replace = "";
      }
      new_item.stock_qty = item.qty;
      new_item.discount_amount = 0;
      new_item.discount_percentage = 0;
      new_item.discount_amount_per_item = 0;
      new_item.price_list_rate = item.rate;
      new_item.base_rate = item.rate || item.price_list_rate || 0; // Save the base rate for reference
      new_item.qty = item.qty;
      new_item.uom = item.uom ? item.uom : item.stock_uom;
      new_item.uom = typeof new_item.uom === "object" && new_item.uom !== null && new_item.uom.uom ? new_item.uom.uom : new_item.uom;
      new_item.actual_batch_qty = "";
      new_item.conversion_factor = 1;
      
      new_item.item_uoms = item.item_uoms || [];
      
      if (new_item.item_uoms.length === 0 || !new_item.item_uoms.some(uom => uom.uom === item.stock_uom)) {
        new_item.item_uoms.unshift({ uom: item.stock_uom, conversion_factor: 1 });
      }
      
      new_item.item_uoms = new_item.item_uoms.map(uom => {
        if (typeof uom === 'string') {
          return { uom: uom, conversion_factor: 1 };
        } 
        else if (typeof uom === 'object' && uom !== null) {
          return { 
            uom: uom.uom || uom.name || uom.toString(), 
            conversion_factor: parseFloat(uom.conversion_factor) || 1 
          };
        }
        else {
          return { uom: item.stock_uom || 'Nos', conversion_factor: 1 };
        }
      }).filter(uom => uom && uom.uom); // Exclude invalid units
      
      if (new_item.item_uoms && Array.isArray(new_item.item_uoms)) {
        const selected_uom_obj = new_item.item_uoms.find(uom => uom.uom === new_item.uom);
        if (selected_uom_obj) {
          new_item.conversion_factor = parseFloat(selected_uom_obj.conversion_factor);
        }
      }
      
      new_item.posa_offers = JSON.stringify([]);
      new_item.posa_offer_applied = 0;
      new_item.posa_is_offer = item.posa_is_offer;
      new_item.posa_is_replace = item.posa_is_replace || null;
      new_item.is_free_item = 0;
      new_item.posa_notes = "";
      new_item.posa_delivery_date = "";
      new_item.posa_row_id = this.makeid(20);
   
      if (
        (!this.pos_profile.posa_auto_set_batch && new_item.has_batch_no) ||
        new_item.has_serial_no
      ) {
        this.expanded.push(new_item);
      }
      return new_item;
    },

    cancel_invoice() {
      if (this.invoice_doc && this.invoice_doc.name) {
        frappe.call({
          method: "frappe.client.delete",
          args: {
            doctype: "Sales Invoice",
            name: this.invoice_doc.name
          },
          callback: (r) => {
            if (r.message) {
              evntBus.emit("show_mesage", {
                text: "Draft invoice cancelled",
                color: "success",
              });
            }
          }
        });
      }
      
      this.invoiceType = "Invoice";
      this.invoiceTypes = ["Invoice"];
      this.posting_date = frappe.datetime.nowdate();
      this.items = [];
      this.posa_offers = [];
      evntBus.emit("set_pos_coupons", []);
      this.posa_coupons = [];
      this.customer = this.pos_profile.customer;
      this.invoice_doc = "";
      this.return_doc = "";
      this.discount_amount = 0;
      this.additional_discount_percentage = 0;
      this.delivery_charges_rate = 0;
      this.selcted_delivery_charges = {};
      evntBus.emit("set_customer_readonly", false);
      
      evntBus.emit("show_payment", "false");
    },

    delete_draft_invoice() {
      if (this.invoice_doc && this.invoice_doc.name) {
        frappe.call({
          method: "frappe.client.delete",
          args: {
            doctype: "Sales Invoice",
            name: this.invoice_doc.name
          },
          callback: (r) => {
            if (r.message) {
              evntBus.emit("show_mesage", {
                text: "Draft invoice deleted",
                color: "success",
              });
              this.invoice_doc = "";
              this.return_doc = "";
              this.discount_amount = 0;
              this.additional_discount_percentage = 0;
              this.delivery_charges_rate = 0;
              this.selcted_delivery_charges = {};
              this.posa_offers = [];
              evntBus.emit("set_pos_coupons", []);
              this.posa_coupons = [];
            }
          }
        });
      }
    },

    new_invoice(data = {}) {
      let old_invoice = null;
      evntBus.emit("set_customer_readonly", false);
      this.posa_offers = [];
      evntBus.emit("set_pos_coupons", []);
      this.posa_coupons = [];
      this.return_doc = "";
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
        this.customer = this.pos_profile.customer;
        this.invoice_doc = "";
        this.discount_amount = 0;
        this.additional_discount_percentage = 0;
        this.invoiceType =  "Invoice";
        this.invoiceTypes = ["Invoice"];
      } else {
        if (data.is_return) {
          evntBus.emit("set_customer_readonly", true);
          this.invoiceType = "Return";
          this.invoiceTypes = ["Return"];
        }
        this.invoice_doc = data;
        this.items = data.items;
        
        this.update_items_details(this.items);
        
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
        this.customer = data.customer;
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

    get_invoice_doc() {
      let doc = {};
      if (this.invoice_doc.name && !this.invoice_doc.submitted_for_payment) {
        doc = { ...this.invoice_doc };
      }
      doc.doctype = "Sales Invoice";
      doc.is_pos = 1;
      doc.ignore_pricing_rule = 1;
      doc.company = doc.company || this.pos_profile.company;
      doc.pos_profile = doc.pos_profile || this.pos_profile.name;
      doc.currency = doc.currency || this.pos_profile.currency;
      doc.naming_series = doc.naming_series || this.pos_profile.naming_series;
      doc.customer = this.customer;
      doc.items = this.get_invoice_items();
      doc.discount_amount = flt(this.discount_amount);
      doc.additional_discount_percentage = flt(this.additional_discount_percentage);
      doc.posa_pos_opening_shift = this.pos_opening_shift.name;
      doc.payments = this.get_payments();
      doc.taxes = [];
      doc.is_return = this.invoice_doc.is_return;
      doc.return_against = this.invoice_doc.return_against;
      doc.posa_offers = this.posa_offers;
      doc.posa_coupons = this.posa_coupons;
      doc.posting_date = this.posting_date;
      return doc;
    },

    get_invoice_items() {
      return this.items.map(item => {
        return {
          item_code: item.item_code,
          posa_row_id: item.posa_row_id,
          posa_offers: item.posa_offers,
          posa_offer_applied: item.posa_offer_applied,
          posa_is_offer: item.posa_is_offer,
          posa_is_replace: item.posa_is_replace,
          is_free_item: item.is_free_item,
          qty: item.qty || 1,
          rate: item.rate || item.price_list_rate || 0,
          uom: item.uom || item.stock_uom,
          conversion_factor: item.conversion_factor || 1,
          serial_no: item.serial_no,
          discount_percentage: item.discount_percentage || 0,
          discount_amount: item.discount_amount || 0,
          batch_no: item.batch_no,
          posa_notes: item.posa_notes,
          posa_delivery_date: item.posa_delivery_date,
          price_list_rate: item.price_list_rate || item.rate || 0,
        };
      });
    },

    get_payments() {
      const payments = [];
      if (this.pos_profile && this.pos_profile.payments && Array.isArray(this.pos_profile.payments)) {
        this.pos_profile.payments.forEach((payment) => {
          payments.push({
            amount: 0,
            mode_of_payment: payment.mode_of_payment,
            default: payment.default,
            account: "",
          });
        });
      }
      return payments;
    },

    update_invoice(doc) {
      const vm = this;
      return new Promise((resolve, reject) => {
        frappe.call({
          method: "posawesome.posawesome.api.invoice.update_invoice",
          args: {
            data: doc,
          },
          async: true,
          callback: function (r) {
            if (r.message) {
              vm.invoice_doc = r.message;
              resolve(vm.invoice_doc);
            } else {
              reject(new Error('Failed to update invoice'));
            }
          },
          error: function (err) {
            if (err.message && err.message.includes('Document has been modified')) {
              evntBus.emit('show_mesage', {
                text: 'Invoice was modified elsewhere, will reload',
                color: 'warning'
              });
              
              vm.reload_invoice().then(() => {
                resolve(vm.invoice_doc);
              }).catch((reloadError) => {
                reject(reloadError);
              });
            } else {
              evntBus.emit('show_mesage', {
                text: 'Error updating invoice',
                color: 'error'
              });
              reject(err);
            }
          }
        });
      });
    },

    async process_invoice() {
      const doc = this.get_invoice_doc();
      
      try {
        const result = await this.update_invoice(doc);
        return result;
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error processing invoice',
          color: 'error'
        });
        throw error;
      }
    },

    async show_payment() {
      if (this.readonly) return;
      if (!this.customer) {
        evntBus.emit("show_mesage", {
          text: "No customer!",
          color: "error",
        });
        return;
      }
      if (!this.items.length) {
        evntBus.emit("show_mesage", {
          text: "No items in invoice!",
          color: "error",
        });
        return;
      }

      evntBus.emit("show_loading", {
        text: "Preparing payment screen...",
        color: "info"
      });

      try {
        const invoice_doc = await this.process_invoice();
        
        evntBus.emit("send_invoice_doc_payment", invoice_doc);
        evntBus.emit("show_payment", "true");
        
        this.posa_offers = [];
        this.posa_coupons = [];
        this._cachedCalculations.clear();
        
        if (this.pos_profile.posa_clear_customer_after_payment) {
          this.customer = this.pos_profile.customer;
          evntBus.emit("set_customer", this.customer);
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

    validate() {
      if (!this.items || this.items.length === 0) {
        return true;
      }
      
      let isValid = true;
      
      frappe.call({
        method: "posawesome.posawesome.api.invoice.validate_invoice_items",
        args: {
          items_data: this.items,
          pos_profile_name: this.pos_profile.name,
          stock_settings: this.stock_settings
        },
        async: false,
        callback: (r) => {
          const result = r.message;
          if (!result.valid) {
            if (result.errors && result.errors.length > 0) {
              evntBus.emit("show_mesage", {
                text: `${result.errors[0].item}: ${result.errors[0].error}`,
                color: "error",
              });
            }
            isValid = false;
          }
        },
        error: () => {
          isValid = false;
        }
      });
      
      return isValid;
    },

    get_draft_invoices() {
      const vm = this;
      frappe.call({
        method: "posawesome.posawesome.api.invoice.get_draft_invoices",
        args: {
          pos_opening_shift: this.pos_opening_shift.name,
        },
        async: true,
        callback: function (r) {
          if (r.message) {
            evntBus.emit("open_drafts", r.message);
          }
        },
        error: function (err) {
          evntBus.emit('show_mesage', {
            text: 'Error fetching draft invoices',
            color: 'error'
          });
        }
      });
    },

    open_returns() {
      if (!this.pos_profile.posa_allow_return) {
        evntBus.emit("show_mesage", {
          text: "Returns are not enabled in POS profile",
          color: "error",
        });
        return;
      }
      
      evntBus.emit("open_returns", {
        pos_profile: this.pos_profile,
        pos_opening_shift: this.pos_opening_shift
      });
    },

    close_payments() {
      evntBus.emit("show_payment", "false");
    },

    update_items_details(items) {
      if (!items.length > 0) {
        return;
      }
      const vm = this;
      if (!vm.pos_profile) return
      frappe.call({
        method: "posawesome.posawesome.api.get_items.get_items",
        async: true,
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.pos_profile.selling_price_list,
          item_group: "",
          search_value: "", // Empty search to get all items
          customer: vm.customer,
        },
        callback: function (r) {
          if (r.message) {
            const updatedItemsMap = new Map();
            r.message.forEach(item => {
              updatedItemsMap.set(item.item_code, item);
            });
            
            items.forEach((item) => {
              const updated_item = updatedItemsMap.get(item.item_code);
              if (updated_item) {
                item.actual_qty = updated_item.actual_qty;
                item.serial_no_data = updated_item.serial_no_data;
                item.batch_no_data = updated_item.batch_no_data;
                item.rate = updated_item.rate;
                item.currency = updated_item.currency;
                
                item.item_uoms = (updated_item.item_uoms || []).map(uom => {
                  if (typeof uom === 'string') {
                    return { uom: uom, conversion_factor: 1 };
                  } else if (typeof uom === 'object' && uom !== null) {
                    return { 
                      uom: uom.uom || uom.name || uom.toString(), 
                      conversion_factor: parseFloat(uom.conversion_factor) || 1 
                    };
                  } else {
                    return { uom: item.stock_uom || 'Nos', conversion_factor: 1 };
                  }
                }).filter(uom => uom && uom.uom);
                
                item.has_batch_no = updated_item.has_batch_no;
                item.has_serial_no = updated_item.has_serial_no;
              }
            });
            
          }
        },
        error: function (err) {
          evntBus.emit('show_mesage', {
            text: 'Error updating item details',
            color: 'error'
          });
        }
      });
    },

    update_item_detail(item) {
      if (!item.item_code || this.invoice_doc.is_return) {
        return;
      }
      const vm = this;
      frappe.call({
        method: "posawesome.posawesome.api.get_items.get_items",
        args: {
          pos_profile: this.pos_profile,
          price_list: this.pos_profile.selling_price_list,
          item_group: "",
          search_value: item.item_code, // Search for specific item
          customer: this.customer,
        },
        callback: function (r) {
          if (r.message && r.message.length > 0) {
            const data = r.message[0]; // Get first item from array
            if (data.batch_no_data) {
              item.batch_no_data = data.batch_no_data;
            }
            if (
              item.has_batch_no &&
              vm.pos_profile.posa_auto_set_batch &&
              !item.batch_no &&
              data.batch_no_data
            ) {
              item.batch_no_data = data.batch_no_data;
              vm.set_batch_qty(item, item.batch_no, false);
            }
            if (data.has_pricing_rule) {
            } else if (
              vm.pos_profile.posa_apply_customer_discount &&
              vm.customer_info.posa_discount > 0 &&
              vm.customer_info.posa_discount <= 100
            ) {
              if (
                item.posa_is_offer == 0 &&
                !item.posa_is_replace &&
                item.posa_offer_applied == 0
              ) {
                if (item.max_discount > 0) {
                  item.discount_percentage =
                    item.max_discount < vm.customer_info.posa_discount
                      ? item.max_discount
                      : vm.customer_info.posa_discount;
                } else {
                  item.discount_percentage = vm.customer_info.posa_discount;
                }
              }
            }
            if (!item.batch_price) {
              if (
                !item.is_free_item &&
                !item.posa_is_offer &&
                !item.posa_is_replace
              ) {
                item.price_list_rate = data.price_list_rate;
              }
            }
            item.last_purchase_rate = data.last_purchase_rate;
            item.projected_qty = data.projected_qty;
            item.reserved_qty = data.reserved_qty;
            item.conversion_factor = data.conversion_factor;
            item.stock_qty = data.stock_qty;
            item.actual_qty = data.actual_qty;
            item.stock_uom = data.stock_uom;
            item.has_serial_no = data.has_serial_no;
            item.has_batch_no = data.has_batch_no;
              
          }
        },
      });
    },

    fetch_customer_details() {
      const vm = this;
      if (this.customer) {
        frappe.call({
          method: "posawesome.posawesome.api.customer.get_customer_info",
          args: {
            customer: vm.customer,
          },
          async: false,
          callback: (r) => {
            const message = r.message;
            if (!r.exc) {
              vm.customer_info = {
                ...message,
              };
            }
            vm.update_price_list();
          },
        });
      }
    },

    get_price_list() {
      let price_list = this.pos_profile.selling_price_list;
      if (this.customer_info && this.pos_profile) {
        const { customer_price_list, customer_group_price_list } =
          this.customer_info;
        const pos_price_list = this.pos_profile.selling_price_list;
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
      let value = parseFloat(event.target.value);
      
      if (Number(value) <= 0) {
        value = 0;
      }
      
      let maxDiscount = 100; // Default value
      
      if (item.max_discount && item.max_discount > 0) {
        maxDiscount = item.max_discount;
      }
      else if (this.pos_profile.posa_item_max_discount_allowed && this.pos_profile.posa_item_max_discount_allowed > 0) {
        maxDiscount = this.pos_profile.posa_item_max_discount_allowed;
      }
      
      if (value < 0) {
        value = 0;
      } else if (value > maxDiscount) {
        value = maxDiscount;
        evntBus.emit("show_mesage", {
          text: `Maximum discount applied: ${maxDiscount}%`,
          color: "info",
        });
      }
      
      item.discount_percentage = value;
      
      // Recalculate item with new discount for immediate visual feedback
      this.refreshTotals();

      if (this.invoice_doc && this.invoice_doc.name) {
        this.debounced_auto_update();
      }
      
      this.$forceUpdate();
    },

    update_price_list() {
      let price_list = this.get_price_list();
      if (price_list == this.pos_profile.selling_price_list) {
        price_list = null;
      }
      evntBus.emit("update_customer_price_list", price_list);
    },

    update_discount_umount() {
      const value = flt(this.additional_discount_percentage) || 0;
      const maxDiscount = this.pos_profile.posa_invoice_max_discount_allowed || 100;
      
      if (value < 0) {
        this.additional_discount_percentage = 0;
      } else if (value > maxDiscount) {
        this.additional_discount_percentage = maxDiscount;
        evntBus.emit("show_mesage", {
          text: `Maximum invoice discount is ${maxDiscount}%`,
          color: "info",
        });
      }
      
      if (this.invoice_doc && this.invoice_doc.name) {
        this.debounced_auto_update();
      }
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
        this.$forceUpdate();
      }
    },

    set_batch_qty(item, value, update = true) {
      if (!item.batch_no_data || !Array.isArray(item.batch_no_data)) {
        return;
      }

      const vm = this;
      frappe.call({
        method: "posawesome.posawesome.api.invoice.process_batch_selection",
        args: {
          item_code: item.item_code,
          current_item_row_id: item.posa_row_id,
          existing_items_data: this.items,
          batch_no_data: item.batch_no_data,
          preferred_batch_no: value || null
        },
        async: false,
        callback: function(r) {
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
            
            vm.$forceUpdate();
            
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
            
            vm.$forceUpdate();
          }
        },
        error: function(err) {
          evntBus.emit("show_mesage", {
            text: "خطأ في اختيار الباتش: " + (err.message || "خطأ غير معروف"),
            color: "error",
          });
        }
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
      let result = "";
      const characters = "abcdefghijklmnopqrstuvwxyz0123456789";
      const charactersLength = characters.length;
      for (var i = 0; i < length; i++) {
        result += characters.charAt(
          Math.floor(Math.random() * charactersLength)
        );
      }
      return result;
    },

    checkOfferIsAppley(item, offer) {
      let applied = false;
      const item_offers = JSON.parse(item.posa_offers);
      for (const row_id of item_offers) {
        const exist_offer = this.posa_offers.find((el) => row_id == el.row_id);
        if (exist_offer && exist_offer.offer_name == offer.name) {
          applied = true;
          break;
        }
      }
      return applied;
    },

    handelOffers() {
      if (this._offersDebounceTimer) {
        clearTimeout(this._offersDebounceTimer);
      }
      
      this._offersDebounceTimer = setTimeout(() => {
        this._processOffers();
      }, 300);
    },

    _processOffers() {
      if (!this.invoice_doc?.name) return;
      
      frappe.call({
        method: "posawesome.posawesome.api.invoice.get_applicable_offers",
        args: {
          invoice_name: this.invoice_doc.name
        },
        callback: (r) => {
          if (r.message) {
            this.updatePosOffers(r.message);
          }
        },
        error: (r) => {
        }
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
        this.posa_coupons.forEach(coupon => {
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
      let apply_offer = null;

      frappe.call({
        method: "posawesome.posawesome.api.invoice.process_item_offer",
        args: {
          offer_data: offer,
          items_data: this.items
        },
        async: false,
        callback: function(r) {
          if (r.message && r.message.success) {
            apply_offer = r.message.offer;
          }
        }
      });

      return apply_offer;
    },

    updatePosOffers(offers) {
      evntBus.emit("update_pos_offers", offers);
    },

    updateInvoiceOffers(offers) {
      this.posa_offers = offers || [];
      
      if (offers && offers.length > 0) {
        const offer_names = offers.map(offer => offer.name || offer.title);
        this.applyOffersToInvoice(offer_names);
      }
    },

    removeApplyOffer(invoiceOffer) {
      if (invoiceOffer.name || invoiceOffer.title) {
        const offer_name = invoiceOffer.name || invoiceOffer.title;
        this.removeOffersFromInvoice([offer_name]);
      }
      
      const index = this.posa_offers.findIndex(
        (el) => el.row_id === invoiceOffer.row_id
      );
      if (index > -1) {
        this.posa_offers.splice(index, 1);
      }
    },

    applyNewOffer(offer) {
      // SIMPLIFIED: Use Python API to apply new offers
      if (offer.name || offer.title) {
        const offer_name = offer.name || offer.title;
        this.applyOffersToInvoice([offer_name]);
      }
      
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

    applyOffersToInvoice(offer_names) {
      if (!this.invoice_doc?.name || !offer_names?.length) return;
      
      frappe.call({
        method: "posawesome.posawesome.api.invoice.apply_offers_to_invoice",
        args: {
          invoice_name: this.invoice_doc.name,
          offer_names: offer_names
        },
        callback: (r) => {
          if (r.message) {
            this.invoice_doc = r.message;
            this.refreshTotals();
            evntBus.emit("show_mesage", {
              text: "Offers applied successfully",
              color: "success",
            });
          }
        }
      });
    },

    removeOffersFromInvoice(offer_names) {
      if (!this.invoice_doc?.name || !offer_names?.length) return;
      
      frappe.call({
        method: "posawesome.posawesome.api.invoice.remove_offers_from_invoice",
        args: {
          invoice_name: this.invoice_doc.name,
          offer_names: offer_names
        },
        callback: (r) => {
          if (r.message) {
            this.invoice_doc = r.message;
            this.refreshTotals();
            evntBus.emit("show_mesage", {
              text: "Offers removed successfully",
              color: "info",
            });
          }
        }
      });
    },

    validate_due_date(item) {
      const today = frappe.datetime.now_date();
      const parse_today = Date.parse(today);
      const new_date = Date.parse(item.posa_delivery_date);
      if (new_date < parse_today) {
        setTimeout(() => {
          item.posa_delivery_date = today;
        }, 0);
      }
    },
    load_print_page(invoice_name) {
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        "/printview?doctype=Sales%20Invoice&name=" +
        invoice_name +
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
        },
        true
      );
    },

    set_delivery_charges() {
      const vm = this;
      if (
        !this.pos_profile ||
        !this.customer ||
        !this.pos_profile.posa_use_delivery_charges
      ) {
        this.delivery_charges = [];
        this.delivery_charges_rate = 0;
        this.selcted_delivery_charges = {};
        return;
      }
      this.delivery_charges_rate = 0;
      this.selcted_delivery_charges = {};
      frappe.call({
        method:
          "posawesome.posawesome.api.posapp.get_applicable_delivery_charges",
        args: {
          company: this.pos_profile.company,
          pos_profile: this.pos_profile.name,
          customer: this.customer,
        },
        async: true,
        callback: function (r) {
          if (r.message) {
            vm.delivery_charges = r.message;
          }
        },
      });
    },
    deliveryChargesFilter(item, queryText, itemText) {
      const textOne = item.name.toLowerCase();
      const searchText = queryText.toLowerCase();
      return textOne.indexOf(searchText) > -1;
    },
    update_delivery_charges() {
      if (this.selcted_delivery_charges) {
        this.delivery_charges_rate = this.selcted_delivery_charges.rate;
      } else {
        this.delivery_charges_rate = 0;
      }
    },
    debugTableDimensions() {
      try {
        if (!this.$el || typeof this.$el.querySelector !== "function") {
          return;
        }
        const table = this.$el.querySelector('.invoice-items-scrollable .v-data-table__wrapper table');
        if (!table) return;
        const rows = table.querySelectorAll('tr');
        rows.forEach((row, rIdx) => {
          [...row.children].forEach((cell, cIdx) => {
            const cs = window.getComputedStyle(cell);
          });
        });
      } catch (e) {
      }
    },
    printInvoice() {
      if (!this.invoice_doc || !this.items || !this.items.length) {
        evntBus.emit("show_mesage", {
          text: "No invoice to print",
          color: "error",
        });
        return;
      }

      const paymentsComponent = this.getPaymentsComponent();
      if (!paymentsComponent) {
        evntBus.emit("show_mesage", {
          text: "Cannot access payment screen for printing",
          color: "error",
        });
        return;
      }

      if (this.hasManualPayments(paymentsComponent)) {
        paymentsComponent.exposeSubmit(true);
        return;
      }

      const defaultMode = this.defaultPaymentMode;
      if (!defaultMode) {
        evntBus.emit("show_mesage", {
          text: "Please select a payment method",
          color: "warning",
        });
        return;
      }

      evntBus.emit("show_loading", {
        text: "Processing invoice for printing...",
        color: "info",
      });

      this.process_invoice()
        .then((invoice_doc) => {
          const defaultPayment = (invoice_doc.payments || []).find(
            (payment) => payment.mode_of_payment === defaultMode
          );
          if (defaultPayment) {
            defaultPayment.amount = this.flt(invoice_doc.grand_total, this.currency_precision);
          }
          evntBus.emit("send_invoice_doc_payment", invoice_doc);
          paymentsComponent.autoPayWithDefault(invoice_doc);
        })
        .catch((error) => {
          evntBus.emit("show_mesage", {
            text: "Failed to prepare invoice for printing: " + error.message,
            color: "error",
          });
        })
        .finally(() => {
          evntBus.emit("hide_loading");
        });
    },
    getPaymentsComponent() {
      let parent = this.$parent;
      while (parent) {
        if (parent.$refs && parent.$refs.payments) {
          return parent.$refs.payments;
        }
        parent = parent.$parent;
      }
      return null;
    },
    hasManualPayments(paymentsComponent) {
      const invoiceDoc = paymentsComponent && paymentsComponent.invoice_doc;
      if (!invoiceDoc || !invoiceDoc.payments) {
        return false;
      }
      return invoiceDoc.payments.some((payment) => this.flt(payment.amount) > 0);
    },
  },

  mounted() {
      this._cachedCalculations = new Map();
      this._lastCalculationTime = Date.now();
    
    evntBus.on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile;
      this.customer = data.pos_profile.customer;
      this.pos_opening_shift = data.pos_opening_shift;
      this.stock_settings = data.stock_settings;
      this.float_precision =
        frappe.defaults.get_default("float_precision") || 2;
      this.currency_precision =
        frappe.defaults.get_default("currency_precision") || 2;
      this.invoiceType = "Invoice";

    });
    evntBus.on("add_item", (item) => {
      this.add_item(item);
    });
    evntBus.on("update_customer", (customer) => {
      this.customer = customer;
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

      if (this.invoice_doc.is_return) {
        this.discount_amount = -data.discount_amount;
        this.additional_discount_percentage =
          -data.additional_discount_percentage;
        this.return_doc = data;
      } else {
        evntBus.emit("set_pos_coupons", data.posa_coupons);
      }
      
    });

    evntBus.on("set_offers", (data) => {
      this.posOffers = data;
    });
    evntBus.on("update_invoice_offers", (data) => {
      this.updateInvoiceOffers(data);
    });
    evntBus.on("update_invoice_coupons", (data) => {
      this.posa_coupons = data;
      this.handelOffers();
    });
    evntBus.on("set_all_items", (data) => {
      this.allItems = data;
      this.items.forEach((item) => {
        this.update_item_detail(item);
      });
    });
    evntBus.on("load_return_invoice", (data) => {
      this.new_invoice(data.invoice_doc);
      this.discount_amount = -data.return_doc.discount_amount;
      this.additional_discount_percentage =
        -data.return_doc.additional_discount_percentage;
      this.return_doc = data.return_doc;
    });
    evntBus.on("set_new_line", (data) => {
      this.new_line = data;
    });
    this.$nextTick(() => {
      this.debugTableDimensions();
    });
    evntBus.on("send_invoice_doc_payment", (doc) => {
      this.invoice_doc = doc;
    });
    evntBus.on("request_invoice_print", async () => {
      try {
        if (!this.canPrintInvoice()) {
          evntBus.emit("show_mesage", {
            text: "Please select a payment method before printing",
            color: "warning",
          });
          return;
        }
        const invoice_doc = await this.process_invoice();
        evntBus.emit("send_invoice_doc_payment", invoice_doc);
        this.printInvoice();
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "Failed to prepare invoice for printing: " + error.message,
          color: "error",
        });
      }
    });
  },
  beforeDestroy() {
    evntBus.$off("register_pos_profile");
    evntBus.$off("add_item");
    evntBus.$off("update_customer");
    evntBus.$off("fetch_customer_details");
    evntBus.$off("new_invoice");
    evntBus.$off("set_offers");
    evntBus.$off("update_invoice_offers");
    evntBus.$off("update_invoice_coupons");
    evntBus.$off("set_all_items");
    
    this._cachedCalculations.clear();
    this._couponCache = null;
    
    if (this._calculationDebounceTimer) {
      clearTimeout(this._calculationDebounceTimer);
    }
    if (this._offersDebounceTimer) {
      clearTimeout(this._offersDebounceTimer);
    }
    if (this._autoUpdateTimer) {
      clearTimeout(this._autoUpdateTimer);
    }
  },
  created() {
    document.addEventListener("keydown", this.shortOpenPayment.bind(this));
    document.addEventListener("keydown", this.shortDeleteFirstItem.bind(this));
    document.addEventListener("keydown", this.shortOpenFirstItem.bind(this));
    document.addEventListener("keydown", this.shortSelectDiscount.bind(this));
  },
  destroyed() {
    document.removeEventListener("keydown", this.shortOpenPayment);
    document.removeEventListener("keydown", this.shortDeleteFirstItem);
    document.removeEventListener("keydown", this.shortOpenFirstItem);
    document.removeEventListener("keydown", this.shortSelectDiscount);
  },
  // ===== SECTION 6: WATCH =====
  watch: {
    customer() {
      this.close_payments();
      evntBus.emit("set_customer", this.customer);
      this.fetch_customer_details();
      this.set_delivery_charges();
    },
    customer_info() {
      evntBus.emit("set_customer_info_to_edit", this.customer_info);
    },
    discount_percentage_offer_name() {
      evntBus.emit("update_discount_percentage_offer_name", {
        value: this.discount_percentage_offer_name,
      });
    },
    items: {
      deep: true,
      handler(items) {
        this.handelOffers();
        this.$forceUpdate();
      },
    },
    invoiceType() {
      evntBus.emit("update_invoice_type", this.invoiceType);
    },
    invoice_doc: {
      deep: true,
      handler(newDoc) {
        evntBus.emit("update_invoice_doc", newDoc);
        if (newDoc && newDoc.name) {
          this.$forceUpdate();
        }
      },
    },
    discount_amount() {
      if (this.invoice_doc && this.invoice_doc.name) {
        this.debounced_auto_update();
      }
    }
  },
  updated() {
    this.$nextTick(() => {
      this.debugTableDimensions();
    });
  }
};
</script>

<style scoped>
.border_line_bottom {
  border-bottom: 1px solid lightgray;
}
.disable-events {
  pointer-events: none;
}
/* Customer container styling */
.customer-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
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
/* Document type buttons styling */
.document-type-btn {
  min-width: 100px !important;
  height: 36px !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  border-radius: 8px !important;
  text-transform: none !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}
.document-type-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
}
/* Compact tweaks for small screens */
.invoice-number-text {
  line-height: 1.2;
}

/* Global compact styling to match 75% zoom appearance */
.v-application {
  font-size: 0.75rem !important; /* More aggressive reduction */
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
  height: 32px !important;
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
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  max-width: 100% !important;
  min-height: 0 !important;
  height: auto !important;
  box-sizing: border-box !important;
  overflow: visible !important;
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
  overflow: hidden;
}

/* Zero spacing table cells */
.invoice-items-scrollable .v-data-table__wrapper table th,
.invoice-items-scrollable .v-data-table__wrapper table td {
  white-space: normal !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  box-sizing: border-box !important;
  padding: 1px 2px !important;
  font-size: 0.7rem !important;
  margin: 0 !important;
  border-spacing: 0 !important;
  height: auto !important;
  min-height: 0 !important;
  max-height: none !important;
  line-height: 1.1 !important;
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
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
}

/* Hide all scrollbars */
.invoice-items-scrollable .v-data-table__wrapper::-webkit-scrollbar,
.invoice-items-scrollable::-webkit-scrollbar,
.v-data-table__wrapper::-webkit-scrollbar {
  width: 0 !important;
  height: 0 !important;
  display: none !important;
}

/* Hide scrollbar for IE, Edge and Firefox */
.invoice-items-scrollable .v-data-table__wrapper,
.invoice-items-scrollable,
.v-data-table__wrapper {
  -ms-overflow-style: none !important; /* IE and Edge */
  scrollbar-width: none !important; /* Firefox */
}

/* Force table to use exact column widths */
.invoice-items-scrollable .v-data-table__wrapper table th[style*="width"],
.invoice-items-scrollable .v-data-table__wrapper table td[style*="width"] {
  width: inherit !important;
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

.invoice-items-scrollable .v-data-table__wrapper table tr {
  margin: 0 !important;
  padding: 0 !important;
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
  max-height: none !important;
  overflow-x: hidden !important;
}

/* Remove any borders from table */
.invoice-items-scrollable .v-data-table,
.invoice-items-scrollable .v-data-table__wrapper,
.invoice-items-scrollable .v-data-table__wrapper table {
  border: none !important;
  outline: none !important;
}

.invoice-items-scrollable .v-data-table .v-data-table__wrapper {
  width: 100% !important;
  max-width: 100% !important;
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

/* Ultra-compact input fields */
.quantity-input,
.rate-input,
.discount-input {
  font-size: 0.7rem !important;
  min-height: 20px !important;
  max-height: 20px !important;
  font-weight: 500 !important;
  padding: 0px 2px !important;
  margin: 0 !important;
  box-sizing: border-box !important;
  width: 100% !important;
}

.quantity-input {
  width: 100% !important;
}

/* Additional border removal for quantity input */
.quantity-input .v-field__outline__start,
.quantity-input .v-field__outline__end,
.quantity-input .v-field__outline__notch {
  display: none !important;
}

.quantity-input .v-field__outline__notch::before,
.quantity-input .v-field__outline__notch::after {
  display: none !important;
}

/* Remove focus states */
.quantity-input .v-field--focused .v-field__outline {
  display: none !important;
}

.quantity-input .v-field--focused .v-field__outline__start,
.quantity-input .v-field--focused .v-field__outline__end,
.quantity-input .v-field--focused .v-field__outline__notch {
  display: none !important;
}

/* Remove hover states */
.quantity-input .v-field:hover .v-field__outline {
  display: none !important;
}

/* Quantity control buttons - Elegant */
/* Ultra-compact quantity controls */
.quantity-controls {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  height: 22px !important;
  width: 100% !important;
  gap: 2px !important;
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

.delete-item-btn .v-icon {
  font-size: 12px !important;
}

/* Ultra-compact quantity buttons */
.quantity-btn {
  min-width: 16px !important;
  width: 16px !important;
  height: 16px !important;
  padding: 0 !important;
  font-size: 0.6rem !important;
  font-weight: bold !important;
  border-radius: 2px !important;
  box-shadow: none !important;
  margin: 0 !important;
  box-sizing: border-box !important;
}

/* Increase button - green with plus shape */
.quantity-plus-btn {
  background-color: #4caf50 !important;
  color: white !important;
  border: 2px solid #2e7d32 !important;
}

.quantity-plus-btn:hover {
  background-color: #45a049 !important;
  transform: scale(1.05) !important;
}

.quantity-plus-btn:active {
  transform: scale(0.95) !important;
}

/* Decrease button - yellow with minus shape */
.quantity-minus-btn {
  background-color: #ff9800 !important;
  color: white !important;
  border: 2px solid #f57c00 !important;
}

.quantity-minus-btn:hover {
  background-color: #f57c00 !important;
  transform: scale(1.05) !important;
}

.quantity-minus-btn:active {
  transform: scale(0.95) !important;
}

.quantity-minus-btn:disabled {
  background-color: #ccc !important;
  color: #666 !important;
  border-color: #999 !important;
  transform: none !important;
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
  
  .invoice-items-scrollable .v-data-table__wrapper table th,
  .invoice-items-scrollable .v-data-table__wrapper table td {
    padding: 2px !important;
    font-size: 0.7rem !important;
  }
}

@media (max-width: 1024px) {
  /* No height restrictions */
}

/* Fixed payment control section at bottom - only the payment/discount controls */
.cards.mb-0.mt-3.py-1.px-0.grey.lighten-5 {
  position: fixed !important;
  bottom: 0 !important;
  right: 0 !important;
  left: 0 !important;
  width: 100% !important;
  z-index: 1000 !important;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1) !important;
  border-radius: 0 !important;
  margin: 0 !important;
}

/* Equal width fields styling for elegant distribution */
.equal-width-field {
  flex: 1 1 0 !important;
  min-width: 0 !important;
  max-width: none !important;
}

.equal-width-field .v-text-field {
  width: 100% !important;
}

.equal-width-field .v-text-field .v-field {
  width: 100% !important;
}

/* Responsive adjustments for fixed payment section */
@media (max-width: 1024px) {
  .cards.mb-0.mt-3.py-1.px-0.grey.lighten-5 {
    width: 100% !important;
    right: 0 !important;
    left: 0 !important;
  }
}

@media (max-width: 768px) {
  .cards.mb-0.mt-3.py-1.px-0.grey.lighten-5 {
    width: 100% !important;
    right: 0 !important;
    left: 0 !important;
  }
}

/* Final overrides to prevent any overflow */
.v-application--is-rtl .v-data-table > .v-data-table__wrapper > table > thead > tr > th {
  padding: 0 4px !important;
}

.invoice-items-scrollable .v-data-table__wrapper table tr td,
.invoice-items-scrollable .v-data-table__wrapper table tr th {
  margin: 0 !important;
  border: none !important;
  box-sizing: border-box !important;
  height: auto !important;
  min-height: 0 !important;
  max-height: none !important;
}

/* Vuetify v-text-field FIXED solution */
.invoice-items-scrollable .v-data-table__wrapper table td {
  height: 22px !important;
  max-height: 22px !important;
  line-height: 22px !important;
  padding: 0 !important;
  vertical-align: middle !important;
}

.quantity-controls {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  height: 22px !important;
  width: 100% !important;
  gap: 2px !important;
}

/* Fix quantity alignment and width */
.quantity-input {
  min-width: 32px !important;
  max-width: 60px !important;
  width: auto !important;
  height: 22px !important;
  line-height: 22px !important;
  padding: 0 4px !important;
  margin: 0 !important;
  text-align: center !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  color: #000 !important;
  background: transparent !important;
  border: none !important;
}

.quantity-input:focus {
  outline: none !important;
  border-bottom: 1px solid #1976d2 !important;
}

/* Remove ALL borders and outlines */
.quantity-input::-webkit-outer-spin-button,
.quantity-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.quantity-input[type='number'] {
  -moz-appearance: textfield;
  appearance: textfield;
}

.quantity-input .v-input__control {
  min-height: 20px !important;
  height: 20px !important;
}

.quantity-input .v-field {
  min-height: 20px !important;
  height: 20px !important;
  padding: 0 !important;
}

.quantity-input .v-field__field {
  align-items: center !important;
  height: 20px !important;
  min-height: 20px !important;
}

.quantity-input .v-field__input {
  font-size: 0.7rem !important;
  min-height: 20px !important;
  height: 20px !important;
  padding: 0 2px !important;
  text-align: center !important;
  line-height: 20px !important;
  font-weight: 600 !important;
  color: black !important;
  background-color: white !important;
}

/* Remove ALL Vuetify styling */
.quantity-input .v-field__field {
  align-items: center !important;
  height: 20px !important;
  min-height: 20px !important;
}

.quantity-input .v-field__input {
  font-size: 0.8rem !important;
  min-height: 20px !important;
  height: 20px !important;
  padding: 0 4px !important;
  text-align: center !important;
  line-height: 20px !important;
  font-weight: bold !important;
  color: black !important;
  background-color: white !important;
}

/* Remove ALL borders and outlines */
.quantity-input .v-field__outline,
.quantity-input .v-field__outline__start,
.quantity-input .v-field__outline__end,
.quantity-input .v-field__outline__notch {
  border-color: transparent !important;
  opacity: 0 !important;
}

/* Remove background */
.quantity-input .v-field--variant-plain {
  --v-field-border-opacity: 0 !important;
  --v-field-bg-opacity: 0 !important;
}

.quantity-btn {
  height: 18px !important;
  width: 18px !important;
  min-width: 18px !important;
  padding: 0 !important;
  font-size: 0.7rem !important;
}

.action-button {
  flex: 1;
  text-align: center;
}

.action-buttons-row {
  display: flex !important;
  flex-wrap: nowrap !important;
  gap: 0 !important;
}

.action-button {
  flex: 1 1 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}

.action-button .v-btn {
  height: 32px !important;
  font-size: 0.85rem !important;
  margin: 0 2px !important;
}
</style>