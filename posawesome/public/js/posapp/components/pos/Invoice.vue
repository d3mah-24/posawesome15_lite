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
                {{ logPriceDisplay(item) }}{{ formatCurrency(item.price_list_rate) }}
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
            :disabled="!hasItems || !hasChosenPayment"
            @click="printInvoice"
            title="Print after choosing a payment method"
          >
            Print Invoice
          </v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="success"
            variant="flat"
            :disabled="!hasItems"
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
      invoice_posting_date: false,
      posting_date: frappe.datetime.nowdate(),
      quick_return_value: false,
      _autoSaveProcessing: false,
      _pendingAutoSaveDoc: null,
      _pendingAutoSaveReason: "auto",
      _autoSaveWorkerTimer: null,
      _autoUpdateTimer: null,
      
      // Offers optimization variables
      _offersDebounceTimer: null,
      _offersCache: null,
      _offersProcessing: false,
      
      // Item operations debounce
      _itemOperationTimer: null,
      _updatingFromAPI: false,
      _itemOperationsQueue: [],
      _processingOperations: false,
      items_headers: [
        { title: "Item Name", align: "start", sortable: true, key: "item_name" },
        { title: "Qty", key: "qty", align: "center" },
        { title: "Unit", key: "uom", align: "center" },
        { title: "Price", key: "price_list_rate", align: "center" },
        { title: "After Disc.", key: "rate", align: "center" },
        { title: "Disc. %", key: "discount_percentage", align: "center" },
        { title: "Disc. Amount", key: "discount_amount", align: "center" },
        { title: "Total", key: "amount", align: "center" },
        { title: "Delete", key: "actions", align: "center", sortable: false },
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
      
      // First try to find a payment marked as default
      let defaultRow = payments.find(payment => payment.default == 1);
      
      // If no default payment is found, use the first payment as default
      if (!defaultRow && payments.length > 0) {
        defaultRow = payments[0];
      }
      
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
    hasItems() {
      return this.items && this.items.length > 0;
    },
    hasChosenPayment() {
      const payments = (this.invoice_doc && Array.isArray(this.invoice_doc.payments)) ? this.invoice_doc.payments : [];
      return payments.some(p => this.flt(p.amount) > 0);
    },
  },

  // ===== SECTION 5: METHODS =====
  methods: {
    
    onQtyChange(item) {
      try {
        const newQty = Number(item.qty) || 0;
        item.qty = newQty;
        this.refreshTotals();
        // Use unified debounce for all item operations
        this.debouncedItemOperation("qty-change");
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
        
        // Emit event for Event-driven approach
        evntBus.emit("item_updated", item);
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
        
        // Emit event for Event-driven approach
        evntBus.emit("item_updated", item);
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
            method: "posawesome.posawesome.api.sales_invoice_item.calculate_item_discount_amount",
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
    
    logPriceDisplay(item) {
      return ""; // Return empty string so it doesn't show in UI
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
        } else {
          // Emit event for Event-driven approach
          evntBus.emit("item_removed", item);
        }
      }
    },

    add_one(item) {
      item.qty++;
      if (item.qty == 0) {
        this.remove_item(item);
      } else {
        this.$forceUpdate();

        // Emit event for Event-driven approach
        evntBus.emit("item_updated", item);
      }
    },
    subtract_one(item) {
      item.qty--;
      if (item.qty == 0) {
        this.remove_item(item);
      } else {
        this.$forceUpdate();

        // Emit event for Event-driven approach
        evntBus.emit("item_updated", item);
      }
    },

    async add_item(item) {
      if (!item || !item.item_code) {
        evntBus.emit("show_mesage", {
          text: "Item data is incorrect or missing",
          color: "error",
        });
        return;
      }
      
      const new_item = Object.assign({}, item);
      
      if (!new_item.uom) {
        new_item.uom = new_item.stock_uom || 'Nos';
      }
      
      const existing_item = this.items.find(existing => 
        existing.item_code === new_item.item_code && 
        existing.uom === new_item.uom
      );
      
      let reason = "item-added";

      if (existing_item) {
        existing_item.qty = flt(existing_item.qty) + flt(new_item.qty);
        reason = "item-updated";
      } else {
        console.log('Invoice.vue(add_item): Added', new_item.item_code);
        new_item.posa_row_id = this.generateRowId();
        new_item.posa_offers = "[]";
        new_item.posa_offer_applied = 0;
        new_item.posa_is_offer = 0;
        new_item.posa_is_replace = 0;
        new_item.is_free_item = 0;
        
        this.items.push(new_item);
      }

      this.refreshTotals();

      // Check if this is the first item and no invoice exists
      if (this.items.length === 1 && !this.invoice_doc?.name) {
        console.log('Invoice.vue(add_item): Creating new invoice');
        // Create draft invoice immediately for first item
        this.create_draft_invoice();
        return;
      } else {
        // Emit event for Event-driven approach
        evntBus.emit("item_added", existing_item || new_item);
      }
    },
    generateRowId() {
      return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    async create_draft_invoice() {
      try {
        const doc = this.get_invoice_doc("draft");
        const result = await this.update_invoice(doc);
        
        if (result) {
          console.log('Invoice.vue(create_draft_invoice): Created', result.name);
          this.invoice_doc = result;
          evntBus.emit("show_mesage", {
            text: "Draft invoice created",
            color: "success",
          });
        } else {
          // Handle case when API returns null (no items)
          this.invoice_doc = null;
          this.items = [];
        }
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "Error creating draft invoice",
          color: "error",
        });
      }
    },

    async auto_update_invoice(doc = null, reason = "auto") {
      if (this.invoice_doc?.submitted_for_payment) {
        return;
      }

      // Skip auto-update if no items and no invoice doc
      if (!doc && this.items.length === 0 && !this.invoice_doc?.name) {
        return;
      }

      const payload = doc || this.get_invoice_doc(reason);

      try {
        const result = await this.update_invoice(payload);
        
        // Handle case when API returns null (no items)
        if (!result) {
          this.invoice_doc = null;
          this.items = [];
          return null;
        }
        
        if (result && Array.isArray(result.items)) {
          // Set flag to prevent watcher loop
          this._updatingFromAPI = true;
          
          // Merge API items with local items instead of replacing
          this.mergeItemsFromAPI(result.items);
          
          // Reset flag after update
          this.$nextTick(() => {
            this._updatingFromAPI = false;
          });
        }
        
        // Always update invoice_doc with API response (totals, taxes, etc.)
        if (result) {
          if (result.name && !this.invoice_doc?.name) {
            console.log('Invoice.vue(auto_update_invoice): Created', result.name);
            evntBus.emit("show_mesage", {
              text: "Draft invoice created",
              color: "success",
            });
          }
          
          // Update invoice_doc with latest totals from server
          this.invoice_doc = {
            ...this.invoice_doc,
            ...result,
            // Preserve local items if they exist and are more recent
            items: this.items.length > (result.items?.length || 0) ? this.items : (result.items || [])
          };
        }
        
        // Reset flag after invoice_doc is updated
        this._updatingFromAPI = false;
        
        return result;
      } catch (error) {
        if (error?.message && error.message.includes("Document has been modified")) {
          try {
            await this.reload_invoice();
          } catch (reloadError) {
            console.error("Failed to reload invoice after modification conflict", reloadError);
          }
          return;
        }

        evntBus.emit("show_mesage", {
          text: "Auto-saving draft failed",
          color: "error",
        });

        // Reset flag on error
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

      this._pendingAutoSaveDoc = this.get_invoice_doc(reason);
      this._pendingAutoSaveReason = reason;

      if (!this._autoSaveProcessing) {
        return this._run_auto_save_worker();
      }
      
      return Promise.resolve();
    },

    _run_auto_save_worker() {
      if (this._autoSaveProcessing) {
        return Promise.resolve();
      }

      if (!this._pendingAutoSaveDoc) {
        return Promise.resolve();
      }

      const doc = this._pendingAutoSaveDoc;
      const reason = this._pendingAutoSaveReason || "auto";

      this._pendingAutoSaveDoc = null;
      this._pendingAutoSaveReason = "auto";
      this._autoSaveProcessing = true;

      return this.auto_update_invoice(doc, reason)
        .then(() => {
          // Auto save success - no logging needed
        })
        .catch((error) => {
          console.log('Invoice.vue(_run_auto_save_worker): Error', error);
        })
        .finally(() => {
          this._autoSaveProcessing = false;

          if (this._pendingAutoSaveDoc) {
            if (this._autoSaveWorkerTimer) {
              clearTimeout(this._autoSaveWorkerTimer);
            }
            this._autoSaveWorkerTimer = setTimeout(() => {
              this._autoSaveWorkerTimer = null;
              this._run_auto_save_worker();
            }, 0);
          }
        });
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

    debounced_auto_update(reason = "auto") {
      if (this._autoUpdateTimer) {
        clearTimeout(this._autoUpdateTimer);
      }

      this._autoUpdateTimer = setTimeout(() => {
        this.queue_auto_save(reason);
      }, 200);
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
      evntBus.emit("set_customer_readonly", false);
      
      evntBus.emit("show_payment", "false");
    },

    delete_draft_invoice() {
      const name = this.invoice_doc && this.invoice_doc.name;
      const reset = () => {
        this.reset_invoice_session();
      };

      if (!name) {
        reset();
        return;
      }

    frappe.call({
      method: "posawesome.posawesome.api.sales_invoice.delete_invoice",
      args: { invoice_name: name }
      }).then(reset).catch(reset);
    },

    reset_invoice_session() {
      this.invoiceType = "Invoice";
      this.invoiceTypes = ["Invoice"];
      this.posting_date = frappe.datetime.nowdate();
      this.items = [];
              this.posa_offers = [];
              evntBus.emit("set_pos_coupons", []);
              this.posa_coupons = [];
      this.discount_amount = 0;
      this.additional_discount_percentage = 0;
      this.return_doc = null;
      this.invoice_doc = "";
      this.customer = this.pos_profile?.customer || this.customer;
      this.refreshTotals?.();
      evntBus.emit("new_invoice", "false");
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

    get_invoice_doc(reason = "auto") {
      const isPaymentFlow = reason === "payment" || reason === "print";
      const doc = {};

      // Always create a new invoice if no invoice exists or if we have items but no invoice name
      if (this.invoice_doc && this.invoice_doc.name && !this.invoice_doc.submitted_for_payment) {
        doc.name = this.invoice_doc.name;
      } else if (this.items.length > 0) {
        // Create new invoice when we have items but no existing invoice
      }

      doc.doctype = "Sales Invoice";
      doc.is_pos = 1;
      doc.ignore_pricing_rule = 1;
      doc.company = this.pos_profile.company;
      doc.pos_profile = this.pos_profile.name;
      doc.currency = this.pos_profile.currency;
      doc.naming_series = this.pos_profile.naming_series;
      doc.customer = this.customer;
      doc.posting_date = this.posting_date;
      doc.posa_pos_opening_shift = this.pos_opening_shift ? this.pos_opening_shift.name : null;

      doc.items = this.get_invoice_items_minimal();

      doc.discount_amount = flt(this.discount_amount);
      doc.additional_discount_percentage = flt(this.additional_discount_percentage);

      if (isPaymentFlow) {
        doc.payments = this.get_payments();
      }

      if (this.invoice_doc) {
        doc.is_return = this.invoice_doc.is_return;
        doc.return_against = this.invoice_doc.return_against;
      }

      return doc;
    },

    get_invoice_items_minimal() {
      return this.items.map((item) => ({
        item_code: item.item_code,
        qty: item.qty || 1,
        rate: item.rate || item.price_list_rate || 0,
        uom: item.uom || item.stock_uom,
        conversion_factor: item.conversion_factor || 1,
        serial_no: item.serial_no,
        discount_percentage: item.discount_percentage || 0,
        discount_amount: item.discount_amount || 0,
        batch_no: item.batch_no,
      }));
    },

    get_payments() {
      // Prefer current invoice payments (e.g., chosen in Payments dialog)
      if (this.invoice_doc && Array.isArray(this.invoice_doc.payments) && this.invoice_doc.payments.length) {
        return this.invoice_doc.payments.map((p) => ({
          amount: this.flt(p.amount),
          mode_of_payment: p.mode_of_payment,
          default: p.default,
          account: p.account || "",
          idx: p.idx,
        }));
      }
      // Fallback to POS Profile payments with zero amounts
      const payments = [];
      if (this.pos_profile && Array.isArray(this.pos_profile.payments)) {
        let hasDefault = false;
        
        // First pass: add all payments and check if any is default
        this.pos_profile.payments.forEach((payment, index) => {
          if (payment.default) hasDefault = true;
          payments.push({
            amount: 0,
            mode_of_payment: payment.mode_of_payment,
            default: payment.default,
            account: "",
            idx: index + 1, // Add idx for payment method identification
          });
        });
        
        // If no default payment is set, make the first one default
        if (!hasDefault && payments.length > 0) {
          payments[0].default = 1;
        }
      }
      return payments;
    },

    update_invoice(doc) {
      const vm = this;
      return new Promise((resolve, reject) => {
          frappe.call({
            method: "posawesome.posawesome.api.sales_invoice.update_invoice",
            args: {
            data: doc,
          },
          async: true,
          callback: function (r) {
            if (r.message !== undefined) {
              // Handle null response (invoice deleted)
              if (r.message === null) {
                vm.invoice_doc = null;
                vm.items = [];
                resolve(null);
              } else {
                vm.invoice_doc = r.message;
                
                // Update posa_offers from backend response
                if (r.message.posa_offers) {
                  vm.posa_offers = r.message.posa_offers;
                  
                  // Send applied offers to PosOffers component
                  const appliedOffers = vm.posa_offers.filter(offer => offer.offer_applied);
                  if (appliedOffers.length > 0) {
                    evntBus.emit('update_pos_offers', appliedOffers);
                  }
                }
                
                resolve(vm.invoice_doc);
              }
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
      const doc = this.get_invoice_doc("payment");
      
      try {
        const result = await this.update_invoice(doc);
        console.log('Invoice.vue(process_invoice): Success', doc.name);
        return result;
      } catch (error) {
        console.log('Invoice.vue(process_invoice): Error', error);
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
        
        // Add default payment method if no payments exist
        if (!invoice_doc.payments || invoice_doc.payments.length === 0) {
          console.log("[Invoice] adding default payment method");
          try {
            const defaultPayment = await frappe.call({
              method: "posawesome.posawesome.api.pos_profile.get_default_payment_from_pos_profile",
              args: {
                pos_profile: this.pos_profile.name,
                company: this.pos_profile.company || frappe.defaults.get_user_default("Company")
              }
            });
            
            if (defaultPayment.message) {
              invoice_doc.payments = [{
                mode_of_payment: defaultPayment.message.mode_of_payment,
                amount: flt(invoice_doc.grand_total),
                account: defaultPayment.message.account,
                default: 1
              }];
              console.log("[Invoice] default payment added", defaultPayment.message.mode_of_payment);
              
              // Save default payment to server
              try {
                await frappe.call({
                  method: "posawesome.posawesome.api.sales_invoice.update_invoice",
                  args: {
                    invoice_data: invoice_doc
                  }
                });
                console.log("[Invoice] default payment saved to server");
              } catch (error) {
                console.log("[Invoice] failed to save default payment to server", error);
              }
            }
          } catch (error) {
            console.log("[Invoice] failed to get default payment", error);
          }
        }
        
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
          method: "posawesome.posawesome.api.sales_invoice_item.validate_invoice_items",
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
          method: "posawesome.posawesome.api.sales_invoice.get_draft_invoices",
          args: {
          pos_opening_shift: this.pos_opening_shift ? this.pos_opening_shift.name : null,
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
        pos_opening_shift: this.pos_opening_shift || null
      });
    },

    close_payments() {
      evntBus.emit("show_payment", "false");
    },

    update_items_details(items) {
      if (!items.length) return;
      
      // Use unified debounce for all item operations
      this.debouncedItemOperation("items-details-update");
    },

    update_item_detail(item) {
      if (!item.item_code || this.invoice_doc.is_return) {
        return;
      }
      
      // Use unified debounce for all item operations
      this.debouncedItemOperation("item-detail-update");
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

      // Use unified debounce for all item operations
      this.debouncedItemOperation("discount-change");
      
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
      
      // Use unified debounce for all item operations
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
        this.$forceUpdate();
      }
    },

    set_batch_qty(item, value, update = true) {
      if (!item.batch_no_data || !Array.isArray(item.batch_no_data)) {
        return;
      }

      const vm = this;
        frappe.call({
          method: "posawesome.posawesome.api.batch.process_batch_selection",
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
          const exist_offer = this.posa_offers.find((el) => row_id == el.row_id);
          if (exist_offer && exist_offer.offer_name == offer.name) {
            applied = true;
            break;
          }
        }
      } catch (error) {
        console.error("[Invoice] error parsing posa_offers:", error);
        return false;
      }
      
      return applied;
    },

    mergeItemsFromAPI(apiItems) {
      console.log("[Invoice] merging items from API");
      console.log("[Invoice] local items count", this.items.length);
      console.log("[Invoice] API items count", apiItems.length);
      
      // Handle null or undefined apiItems
      if (!apiItems || !Array.isArray(apiItems)) {
        console.log("[Invoice] API items is null - keeping local items");
        return;
      }
      
      console.log("[Invoice] API items count", apiItems.length);
      
      // Always update invoice_doc with API totals, regardless of items merge strategy
      // This ensures totals are always updated from server
      
      // If local items are more than API items, keep local items
      // This happens when user adds items quickly before API responds
      if (this.items.length > (apiItems?.length || 0)) {
        console.log("[Invoice] keeping local items (more than API)");
        return;
      }
      
      // If API has more items, use API items
      if ((apiItems?.length || 0) > this.items.length) {
        console.log("[Invoice] using API items (more than local)");
        this.items = apiItems;
        return;
      }
      
      // If counts are equal, merge by updating existing items
      console.log("[Invoice] merging equal counts");
      if (Array.isArray(apiItems)) {
        apiItems.forEach(apiItem => {
        const localIndex = this.items.findIndex(localItem => 
          localItem.item_code === apiItem.item_code && 
          localItem.posa_row_id === apiItem.posa_row_id
        );
        
        if (localIndex >= 0) {
          // Update existing item with API data
          console.log("[Invoice] updating existing item", apiItem.item_code);
          this.items[localIndex] = { ...this.items[localIndex], ...apiItem };
        } else {
          // Check if item exists with different criteria (same item_code and uom)
          const existingItemIndex = this.items.findIndex(localItem => 
            localItem.item_code === apiItem.item_code && 
            localItem.uom === apiItem.uom
          );
          
          if (existingItemIndex >= 0) {
            console.log("[Invoice] updating existing item by item_code and uom", apiItem.item_code);
            this.items[existingItemIndex] = { ...this.items[existingItemIndex], ...apiItem };
          } else {
            console.log("[Invoice] adding new item from API", apiItem.item_code);
            this.items.push(apiItem);
          }
        }
        });
      }
    },

    debouncedItemOperation(operation = "item-operation") {
      console.log("[Invoice] debounced operation", operation);
      // Add operation to queue
      if (!this._itemOperationsQueue.includes(operation)) {
        this._itemOperationsQueue.push(operation);
      }
      
      // Clear existing timer
      if (this._itemOperationTimer) {
        clearTimeout(this._itemOperationTimer);
      }
      
      // Set new debounced timer for all item operations
      this._itemOperationTimer = setTimeout(() => {
        this.processItemOperations();
      }, 200); // 200ms for fast response
    },

    processItemOperations() {
      if (this._processingOperations) {
        return;
      }
      
      this._processingOperations = true;
      
      console.log("[Invoice] processing operations");
      
      // Process offers after all item operations are complete
      this.handelOffers();
      
      // Use queue_auto_save for better batching with combined operations
      const combinedReason = this._itemOperationsQueue.join("-") || "item-operation";
      console.log("[Invoice] auto save", combinedReason);
      
      // Clear queue immediately
      this._itemOperationsQueue = [];
      
      // Call queue_auto_save and reset processing flag after completion
      this.queue_auto_save(combinedReason).finally(() => {
        this._processingOperations = false;
        console.log("[Invoice] processing operations completed");
      });
    },

    handelOffers() {
      // Clear existing timer
      if (this._offersDebounceTimer) {
        clearTimeout(this._offersDebounceTimer);
      }
      
      // Set new debounced timer with same delay
      this._offersDebounceTimer = setTimeout(() => {
        this._processOffers();
      }, 200); // 200ms for fast response
    },

    _processOffers() {
      if (!this.invoice_doc?.name) return;
      
      // Skip offers processing if no items or only one item
      if (!this.items || this.items.length <= 1) {
        return;
      }
      
      // Check cache first (cache for 30 seconds)
      const cacheKey = `${this.invoice_doc.name}_${this.items.length}`;
      const now = Date.now();
      
      if (this._offersCache && 
          this._offersCache.key === cacheKey && 
          now - this._offersCache.timestamp < 30000) {
        console.log("[Invoice] using cached offers");
        this.updatePosOffers(this._offersCache.data);
        return;
      }
      
      // Prevent multiple simultaneous calls
      if (this._offersProcessing) {
        console.log("[Invoice] offers processing already in progress");
        return;
      }
      
      this._offersProcessing = true;
      
      frappe.call({
        method: "posawesome.posawesome.api.pos_offer.get_applicable_offers",
        args: {
          invoice_name: this.invoice_doc.name
        },
        callback: (r) => {
          this._offersProcessing = false;
          
          if (r.message) {
            // Cache the results
            this._offersCache = {
              key: cacheKey,
              data: r.message,
              timestamp: now
            };
            
            this.updatePosOffers(r.message);
          }
        },
        error: (r) => {
          this._offersProcessing = false;
          console.error("[Invoice] error fetching offers:", r);
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
          method: "posawesome.posawesome.api.pos_offer.process_item_offer",
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
      // Offers are now applied automatically in sales_invoice.py
      // No need to call backend API here
      console.log('[Invoice] offers applied automatically by backend', offer_names);
    },

    removeOffersFromInvoice(offer_names) {
      // Offers removal is now handled automatically in sales_invoice.py
      // No need to call backend API here
      console.log('[Invoice] offers removal handled automatically by backend', offer_names);
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

      const defaultMode = this.defaultPaymentMode;
      if (!defaultMode) {
        evntBus.emit("show_mesage", {
          text: "No default payment method in POS profile",
          color: "error",
        });
        return;
      }

      evntBus.emit("show_loading", {
        text: "Processing invoice for printing...",
        color: "info",
      });

      console.log("[Invoice] starting invoice submission process");
      this.process_invoice()
        .then((invoice_doc) => {
          console.log("[Invoice] process_invoice completed", invoice_doc.name);
          const hasChosen = (invoice_doc.payments || []).some((p) => this.flt(p.amount) > 0);
          console.log("[Invoice] payment check - hasChosen", hasChosen, "payments", invoice_doc.payments?.length || 0);
          
          if (!hasChosen) {
            evntBus.emit("show_mesage", { text: "Choose a payment method amount first", color: "warning" });
            evntBus.emit("show_payment", "true");
            throw new Error('No payment chosen');
          }
          
          console.log("[Invoice] calling submit_invoice API");
          console.log("[Invoice] invoice doc being sent", invoice_doc.name);
          
          // Submit and print the invoice
      frappe.call({
            method: "posawesome.posawesome.api.sales_invoice.submit_invoice",
        args: {
              data: {
                total_change: 0,
                paid_change: 0,
                credit_change: 0,
                redeemed_customer_credit: 0,
                customer_credit_dict: [],
                is_cashback: false,
              },
              invoice: invoice_doc,
        },
        async: true,
            callback: (r) => {
              console.log("[Invoice] submit_invoice callback received");
              console.log("[Invoice] full response:", r);
              console.log("[Invoice] r.message:", r.message);
              evntBus.emit("unfreeze");
              
              if (r.message) {
                console.log("[Invoice] invoice submitted successfully");
                
                // Handle different response formats
                let invoice_data = null;
                if (r.message.success && r.message.invoice) {
                  // New format: { success: true, invoice: {...} }
                  invoice_data = r.message.invoice;
                  console.log("[Invoice] using invoice from success response", invoice_data.name);
                } else if (r.message.name) {
                  // Old format: direct invoice object
                  invoice_data = r.message;
                  console.log("[Invoice] using direct invoice object", invoice_data.name);
                } else {
                  console.log("[Invoice] unexpected response format");
                  console.log("[Invoice] r.message keys:", Object.keys(r.message));
                  evntBus.emit("show_mesage", {
                    text: "Unexpected response format from server",
                    color: "error",
                  });
                  return;
                }
                
                if (invoice_data && invoice_data.name) {
                  console.log("[Invoice] invoice submitted successfully", invoice_data.name);
                  
                  this.load_print_page(invoice_data.name);
                  evntBus.emit("set_last_invoice", invoice_data.name);
                  evntBus.emit("show_mesage", {
                    text: `Invoice ${invoice_data.name} submitted and printed successfully`,
                    color: "success",
                  });
                  frappe.utils.play_sound("submit");
                  
                  // Clear local data after successful submission to prevent auto-save errors
                  console.log("[Invoice] clearing local data after successful submission");
                  this.items = [];
                  this.invoice_doc = null;
                  
                  evntBus.emit("new_invoice", "false");
                  evntBus.emit("invoice_submitted");
                } else {
                  console.log("[Invoice] no invoice name in response");
                  evntBus.emit("show_mesage", {
                    text: "Invoice submitted but no name received",
                    color: "warning",
                  });
                }
              } else {
                console.log("[Invoice] no message in submit_invoice response");
                evntBus.emit("show_mesage", {
                  text: "Failed to submit invoice",
                  color: "error",
                });
              }
            },
            error: (err) => {
              console.error("[Invoice] submit_invoice error:", err);
              evntBus.emit("unfreeze");
              evntBus.emit("show_mesage", {
                text: err?.message || "Failed to submit invoice",
                color: "error",
      });
    },
          });
        })
        .catch((error) => {
          console.error("[Invoice] process_invoice catch error:", error);
          evntBus.emit("unfreeze");
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
      this.discount_amount = -data.return_doc.discount_amount;
      this.additional_discount_percentage =
        -data.return_doc.additional_discount_percentage;
      this.return_doc = data.return_doc;
    });
    evntBus.on("set_new_line", (data) => {
      this.new_line = data;
    });
    
    // Event-driven approach for items changes
    evntBus.on("item_added", (item) => {
      console.log("[Invoice] item_added event received", item.item_code);
      this.debouncedItemOperation("item-added");
    });
    
    evntBus.on("item_removed", (item) => {
      console.log("[Invoice] item_removed event received", item.item_code);
      this.debouncedItemOperation("item-removed");
    });
    
    evntBus.on("item_updated", (item) => {
      console.log("[Invoice] item_updated event received", item.item_code);
      this.debouncedItemOperation("item-updated");
    });
    
    this.$nextTick(() => {
      this.debugTableDimensions();
    });
    evntBus.on("send_invoice_doc_payment", (doc) => {
      this.invoice_doc = doc;
    });
    evntBus.on('payments_updated', (payments) => {
      if (this.invoice_doc) {
        this.invoice_doc.payments = payments || [];
        this.$forceUpdate();
      }
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
    if (this._itemOperationTimer) {
      clearTimeout(this._itemOperationTimer);
    }
    
    // Clear operations queue
    this._itemOperationsQueue = [];
    this._processingOperations = false;
    if (this._autoUpdateTimer) {
      clearTimeout(this._autoUpdateTimer);
    }
    if (this._autoSaveWorkerTimer) {
      clearTimeout(this._autoSaveWorkerTimer);
    }
    this._pendingAutoSaveDoc = null;
    this._pendingAutoSaveReason = "auto";
    this._autoSaveProcessing = false;
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
      // Reset contact fields to avoid ERPNext validation error when customer changes
      if (this.invoice_doc) {
        this.invoice_doc.contact_person = "";
        this.invoice_doc.contact_email = "";
        this.invoice_doc.contact_mobile = "";
      }
      this.fetch_customer_details();
    },
    customer_info() {
      evntBus.emit("set_customer_info_to_edit", this.customer_info);
    },
    discount_percentage_offer_name() {
      evntBus.emit("update_discount_percentage_offer_name", {
        value: this.discount_percentage_offer_name,
      });
    },
    // items watcher removed - using Event-driven approach instead
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
        this.debouncedItemOperation("discount-amount-change");
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