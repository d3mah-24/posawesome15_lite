<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div>
    {{ console.log({template: "main container", result: "main container rendered"}) }}
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
            label="تكلفة الشحن"
            v-model="selcted_delivery_charges"
            :items="delivery_charges"
            item-title="name"
            return-object
            background-color="white"
            no-data-text="لا توجد تكاليف شحن متاحة"
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
                    v-html="`السعر: ${item.rate}`"
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
            label="سعر تكلفة الشحن"
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
                label="تاريخ المستند"
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
                <!-- حقل إدخال السعر -->
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
                      calc_prices(item, $event.target.value, $event),
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
                      calc_prices(item, $event.target.value, $event),
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
                      calc_prices(item, $event.target.value, $event),
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
                title="حذف الصنف"
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
            label="إجمالي الكمية"
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
            :model-value="formatFloat(additional_discount_percentage)"
            @change="
              [
                setFormatedFloat(
                  additional_discount_percentage,
                  'additional_discount_percentage',
                  null,
                  false,
                  $event
                ),
                update_discount_umount($event),
              ]
            "
            :rules="[isNumber]"
            label="خصم نسبة من الفاتورة"
            suffix="%"
            ref="percentage_discount"
            variant="outlined"
            dense
            color="warning"
            hide-details
            class="ma-0"
            style="margin: 0 1px !important;"
            :readonly="
              !pos_profile.posa_allow_user_to_edit_additional_discount ||
              !!discount_percentage_offer_name
            "
          ></v-text-field>
        </v-col>
        <v-col class="pa-0 ma-0 equal-width-field">
          <v-text-field
            :model-value="formatCurrency(total_items_discount_amount)"
            :prefix="currencySymbol(pos_profile.currency)"
            label="خصم الأصناف"
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
            label="الإجمالي قبل الخصم"
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
            label="الصافي بدون ضريبة"
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
            label="الضريبة"
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
            label="إجمالي الفاتورة"
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
            طباعة الفاتورة
          </v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="success"
            variant="flat"
            @click="show_payment"
          >
            دفع
          </v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="secondary"
            dark
            :disabled="!pos_profile.posa_allow_return"
            @click="open_returns"
          >مرتجع</v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="purple"
            dark
            variant="flat"
            :disabled="!pos_profile.posa_allow_quick_return"
            @click="quick_return"
          >مرتجع سريع</v-btn>
        </v-col>
        <v-col class="action-button">
          <v-btn
            block
            color="error"
            dark
            @click="cancel_invoice"
          >إلغاء</v-btn>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
console.log({script: "imports start"});
import { evntBus } from "../../bus";
import format from "../../format";
import Customer from "./Customer.vue";
console.log({script: "imports end", result: "3 imports loaded successfully"});

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],
  components: { Customer },
  // ===== SECTION 3: DATA =====
  data() {
    console.log({script: "data start"});
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
        { title: "مسح", key: "actions", align: "center", sortable: false },
        { title: "المجموع", key: "amount", align: "center" },
        { title: "قيمة الخصم", key: "discount_amount", align: "center" },
        { title: "نسبة الخصم", key: "discount_percentage", align: "center" },
        { title: "بعد الخصم", key: "rate", align: "center" },
        { title: "السعر", key: "price_list_rate", align: "center" },
        { title: "الوحدة", key: "uom", align: "center" },
        { title: "الكمية", key: "qty", align: "center" },
        { title: "اسم الصنف", align: "end", sortable: true, key: "item_name" },
      ],
      _cachedCalculations: new Map(),
      _lastCalculationTime: 0,
      _calculationDebounceTimer: null,
    };
    console.log({script: "data end", result: "data object initialized successfully"});
  },

  // ===== SECTION 4: COMPUTED =====
  computed: {
    // Dynamic table headers
    dynamicHeaders() {
      let headers = [...this.items_headers];
      
      // إزالة عمود نسبة الخصم إذا كان غير مفعل
      if (!this.pos_profile?.posa_display_discount_percentage) {
        headers = headers.filter(header => header.key !== 'discount_percentage');
      }
      
      // إزالة عمود قيمة الخصم إذا كان غير مفعل
      if (!this.pos_profile?.posa_display_discount_amount) {
        headers = headers.filter(header => header.key !== 'discount_amount');
      }
      
      // إزالة عمود "بعد الخصم" إذا لم يكن مسموحاً بتعديل الخصم
      if (!this.pos_profile?.posa_allow_user_to_edit_item_discount) {
        headers = headers.filter(header => header.key !== 'rate');
      }
      
      return headers;
    },
    readonly() {
      // الفاتورة تكون readonly فقط في حالة المرتجعات
      // المسودات يجب أن تكون قابلة للتعديل
      const isReadonly = this.invoice_doc?.is_return || false;
      return isReadonly;
    },
    total_qty() {
      return this.items.reduce((sum, item) => sum + flt(item.qty), 0);
    },
    Total() {
      const cacheKey = `total_${this.items.length}_${this.items.map(item => `${item.posa_row_id}_${item.qty}_${item.price_list_rate}`).join('_')}`;
      
      if (this._cachedCalculations.has(cacheKey)) {
        return this._cachedCalculations.get(cacheKey);
      }
      
      
      const total = this.items.reduce((sum, item) => {
        const qty = flt(item.qty, this.float_precision);
        const rate = flt(item.price_list_rate, this.currency_precision); // استخدام price_list_rate بدلاً من rate
        const itemTotal = qty * rate;
        
        
        return sum + itemTotal;
      }, 0);
      
      
      this._cachedCalculations.set(cacheKey, total);
      
      // تنظيف الذاكرة المؤقتة كل 5 دقائق
      if (Date.now() - this._lastCalculationTime > 300000) {
        this._cachedCalculations.clear();
        this._lastCalculationTime = Date.now();
      }
      
      return total;
    },
    subtotal() {
      try {
        // Calculate subtotal after discounts and delivery charges
        this.close_payments();
        
        let sum = 0;
        
        this.items.forEach((item, index) => {
          
          // For returns, use absolute value for correct calculation
          const qty = this.isReturnInvoice ? Math.abs(flt(item.qty)) : flt(item.qty);
          const rate = flt(item.rate);
          const itemTotal = qty * rate;
          sum += itemTotal;
          
        });


        // Calculate additional discount based on percentage of current item totals
        // This ensures the discount scales properly with the number of items
        let additional_discount_amount = 0;
        
        if (this.additional_discount_percentage && sum > 0) {
          additional_discount_amount = (sum * this.flt(this.additional_discount_percentage)) / 100;
        } else if (this.discount_amount) {
          // Fallback to fixed discount amount if percentage is not used
          additional_discount_amount = this.flt(this.discount_amount);
        }
        
        sum -= additional_discount_amount;

        // Add delivery charges
        const delivery_charges = this.flt(this.delivery_charges_rate);
        sum += delivery_charges;

        const finalResult = this.flt(sum, this.currency_precision);
        
        return finalResult;
      } catch (error) {
        console.error('❌ خطأ في حساب subtotal:', error);
        console.error('❌ تفاصيل الخطأ:', {
          message: error.message,
          stack: error.stack
        });
        // إرجاع قيمة افتراضية في حالة الخطأ
        return 0;
      }
    },
    total_items_discount_amount() {
      return this.items.reduce((sum, item) => sum + flt(item.qty) * flt(item.discount_amount), 0);
    },
    TaxAmount() {
      const cacheKey = `tax_${this.Total}_${this.tax_rate}`;
      
      if (this._cachedCalculations.has(cacheKey)) {
        return this._cachedCalculations.get(cacheKey);
      }
      
      const taxAmount = (flt(this.Total) * flt(this.tax_rate)) / 100;
      this._cachedCalculations.set(cacheKey, taxAmount);
      
      return taxAmount;
    },
    DiscountAmount() {
      const cacheKey = `discount_${this.Total}_${this.discount_amount}_${this.discount_percentage}`;
      
      if (this._cachedCalculations.has(cacheKey)) {
        return this._cachedCalculations.get(cacheKey);
      }
      
      let discountAmount = flt(this.discount_amount);
      if (this.discount_percentage > 0) {
        discountAmount += (flt(this.Total) * flt(this.discount_percentage)) / 100;
      }
      
      this._cachedCalculations.set(cacheKey, discountAmount);
      return discountAmount;
    },
    GrandTotal() {
      const cacheKey = `grand_total_${this.Total}_${this.TaxAmount}_${this.DiscountAmount}_${this.delivery_charges_rate}`;
      if (this._cachedCalculations.has(cacheKey)) {
        return this._cachedCalculations.get(cacheKey);
      }
      const grandTotal = flt(this.Total) + flt(this.TaxAmount) - flt(this.DiscountAmount) + flt(this.delivery_charges_rate);
      this._cachedCalculations.set(cacheKey, grandTotal);
      return grandTotal;
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
    getInvoiceNumberClass() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return 'invoice-number-field no-invoice';
      }
      if (this.invoice_doc && this.invoice_doc.is_return) {
        return 'invoice-number-field return-invoice';
      }
      return 'invoice-number-field regular-invoice';
    },
    getInvoiceNumberStyle() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return {
          color: '#757575',
          fontWeight: 'normal',
          fontStyle: 'italic'
        };
      }
      if (this.invoice_doc && this.invoice_doc.is_return) {
        return {
          color: '#d32f2f',
          fontWeight: 'bold'
        };
      }
      return {
        color: '#1976d2',
        fontWeight: 'bold'
      };
    },
    getInvoiceIconColor() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return '#757575';
      }
      if (this.invoice_doc && this.invoice_doc.is_return) {
        return '#d32f2f';
      }
      return '#1976d2';
    },
    onQtyChange(item) {
      try {
        const newQty = Number(item.qty) || 0;
        item.qty = newQty;
        if (newQty > 0) {
          this.calc_stock_qty(item, newQty);
        }
        this.recalculateItem(item);
        this.refreshTotals();
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      } catch (error) {
        console.error('Error updating quantity:', error);
        evntBus.emit("show_mesage", {
          text: "خطأ في تحديث الكمية",
          color: "error",
        });
      }
    },
    onQtyInput(item) {
      item.qty = Number(item.qty) || 0;
      this.recalculateItem(item);
      this.refreshTotals();
    },
    recalculateItem(item) {
      this.calc_item_price(item);
    },
    refreshTotals() {
      this._cachedCalculations.clear();
      this.$forceUpdate();
    },
    
    // دوال الزيادة والنقصان للكمية
    increaseQuantity(item) {
      try {
        const currentQty = Number(item.qty) || 0;
        const newQty = currentQty + 1;
        
        // تحديث الكمية مباشرة
        item.qty = newQty;
        
        // حساب الكمية المتاحة
        this.calc_stock_qty(item, newQty);
        
        // تنظيف الذاكرة المؤقتة
        this._cachedCalculations.clear();
        
        // تحديث الواجهة
        this.$forceUpdate();
        
        // تحديث تلقائي للفاتورة
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      } catch (error) {
        console.error('Error increasing quantity:', error);
        evntBus.emit("show_mesage", {
          text: "خطأ في زيادة الكمية",
          color: "error",
        });
      }
    },
    
    decreaseQuantity(item) {
      try {
        const currentQty = Number(item.qty) || 0;
        const newQty = Math.max(0, currentQty - 1);
        
        // تحديث الكمية مباشرة
        item.qty = newQty;
        
        // إذا كانت الكمية صفر، احذف العنصر
        if (newQty === 0) {
          this.remove_item(item);
          return;
        }
        
        // حساب الكمية المتاحة
        this.calc_stock_qty(item, newQty);
        
        // تنظيف الذاكرة المؤقتة
        this._cachedCalculations.clear();
        
        // تحديث الواجهة
        this.$forceUpdate();
        
        // تحديث تلقائي للفاتورة
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      } catch (error) {
        console.error('Error decreasing quantity:', error);
        evntBus.emit("show_mesage", {
          text: "خطأ في تقليل الكمية",
          color: "error",
        });
      }
    },

    
    getDiscountAmount(item) {
      // حساب قيمة الخصم بناءً على نسبة الخصم والسعر
      if (!item) return 0;
      
      const basePrice = flt(item.price_list_rate) || flt(item.rate) || 0;
      const discountPercentage = flt(item.discount_percentage) || 0;
      
      if (discountPercentage > 0 && basePrice > 0) {
        return this.flt((basePrice * discountPercentage) / 100, this.currency_precision);
      }
      
      // إذا كانت هناك قيمة خصم محفوظة، استخدمها
      return flt(item.discount_amount) || 0;
    },
    

    
    quick_return() {
      // التحقق من تفعيل المرتجع السريع
      if (!this.pos_profile.posa_allow_quick_return) {
        evntBus.emit("show_mesage", {
          text: "المرتجع السريع غير مفعل في ملف نقاط البيع",
          color: "error",
        });
        return;
      }
      
      if (!this.customer) {
        evntBus.emit("show_mesage", {
          text: "لا يوجد عميل!",
          color: "error",
        });
        return;
      }
      if (!this.items.length) {
        evntBus.emit("show_mesage", {
          text: "لا توجد أصناف!",
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
        
        // التحقق من عدد الأصناف المتبقية
        if (this.items.length === 0 && this.invoice_doc && this.invoice_doc.name) {
          // حذف الفاتورة إذا لم يعد هناك أصناف
          this.delete_draft_invoice();
        } else if (this.invoice_doc && this.invoice_doc.name) {
          // تحديث تلقائي للفاتورة عند حذف صنف
          this.debounced_auto_update();
        }
      }
    },

    add_one(item) {
      item.qty++;
      if (item.qty == 0) {
        this.remove_item(item);
      } else {
        this.calc_stock_qty(item, item.qty);
        this.$forceUpdate();
        
        // تحديث تلقائي للفاتورة عند تغيير الكمية
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
        this.calc_stock_qty(item, item.qty);
        this.$forceUpdate();
        
        // تحديث تلقائي للفاتورة عند تغيير الكمية
        if (this.invoice_doc && this.invoice_doc.name) {
          this.debounced_auto_update();
        }
      }
    },

    add_item(item) {
      // التأكد من وجود البيانات المطلوبة
      if (!item || !item.item_code) {
        evntBus.emit("show_mesage", {
          text: "بيانات الصنف غير صحيحة أو مفقودة",
          color: "error",
        });
        return;
      }
      
      // استخدام Object.assign بدلاً من spread operator للأداء الأفضل
      const new_item = Object.assign({}, item);
      
      // التأكد من وجود السعر
      if (!new_item.rate && !new_item.price_list_rate) {
        evntBus.emit("show_mesage", {
          text: `لا يوجد سعر للصنف '${new_item.item_name || new_item.item_code}'`,
          color: "error",
        });
        return;
      }
      
      // البحث المحسن عن العنصر الموجود
      // تحسين البحث ليتعامل مع الباركود بشكل صحيح
      
      // التأكد من وجود UOM
      if (!new_item.uom) {
        new_item.uom = new_item.stock_uom || 'Nos';
      }
      
      const existing_item = this.items.find(existing => {
        // المطابقة الأساسية: نفس كود الصنف ووحدة القياس
        const basicMatch = existing.item_code === new_item.item_code && 
                          existing.uom === new_item.uom;
        
        
        // إذا كان الصنف له batch_no، يجب أن يكون متطابقاً
        if (existing.batch_no || new_item.batch_no) {
          const batchMatch = basicMatch && existing.batch_no === new_item.batch_no;
          return batchMatch;
        }
        
        // إذا لم يكن هناك batch_no، المطابقة الأساسية كافية
        return basicMatch;
      });
      
      if (existing_item) {
        existing_item.qty = flt(existing_item.qty) + flt(new_item.qty);
        this.calc_item_price(existing_item);
      } else {
        new_item.posa_row_id = this.generateRowId();
        new_item.posa_offers = "[]";
        new_item.posa_offer_applied = 0;
        new_item.posa_is_offer = 0;
        new_item.posa_is_replace = 0;
        new_item.is_free_item = 0;
        new_item.uom = new_item.uom || new_item.stock_uom;

        const original_price = new_item.price_list_rate || new_item.rate || 0;
        new_item.price_list_rate = original_price;
        new_item.base_rate = original_price;
        new_item.rate = original_price;

        this.items.push(new_item);
        this.calc_item_price(new_item);
      }
      
      // إنشاء فاتورة مسودة تلقائياً عند إضافة أول صنف
      if (this.items.length === 1 && !this.invoice_doc) {
        this.create_draft_invoice();
      } else if (this.invoice_doc && this.invoice_doc.name) {
        // تحديث تلقائي للفاتورة عند إضافة صنف جديد مع تأخير
        this.debounced_auto_update();
      }
      
      // تنظيف الذاكرة المؤقتة
      this._cachedCalculations.clear();
    },

    generateRowId() {
      return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    async create_draft_invoice() {
      try {
        console.log("إنشاء فاتورة مسودة جديدة...");
        const doc = this.get_invoice_doc();
        const result = await this.update_invoice(doc);
        
        if (result) {
          this.invoice_doc = result;
          console.log("تم إنشاء فاتورة مسودة بنجاح");
          evntBus.emit("show_mesage", {
            text: "تم إنشاء فاتورة مسودة",
            color: "success",
          });
        }
      } catch (error) {
        console.log("خطأ في إنشاء فاتورة مسودة:", error);
        evntBus.emit("show_mesage", {
          text: "خطأ في إنشاء فاتورة مسودة",
          color: "error",
        });
      }
    },

    async auto_update_invoice() {
      // تحديث تلقائي للفاتورة إذا كانت موجودة
      if (this.invoice_doc && this.invoice_doc.name && !this.invoice_doc.submitted_for_payment) {
        // منع التحديث المتكرر السريع
        if (this._autoUpdateInProgress) {
          return;
        }
        
        this._autoUpdateInProgress = true;
        
        try {
          console.log("تحديث فاتورة مسودة...");
          const doc = this.get_invoice_doc();
          const result = await this.update_invoice(doc);
          if (result) {
            this.invoice_doc = result;
            console.log("تم تحديث فاتورة مسودة بنجاح");
            evntBus.emit("show_mesage", {
              text: "تم تحديث فاتورة مسودة",
              color: "info",
            });
          }
        } catch (error) {
          // معالجة الخطأ بصمت لتجنب إزعاج المستخدم
          console.warn('Auto update failed:', error);
          
          // إذا كان الخطأ بسبب تعديل المستند، إعادة تحميل الفاتورة
          if (error.message && error.message.includes('Document has been modified')) {
            try {
              await this.reload_invoice();
            } catch (reloadError) {
              console.warn('Failed to reload invoice:', reloadError);
            }
          }
        } finally {
          // إزالة القفل بعد انتهاء التحديث
          setTimeout(() => {
            this._autoUpdateInProgress = false;
          }, 1000); // انتظار ثانية واحدة قبل السماح بتحديث آخر
        }
      }
    },

    async reload_invoice() {
      // إعادة تحميل الفاتورة من قاعدة البيانات
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
            // تحديث الأصناف من الفاتورة المحملة
            if (result.message.items) {
              this.items = result.message.items;
            }
          }
        } catch (error) {
          console.warn('Failed to reload invoice:', error);
        }
      }
    },

    debounced_auto_update() {
      // إلغاء التحديث السابق إذا كان موجوداً
      if (this._autoUpdateTimer) {
        clearTimeout(this._autoUpdateTimer);
      }
      
      // تأخير التحديث لمدة 500ms لتجنب التحديثات المتكررة
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
      
      // الحفاظ على قائمة الوحدات للصنف
      new_item.item_uoms = item.item_uoms || [];
      
      // إضافة الوحدة الأساسية إذا لم تكن في قائمة الوحدات
      if (new_item.item_uoms.length === 0 || !new_item.item_uoms.some(uom => uom.uom === item.stock_uom)) {
        new_item.item_uoms.unshift({ uom: item.stock_uom, conversion_factor: 1 });
      }
      
      // تصحيح البيانات: التأكد من وجود الحقول المطلوبة لكل وحدة
      new_item.item_uoms = new_item.item_uoms.map(uom => {
        // إذا كانت الوحدة نص، تحويلها إلى كائن
        if (typeof uom === 'string') {
          return { uom: uom, conversion_factor: 1 };
        } 
        // إذا كانت كائن، التأكد من وجود الحقول المطلوبة
        else if (typeof uom === 'object' && uom !== null) {
          return { 
            uom: uom.uom || uom.name || uom.toString(), 
            conversion_factor: parseFloat(uom.conversion_factor) || 1 
          };
        }
        // إذا كانت فارغة أو غير معرفة، استخدام الوحدة الأساسية
        else {
          return { uom: item.stock_uom || 'Nos', conversion_factor: 1 };
        }
      }).filter(uom => uom && uom.uom); // استبعاد الوحدات غير الصحيحة
      
      // تعيين عامل التحويل الصحيح بناءً على الوحدة المختارة
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
      const doc = this.get_invoice_doc();
      
      // حذف الفاتورة المسودة من قاعدة البيانات إذا كانت موجودة
      if (this.invoice_doc && this.invoice_doc.name) {
        console.log("إلغاء فاتورة مسودة...");
        frappe.call({
          method: "frappe.client.delete",
          args: {
            doctype: "Sales Invoice",
            name: this.invoice_doc.name
          },
          callback: (r) => {
            if (r.message) {
              console.log("تم إلغاء فاتورة مسودة بنجاح");
              evntBus.emit("show_mesage", {
                text: "تم إلغاء فاتورة مسودة",
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
      
      // إغلاق شاشة الدفع إذا كانت مفتوحة
      evntBus.emit("show_payment", "false");
    },

    delete_draft_invoice() {
      // حذف الفاتورة المسودة من قاعدة البيانات
      if (this.invoice_doc && this.invoice_doc.name) {
        console.log("حذف فاتورة مسودة...");
        frappe.call({
          method: "frappe.client.delete",
          args: {
            doctype: "Sales Invoice",
            name: this.invoice_doc.name
          },
          callback: (r) => {
            if (r.message) {
              console.log("تم حذف فاتورة مسودة بنجاح");
              evntBus.emit("show_mesage", {
                text: "تم حذف فاتورة مسودة",
                color: "success",
              });
              // إعادة تعيين البيانات
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
      
      // الإجمالي قبل الخصم يجب أن يكون مجموع price_list_rate
      doc.total = this.Total;
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
      // doc.branch = this.pos_profile.branch || ""; // Temporarily disabled - branch field not in database
      return doc;
    },

    get_invoice_items() {
      // استخدام Array.map بدلاً من forEach للأداء الأفضل
      return this.items.map(item => {
        // التأكد من أن السعر والكمية صحيحة
        const rate = flt(item.rate) || flt(item.price_list_rate) || 0;
        const qty = Number(item.qty) > 0 ? Number(item.qty) : 1;

        return {
          item_code: item.item_code,
          posa_row_id: item.posa_row_id,
          posa_offers: item.posa_offers,
          posa_offer_applied: item.posa_offer_applied,
          posa_is_offer: item.posa_is_offer,
          posa_is_replace: item.posa_is_replace,
          is_free_item: item.is_free_item,
          qty: qty,
          rate: rate,
          uom: item.uom || item.stock_uom,
          amount: qty * rate,
          conversion_factor: item.conversion_factor || 1,
          serial_no: item.serial_no,
          discount_percentage: flt(item.discount_percentage) || 0,
          discount_amount: flt(item.discount_amount) || 0,
          batch_no: item.batch_no,
          posa_notes: item.posa_notes,
          posa_delivery_date: item.posa_delivery_date,
          price_list_rate: item.price_list_rate || rate,
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
              reject(new Error('فشل في تحديث الفاتورة'));
            }
          },
          error: function (err) {
            // معالجة خطأ تعديل المستند
            if (err.message && err.message.includes('Document has been modified')) {
              evntBus.emit('show_mesage', {
                text: 'تم تعديل الفاتورة من مكان آخر، سيتم إعادة تحميلها',
                color: 'warning'
              });
              
              // إعادة تحميل الفاتورة
              vm.reload_invoice().then(() => {
                resolve(vm.invoice_doc);
              }).catch((reloadError) => {
                reject(reloadError);
              });
            } else {
              evntBus.emit('show_mesage', {
                text: 'خطأ في تحديث الفاتورة',
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
          text: 'خطأ في معالجة الفاتورة',
          color: 'error'
        });
        throw error;
      }
    },


    async show_payment() {
      if (this.readonly) return;
      if (!this.customer) {
        evntBus.emit("show_mesage", {
          text: "لا يوجد عميل!",
          color: "error",
        });
        return;
      }
      if (!this.items.length) {
        evntBus.emit("show_mesage", {
          text: "لا توجد أصناف في الفاتورة!",
          color: "error",
        });
        return;
      }

      // إظهار مؤشر التحميل
      evntBus.emit("show_loading", {
        text: "جاري تحضير شاشة الدفع...",
        color: "info"
      });

      try {
        // معالجة الفاتورة الحالية
        const invoice_doc = await this.process_invoice();
        
        
        // إرسال الفاتورة لشاشة الدفع
        evntBus.emit("send_invoice_doc_payment", invoice_doc);
        evntBus.emit("show_payment", "true");
        
        // لا نمسح السلة هنا - سنمسحها بعد اكتمال الدفع
        // السلة ستبقى حتى يتم تأكيد الدفع بنجاح
        // لا نمسح الخصومات والعروض هنا - يجب أن تبقى حتى اكتمال الدفع
        
        // فقط مسح العروض والكوبونات المؤقتة
        this.posa_offers = [];
        this.posa_coupons = [];
        this._cachedCalculations.clear();
        

        // 3. إعادة تعيين العميل فقط إذا كان مطلوباً في الإعدادات
        if (this.pos_profile.posa_clear_customer_after_payment) {
          this.customer = this.pos_profile.customer;
          evntBus.emit("set_customer", this.customer);
        }

        // 4. إعلام المكونات الأخرى بجلسة جديدة
        evntBus.emit("invoice_session_reset");
        
        // إخفاء مؤشر التحميل
        evntBus.emit("hide_loading");
        
      } catch (error) {
        evntBus.emit("hide_loading");
        evntBus.emit("show_mesage", {
          text: "حدث خطأ أثناء تحضير الفاتورة: " + error.message,
          color: "error",
        });
        console.error("Error in show_payment:", error);
      }
    },

    validate() {
      // استخدام Array.every بدلاً من forEach للتحقق السريع
      return this.items.every(item => {
              // التحقق من صحة الكمية - السماح بالكميات السالبة للفواتير المرتجعة
      if (item.qty == 0) {
          evntBus.emit("show_mesage", {
            text: `كمية الصنف '${item.item_name}' لا يمكن أن تكون صفر (0)`,
            color: "error",
          });
          return false;
        }
        
        // للفواتير العادية، لا تسمح بالكميات السالبة
        if (!this.invoice_doc.is_return && item.qty < 0) {
          evntBus.emit("show_mesage", {
            text: `كمية الصنف '${item.item_name}' لا يمكن أن تكون سالبة في الفواتير العادية`,
            color: "error",
          });
          return false;
        }
        
        // التحقق من الحد الأقصى للخصم
        if (this.pos_profile.posa_item_max_discount_allowed && !item.posa_offer_applied) {
          if (item.discount_amount && this.flt(item.discount_amount) > 0) {
            const discount_percentage = (this.flt(item.discount_amount) * 100) / this.flt(item.price_list_rate);
            if (discount_percentage > this.pos_profile.posa_item_max_discount_allowed) {
              evntBus.emit("show_mesage", {
                text: `نسبة الخصم للصنف '${item.item_name}' لا يمكن أن تتجاوز ${this.pos_profile.posa_item_max_discount_allowed}%`,
                color: "error",
              });
              return false;
            }
          }
        }
        
        // التحقق من توفر المخزون
        if (this.stock_settings.allow_negative_stock != 1) {
                      if (this.invoiceType == "Invoice" && item.is_stock_item && item.stock_qty && 
                (!item.actual_qty || item.stock_qty > item.actual_qty)) {
              evntBus.emit("show_mesage", {
                text: `الكمية المتاحة '${item.actual_qty}' للصنف '${item.item_name}' غير كافية`,
                color: "error",
              });
              return false;
            }
        }
        
        return true;
      });
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
            text: 'خطأ في جلب الفواتير المسودة',
            color: 'error'
          });
        }
      });
    },



    open_returns() {
      // التحقق من تفعيل المرتجع
      if (!this.pos_profile.posa_allow_return) {
        evntBus.emit("show_mesage", {
          text: "المرتجع غير مفعل في ملف نقاط البيع",
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
            // استخدام Map للبحث الأسرع
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
                
                // تصحيح بيانات الوحدات
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
            text: 'خطأ في تحديث تفاصيل الأصناف',
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
            (item.has_serial_no = data.has_serial_no),
              (item.has_batch_no = data.has_batch_no),
              vm.calc_item_price(item);
              
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
      
      // تحديد الحد الأقصى للخصم
      let maxDiscount = 100; // القيمة الافتراضية
      
      // إذا كان الصنف له حد أقصى محدد
      if (item.max_discount && item.max_discount > 0) {
        maxDiscount = item.max_discount;
      }
      // إذا كان POS Profile له حد أقصى محدد
      else if (this.pos_profile.posa_item_max_discount_allowed && this.pos_profile.posa_item_max_discount_allowed > 0) {
        maxDiscount = this.pos_profile.posa_item_max_discount_allowed;
      }
      
      
      if (value < 0) {
        value = 0;
      } else if (value > maxDiscount) {
        value = maxDiscount;
        evntBus.emit("show_mesage", {
          text: `تم تطبيق الحد الأقصى للخصم: ${maxDiscount}%`,
          color: "info",
        });
      }
      
      item.discount_percentage = value;
      
      const syntheticEvent = {
        target: {
          id: 'discount_percentage',
          value: value
        }
      };
      
      this.calc_prices(item, value, syntheticEvent);
      
      // إعادة حساب Total بعد تطبيق الخصم
      this._cachedCalculations.clear();
      
      // إجبار إعادة حساب Total
      
      this.$forceUpdate();
    },

    update_price_list() {
      let price_list = this.get_price_list();
      if (price_list == this.pos_profile.selling_price_list) {
        price_list = null;
      }
      evntBus.emit("update_customer_price_list", price_list);
    },
    update_discount_umount(event) {
      this.additional_discount_percentage = event.target.value;
      const value = flt(this.additional_discount_percentage);
      
      // تحديد الحد الأقصى للخصم
      const maxDiscount = this.pos_profile.posa_invoice_max_discount_allowed || 100;
      
      
      if (value >= 0 && value <= maxDiscount) {
        this.discount_amount = (this.Total * value) / 100;
      } else if (value > maxDiscount) {
        this.additional_discount_percentage = maxDiscount;
        this.discount_amount = (this.Total * maxDiscount) / 100;
        evntBus.emit("show_mesage", {
          text: `تم الرجوع لنسبة الخصم المسموح بها`,
          color: "info",
        });
      } else {
        this.additional_discount_percentage = 0;
        this.discount_amount = 0;
      }
      
      // تحديث تلقائي للفاتورة عند تطبيق خصم على الفاتورة
      if (this.invoice_doc && this.invoice_doc.name) {
        this.debounced_auto_update();
      }
    },

    calc_prices(item, value, $event) {
      const originalPrice = flt(item.base_rate) || flt(item.price_list_rate) || 0;

      if ($event.target.id === "rate") {
        item.discount_percentage = 0;
        if (value < originalPrice) {
          item.discount_amount = this.flt(
            originalPrice - flt(value),
            this.currency_precision
          );
        } else if (value < 0) {
          item.rate = originalPrice;
          item.discount_amount = 0;
        } else if (value > originalPrice) {
          item.discount_amount = 0;
        }
      } else if ($event.target.id === "discount_amount") {
        if (value < 0) {
          item.discount_amount = 0;
          item.discount_percentage = 0;
        } else {
          item.rate = originalPrice - flt(value);
          item.discount_percentage = 0;
        }
      } else if ($event.target.id === "discount_percentage") {
        if (value < 0) {
          item.discount_amount = 0;
          item.discount_percentage = 0;
          item.rate = originalPrice;
        } else {
          item.rate = this.flt(
            originalPrice - (originalPrice * flt(value)) / 100,
            this.currency_precision
          );
          
          item.discount_amount = this.flt(
            originalPrice - flt(+item.rate),
            this.currency_precision
          );
          
          if (item.rate < 0) {
            item.rate = 0;
            item.discount_amount = originalPrice;
          }
        }
      }
      
      // تحديث تلقائي للفاتورة عند تغيير السعر أو الخصم
      if (this.invoice_doc && this.invoice_doc.name) {
        this.debounced_auto_update();
      }
    },

    calc_item_price(item) {
      // التأكد من وجود البيانات المطلوبة
      if (!item) return;
      
      // استخدام الذاكرة المؤقتة للعمليات الحسابية المتكررة
      const cacheKey = `price_${item.qty}_${item.rate}_${item.discount_percentage}_${item.discount_amount}`;
      
      if (this._cachedCalculations.has(cacheKey)) {
        const cached = this._cachedCalculations.get(cacheKey);
        item.amount = cached.amount;
        item.rate = cached.rate;
        return;
      }
      
      // التأكد من وجود السعر الأساسي
      const original_rate = flt(item.base_rate) || flt(item.price_list_rate) || 0;
      if (original_rate <= 0) {
        evntBus.emit("show_mesage", {
          text: `السعر غير صحيح للصنف '${item.item_name || item.item_code}'`,
          color: "error",
        });
        return;
      }
      
      let final_rate = original_rate;
      
      if (item.discount_percentage > 0) {
        final_rate = original_rate - (original_rate * flt(item.discount_percentage) / 100);
      }
      
      if (item.discount_amount > 0) {
        final_rate = final_rate - flt(item.discount_amount);
      }
      
      // التأكد من أن السعر النهائي لا يكون سالب
      final_rate = Math.max(0, final_rate);
      
      item.rate = final_rate;
      item.amount = flt(item.qty || 0) * final_rate;
      
      // حفظ في الذاكرة المؤقتة
      this._cachedCalculations.set(cacheKey, {
        amount: item.amount,
        rate: item.rate
      });
    },

    calc_uom(item, value) {
      // Ensure the selected value is the unit name (string)
      let selected_uom = value;
      if (typeof value === "object" && value !== null) {
        if (value.target && value.target.value) {
          selected_uom = value.target.value;
        } else if (value.uom) {
          selected_uom = value.uom;
        }
      }
      
      item.uom = selected_uom;
      
      // البحث عن عامل التحويل للوحدة المختارة
      if (item.item_uoms && Array.isArray(item.item_uoms)) {
        const selected_uom_obj = item.item_uoms.find((uom_item) => uom_item.uom === selected_uom);
        item.conversion_factor = selected_uom_obj ? parseFloat(selected_uom_obj.conversion_factor) : 1;
      } else {
        item.conversion_factor = 1;
      }
      
      // حفظ السعر الأساسي إذا لم يكن محفوظاً مسبقاً
      if (!item.base_rate && item.price_list_rate) {
        item.base_rate = item.price_list_rate;
      }
      
      if (!item.posa_offer_applied) {
        item.discount_amount = 0;
        item.discount_percentage = 0;
      }
      
      // إعادة حساب السعر بناءً على عامل التحويل
      if (item.batch_price) {
        item.price_list_rate = item.batch_price * item.conversion_factor;
      } else if (item.base_rate) {
        // إعادة حساب السعر بناءً على عامل التحويل
        item.price_list_rate = item.base_rate * item.conversion_factor;
        item.rate = item.price_list_rate;
      }
      
      // حساب كمية المخزون
      this.calc_stock_qty(item, item.qty);
      
      this.update_item_detail(item);
    },

    calc_stock_qty(item, value) {
      // تأكد من أن item موجود
      if (!item) return;
      
      // تحويل القيم إلى أرقام بشكل مباشر
      const numValue = Number(value);
      value = numValue > 0 ? numValue : 1;
      
      // تأكد من أن conversion_factor رقم صحيح
      const convFactor = Number(item.conversion_factor || 1);
      item.conversion_factor = convFactor > 0 ? convFactor : 1;
      
      // حساب stock_qty بشكل صحيح
      item.stock_qty = item.conversion_factor * value;
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
        this.calc_stock_qty(item, item.qty);
        this.$forceUpdate();
      }
    },

    set_batch_qty(item, value, update = true) {
      const existing_items = this.items.filter(
        (element) =>
          element.item_code == item.item_code &&
          element.posa_row_id != item.posa_row_id
      );
      const used_batches = {};
      item.batch_no_data.forEach((batch) => {
        used_batches[batch.batch_no] = {
          ...batch,
          used_qty: 0,
          remaining_qty: batch.batch_qty,
        };
        existing_items.forEach((element) => {
          if (element.batch_no && element.batch_no == batch.batch_no) {
            used_batches[batch.batch_no].used_qty += element.qty;
            used_batches[batch.batch_no].remaining_qty -= element.qty;
            used_batches[batch.batch_no].batch_qty -= element.qty;
          }
        });
      });

      // set item batch_no based on:
      // 1. if batch has expiry_date we should use the batch with the nearest expiry_date
      // 2. if batch has no expiry_date we should use the batch with the earliest manufacturing_date
      // 3. we should not use batch with remaining_qty = 0
      // 4. we should the highest remaining_qty
      const batch_no_data = Object.values(used_batches)
        .filter((batch) => batch.remaining_qty > 0)
        .sort((a, b) => {
          if (a.expiry_date && b.expiry_date) {
            return a.expiry_date - b.expiry_date;
          } else if (a.expiry_date) {
            return -1;
          } else if (b.expiry_date) {
            return 1;
          } else if (a.manufacturing_date && b.manufacturing_date) {
            return a.manufacturing_date - b.manufacturing_date;
          } else if (a.manufacturing_date) {
            return -1;
          } else if (b.manufacturing_date) {
            return 1;
          } else {
            return b.remaining_qty - a.remaining_qty;
          }
        });
      if (batch_no_data.length > 0) {
        let batch_to_use = null;
        if (value) {
          batch_to_use = batch_no_data.find((batch) => batch.batch_no == value);
        }
        if (!batch_to_use) {
          batch_to_use = batch_no_data[0];
        }
        item.batch_no = batch_to_use.batch_no;
        item.actual_batch_qty = batch_to_use.batch_qty;
        item.batch_no_expiry_date = batch_to_use.expiry_date;
        if (batch_to_use.batch_price) {
          item.batch_price = batch_to_use.batch_price;
          item.price_list_rate = batch_to_use.batch_price;
          item.rate = batch_to_use.batch_price;
        } else if (update) {
          item.batch_price = null;
          this.update_item_detail(item);
        }
      } else {
        item.batch_no = null;
        item.actual_batch_qty = null;
        item.batch_no_expiry_date = null;
        item.batch_price = null;
      }
      // update item batch_no_data from batch_no_data
      item.batch_no_data = batch_no_data;
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
      // إضافة Debouncing لتحسين الأداء
      if (this._offersDebounceTimer) {
        clearTimeout(this._offersDebounceTimer);
      }
      
      this._offersDebounceTimer = setTimeout(() => {
        this._processOffers();
      }, 300);
    },

    _processOffers() {
      const offers = [];
      this.posOffers.forEach((offer) => {
        if (offer.apply_on === "Item Code") {
          const itemOffer = this.getItemOffer(offer);
          if (itemOffer) {
            offers.push(itemOffer);
          }
        } else if (offer.apply_on === "Item Group") {
          const groupOffer = this.getGroupOffer(offer);
          if (groupOffer) {
            offers.push(groupOffer);
          }
        } else if (offer.apply_on === "Brand") {
          const brandOffer = this.getBrandOffer(offer);
          if (brandOffer) {
            offers.push(brandOffer);
          }
        } else if (offer.apply_on === "Transaction") {
          const transactionOffer = this.getTransactionOffer(offer);
          if (transactionOffer) {
            offers.push(transactionOffer);
          }
        }
      });

      this.setItemGiveOffer(offers);
      this.updatePosOffers(offers);
    },

    setItemGiveOffer(offers) {
      // Set item give offer for replace
      offers.forEach((offer) => {
        if (
          offer.apply_on == "Item Code" &&
          offer.apply_type == "Item Code" &&
          offer.replace_item
        ) {
          offer.give_item = offer.item;
          offer.apply_item_code = offer.item;
        } else if (
          offer.apply_on == "Item Group" &&
          offer.apply_type == "Item Group" &&
          offer.replace_cheapest_item
        ) {
          const offerItemCode = this.getCheapestItem(offer).item_code;
          offer.give_item = offerItemCode;
          offer.apply_item_code = offerItemCode;
        }
      });
    },

    getCheapestItem(offer) {
      let itemsRowID;
      if (typeof offer.items === "string") {
        itemsRowID = JSON.parse(offer.items);
      } else {
        itemsRowID = offer.items;
      }
      const itemsList = [];
      itemsRowID.forEach((row_id) => {
        itemsList.push(this.getItemFromRowID(row_id));
      });
      const result = itemsList.reduce(function (res, obj) {
        return !obj.posa_is_replace &&
          !obj.posa_is_offer &&
          obj.price_list_rate < res.price_list_rate
          ? obj
          : res;
      });
      return result;
    },

    getItemFromRowID(row_id) {
      const item = this.items.find((el) => el.posa_row_id == row_id);
      return item;
    },

    chech_qty_amount_offer(offer, qty, amount) {
      const cacheKey = `offer_${offer.name}_${qty}_${amount}`;
      
      
      if (this._cachedCalculations.has(cacheKey)) {
        return this._cachedCalculations.get(cacheKey);
      }
      
      let min_qty = true;
      let max_qty = true;
      let min_amt = true;
      let max_amt = true;
      const applys = [];
      
      if (offer.min_qty > 0) {
        min_qty = qty >= offer.min_qty;
        applys.push(min_qty);
      }
      
      if (offer.max_qty > 0) {
        max_qty = qty <= offer.max_qty;
        applys.push(max_qty);
      }
      
      if (offer.min_amt > 0) {
        min_amt = amount >= offer.min_amt;
        applys.push(min_amt);
      }
      
      if (offer.max_amt > 0) {
        max_amt = amount <= offer.max_amt;
        applys.push(max_amt);
      }
      
      const apply = !applys.includes(false);
      const result = {
        apply: apply,
        conditions: { min_qty, max_qty, min_amt, max_amt }
      };
      
      
      this._cachedCalculations.set(cacheKey, result);
      return result;
    },

    checkOfferCoupon(offer) {
      if (!offer.coupon_based) {
        offer.coupon = null;
        return true;
      }
      
      // استخدام خريطة للبحث الأسرع
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
      if (offer.apply_on === "Item Code") {
        if (this.checkOfferCoupon(offer)) {
          this.items.forEach((item) => {
            if (!item.posa_is_offer && item.item_code === offer.item) {
              const items = [];
              if (
                offer.offer === "Item Price" &&
                item.posa_offer_applied &&
                !this.checkOfferIsAppley(item, offer)
              ) {
              } else {
                // التأكد من أن stock_qty رقم صحيح
                const itemQty = Number(item.qty) > 0 ? Number(item.qty) : 1;
                item.stock_qty = Number(item.stock_qty) > 0 ? Number(item.stock_qty) : itemQty;
                
                
                const res = this.chech_qty_amount_offer(
                  offer,
                  item.stock_qty,
                  item.stock_qty * (item.price_list_rate || 0)
                );
                if (res.apply) {
                  items.push(item.posa_row_id);
                  offer.items = items;
                  apply_offer = offer;
                }
              }
            }
          });
        }
      }
      return apply_offer;
    },

    getGroupOffer(offer) {
      let apply_offer = null;
      if (offer.apply_on === "Item Group") {
        if (this.checkOfferCoupon(offer)) {
          const items = [];
          let total_count = 0;
          let total_amount = 0;
          this.items.forEach((item) => {
            if (!item.posa_is_offer && item.item_group === offer.item_group) {
              if (
                offer.offer === "Item Price" &&
                item.posa_offer_applied &&
                !this.checkOfferIsAppley(item, offer)
              ) {
              } else {
                // التأكد من أن stock_qty رقم صحيح
                const itemQty = Number(item.qty) > 0 ? Number(item.qty) : 1;
                item.stock_qty = Number(item.stock_qty) > 0 ? Number(item.stock_qty) : itemQty;
                
                total_count += item.stock_qty;
                total_amount += item.stock_qty * (item.price_list_rate || 0);
                items.push(item.posa_row_id);
              }
            }
          });
          if (total_count || total_amount) {
            const res = this.chech_qty_amount_offer(
              offer,
              total_count,
              total_amount
            );
            if (res.apply) {
              offer.items = items;
              apply_offer = offer;
            }
          }
        }
      }
      return apply_offer;
    },

    getBrandOffer(offer) {
      let apply_offer = null;
      if (offer.apply_on === "Brand") {
        if (this.checkOfferCoupon(offer)) {
          const items = [];
          let total_count = 0;
          let total_amount = 0;
          this.items.forEach((item) => {
            if (!item.posa_is_offer && item.brand === offer.brand) {
              if (
                offer.offer === "Item Price" &&
                item.posa_offer_applied &&
                !this.checkOfferIsAppley(item, offer)
              ) {
              } else {
                // التأكد من أن stock_qty رقم صحيح
                const itemQty = Number(item.qty) > 0 ? Number(item.qty) : 1;
                item.stock_qty = Number(item.stock_qty) > 0 ? Number(item.stock_qty) : itemQty;
                
                total_count += item.stock_qty;
                total_amount += item.stock_qty * (item.price_list_rate || 0);
              }
            }
          });
          if (total_count || total_amount) {
            const res = this.chech_qty_amount_offer(
              offer,
              total_count,
              total_amount
            );
            if (res.apply) {
              offer.items = items;
              apply_offer = offer;
            }
          }
        }
      }
      return apply_offer;
    },
    getTransactionOffer(offer) {
      let apply_offer = null;
      if (offer.apply_on === "Transaction") {
        if (this.checkOfferCoupon(offer)) {
          let total_qty = 0;
          this.items.forEach((item) => {
            // تعديل الشرط ليشمل الأصناف في الفواتير المسودة
            if ((!item.posa_is_offer && !item.posa_is_replace) || (this.invoice_doc?.docstatus === 0)) {
              // التأكد من أن stock_qty رقم صحيح
              const itemQty = Number(item.qty) > 0 ? Number(item.qty) : 1;
              item.stock_qty = Number(item.stock_qty) > 0 ? Number(item.stock_qty) : itemQty;
              
              total_qty += item.stock_qty;
            }
          });
          const items = [];
          const total_count = total_qty;
          const total_amount = this.Total;
          if (total_count || total_amount) {
            const res = this.chech_qty_amount_offer(
              offer,
              total_count,
              total_amount
            );
            if (res.apply) {
              this.items.forEach((item) => {
                items.push(item.posa_row_id);
              });
              offer.items = items;
              apply_offer = offer;
            }
          }
        }
      }
      return apply_offer;
    },

    updatePosOffers(offers) {
      evntBus.emit("update_pos_offers", offers);
    },

    updateInvoiceOffers(offers) {
      this.posa_offers.forEach((invoiceOffer) => {
        const existOffer = offers.find(
          (offer) => invoiceOffer.row_id == offer.row_id
        );
        if (!existOffer) {
          this.removeApplyOffer(invoiceOffer);
        }
      });
      offers.forEach((offer) => {
        const existOffer = this.posa_offers.find(
          (invoiceOffer) => invoiceOffer.row_id == offer.row_id
        );
        if (existOffer) {
          existOffer.items = JSON.stringify(offer.items);
          if (
            existOffer.offer === "Give Product" &&
            existOffer.give_item &&
            existOffer.give_item != offer.give_item
          ) {
            const item_to_remove = this.items.find(
              (item) => item.posa_row_id == existOffer.give_item_row_id
            );
            if (item_to_remove) {
              const updated_item_offers = offer.items.filter(
                (row_id) => row_id != item_to_remove.posa_row_id
              );
              offer.items = updated_item_offers;
              this.remove_item(item_to_remove);
              existOffer.give_item_row_id = null;
              existOffer.give_item = null;
            }
            const newItemOffer = this.ApplyOnGiveProduct(offer);
            if (offer.replace_cheapest_item) {
              const cheapestItem = this.getCheapestItem(offer);
              const oldBaseItem = this.items.find(
                (el) => el.posa_row_id == item_to_remove.posa_is_replace
              );
              newItemOffer.qty = item_to_remove.qty;
              if (oldBaseItem && !oldBaseItem.posa_is_replace) {
                oldBaseItem.qty += item_to_remove.qty;
              } else {
                const restoredItem = this.ApplyOnGiveProduct(
                  {
                    given_qty: item_to_remove.qty,
                  },
                  item_to_remove.item_code
                );
                restoredItem.posa_is_offer = 0;
                this.items.unshift(restoredItem);
              }
              newItemOffer.posa_is_offer = 0;
              newItemOffer.posa_is_replace = cheapestItem.posa_row_id;
              const diffQty = cheapestItem.qty - newItemOffer.qty;
              if (diffQty <= 0) {
                newItemOffer.qty += diffQty;
                this.remove_item(cheapestItem);
                newItemOffer.posa_row_id = cheapestItem.posa_row_id;
                newItemOffer.posa_is_replace = newItemOffer.posa_row_id;
              } else {
                cheapestItem.qty = diffQty;
              }
            }
            this.items.unshift(newItemOffer);
            existOffer.give_item_row_id = newItemOffer.posa_row_id;
            existOffer.give_item = newItemOffer.item_code;
          } else if (
            existOffer.offer === "Give Product" &&
            existOffer.give_item &&
            existOffer.give_item == offer.give_item &&
            (offer.replace_item || offer.replace_cheapest_item)
          ) {
            this.$nextTick(function () {
              const offerItem = this.getItemFromRowID(
                existOffer.give_item_row_id
              );
              const diff = offer.given_qty - offerItem.qty;
              if (diff > 0) {
                const itemsRowID = JSON.parse(existOffer.items);
                const itemsList = [];
                itemsRowID.forEach((row_id) => {
                  itemsList.push(this.getItemFromRowID(row_id));
                });
                const existItem = itemsList.find(
                  (el) =>
                    el.item_code == offerItem.item_code &&
                    el.posa_is_replace != offerItem.posa_row_id
                );
                if (existItem) {
                  const diffExistQty = existItem.qty - diff;
                  if (diffExistQty > 0) {
                    offerItem.qty += diff;
                    existItem.qty -= diff;
                  } else {
                    offerItem.qty += existItem.qty;
                    this.remove_item(existItem);
                  }
                }
              }
            });
          } else if (existOffer.offer === "Item Price") {
            this.ApplyOnPrice(offer);
          } else if (existOffer.offer === "Grand Total") {
            this.ApplyOnTotal(offer);
          }
          this.addOfferToItems(existOffer);
        } else {
          this.applyNewOffer(offer);
        }
      });
    },

    removeApplyOffer(invoiceOffer) {
      if (invoiceOffer.offer === "Item Price") {
        this.RemoveOnPrice(invoiceOffer);
        const index = this.posa_offers.findIndex(
          (el) => el.row_id === invoiceOffer.row_id
        );
        this.posa_offers.splice(index, 1);
      }
      if (invoiceOffer.offer === "Give Product") {
        const item_to_remove = this.items.find(
          (item) => item.posa_row_id == invoiceOffer.give_item_row_id
        );
        const index = this.posa_offers.findIndex(
          (el) => el.row_id === invoiceOffer.row_id
        );
        this.posa_offers.splice(index, 1);
        this.remove_item(item_to_remove);
      }
      if (invoiceOffer.offer === "Grand Total") {
        this.RemoveOnTotal(invoiceOffer);
        const index = this.posa_offers.findIndex(
          (el) => el.row_id === invoiceOffer.row_id
        );
        this.posa_offers.splice(index, 1);
      }
      if (invoiceOffer.offer === "Loyalty Point") {
        const index = this.posa_offers.findIndex(
          (el) => el.row_id === invoiceOffer.row_id
        );
        this.posa_offers.splice(index, 1);
      }
      this.deleteOfferFromItems(invoiceOffer);
    },

    applyNewOffer(offer) {
      if (offer.offer === "Item Price") {
        this.ApplyOnPrice(offer);
      }
      if (offer.offer === "Give Product") {
        let itemsRowID;
        if (typeof offer.items === "string") {
          itemsRowID = JSON.parse(offer.items);
        } else {
          itemsRowID = offer.items;
        }
        if (
          offer.apply_on == "Item Code" &&
          offer.apply_type == "Item Code" &&
          offer.replace_item
        ) {
          const item = this.ApplyOnGiveProduct(offer, offer.item);
          item.posa_is_replace = itemsRowID[0];
          const baseItem = this.items.find(
            (el) => el.posa_row_id == item.posa_is_replace
          );
          const diffQty = baseItem.qty - offer.given_qty;
          item.posa_is_offer = 0;
          if (diffQty <= 0) {
            item.qty = baseItem.qty;
            this.remove_item(baseItem);
            item.posa_row_id = item.posa_is_replace;
          } else {
            baseItem.qty = diffQty;
          }
          this.items.unshift(item);
          offer.give_item_row_id = item.posa_row_id;
        } else if (
          offer.apply_on == "Item Group" &&
          offer.apply_type == "Item Group" &&
          offer.replace_cheapest_item
        ) {
          const itemsList = [];
          itemsRowID.forEach((row_id) => {
            itemsList.push(this.getItemFromRowID(row_id));
          });
          const baseItem = itemsList.find(
            (el) => el.item_code == offer.give_item
          );
          const item = this.ApplyOnGiveProduct(offer, offer.give_item);
          item.posa_is_offer = 0;
          item.posa_is_replace = baseItem.posa_row_id;
          const diffQty = baseItem.qty - offer.given_qty;
          if (diffQty <= 0) {
            item.qty = baseItem.qty;
            this.remove_item(baseItem);
            item.posa_row_id = item.posa_is_replace;
          } else {
            baseItem.qty = diffQty;
          }
          this.items.unshift(item);
          offer.give_item_row_id = item.posa_row_id;
        } else {
          const item = this.ApplyOnGiveProduct(offer);
          this.items.unshift(item);
          if (item) {
            offer.give_item_row_id = item.posa_row_id;
          }
        }
      }
      if (offer.offer === "Grand Total") {
        this.ApplyOnTotal(offer);
      }
      if (offer.offer === "Loyalty Point") {
        evntBus.emit("show_mesage", {
          text: "تم تطبيق عرض نقاط الولاء",
          color: "success",
        });
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
      this.addOfferToItems(newOffer);
    },

    ApplyOnGiveProduct(offer, item_code) {
      if (!item_code) {
        item_code = offer.give_item;
      }
      const items = this.allItems;
      const item = items.find((item) => item.item_code == item_code);
      if (!item) {
        return;
      }
      const new_item = { ...item };
      new_item.qty = offer.given_qty;
      new_item.stock_qty = offer.given_qty;
      new_item.rate = offer.discount_type === "Rate" ? offer.rate : item.rate;
      new_item.discount_amount =
        offer.discount_type === "Discount Amount" ? offer.discount_amount : 0;
      new_item.discount_percentage =
        offer.discount_type === "Discount Percentage"
          ? offer.discount_percentage
          : 0;
      new_item.discount_amount_per_item = 0;
      new_item.uom = item.uom ? item.uom : item.stock_uom;
      new_item.uom = new_item.uom && new_item.uom.uom ? new_item.uom.uom : new_item.uom;
      new_item.actual_batch_qty = "";
      new_item.conversion_factor = 1;
      new_item.posa_offers = JSON.stringify([]);
      new_item.posa_offer_applied = 0;
      new_item.posa_is_offer = 1;
      new_item.posa_is_replace = null;
      new_item.posa_notes = "";
      new_item.posa_delivery_date = "";
      new_item.posa_row_id = this.makeid(20);
      new_item.price_list_rate =
        (offer.discount_type === "Rate" && !offer.rate) ||
        (offer.discount_type === "Discount Percentage" &&
          offer.discount_percentage == 0)
          ? 0
          : item.rate;
      if (
        (!this.pos_profile.posa_auto_set_batch && new_item.has_batch_no) ||
        new_item.has_serial_no
      ) {
        this.expanded.push(new_item);
      }
      this.update_item_detail(new_item);
      return new_item;
    },

    ApplyOnPrice(offer) {
      this.items.forEach((item) => {
        if (offer.items.includes(item.posa_row_id)) {
          const item_offers = JSON.parse(item.posa_offers);
          if (!item_offers.includes(offer.row_id)) {
            if (offer.discount_type === "Rate") {
              item.rate = offer.rate;
            } else if (offer.discount_type === "Discount Percentage") {
              item.discount_percentage += offer.discount_percentage;
            } else if (offer.discount_type === "Discount Amount") {
              item.discount_amount += offer.discount_amount;
            }
            item.posa_offer_applied = 1;
            this.calc_item_price(item);
          }
        }
      });
    },

    RemoveOnPrice(offer) {
      this.items.forEach((item) => {
        const item_offers = JSON.parse(item.posa_offers);
        if (item_offers.includes(offer.row_id)) {
          const originalOffer = this.posOffers.find(
            (el) => el.name == offer.offer_name
          );
          if (originalOffer) {
            if (originalOffer.discount_type === "Rate") {
              item.rate = item.price_list_rate;
            } else if (originalOffer.discount_type === "Discount Percentage") {
              item.discount_percentage -= offer.discount_percentage;
              if (!item.discount_percentage) {
                item.discount_percentage = 0;
                item.discount_amount = 0;
                item.rate = item.price_list_rate;
              }
            } else if (originalOffer.discount_type === "Discount Amount") {
              item.discount_amount -= offer.discount_amount;
            }
            this.calc_item_price(item);
          }
        }
      });
    },

    ApplyOnTotal(offer) {
      if (!offer.name) {
        offer = this.posOffers.find((el) => el.name == offer.offer_name);
      }
      if (
        (!this.discount_percentage_offer_name ||
          this.discount_percentage_offer_name == offer.name) &&
        offer.discount_percentage > 0 &&
        offer.discount_percentage <= 100
      ) {
        this.discount_amount = this.flt(
          (flt(this.Total) * flt(offer.discount_percentage)) / 100,
          this.currency_precision
        );
        this.discount_percentage_offer_name = offer.name;
      }
    },

    RemoveOnTotal(offer) {
      if (
        this.discount_percentage_offer_name &&
        this.discount_percentage_offer_name == offer.offer_name
      ) {
        this.discount_amount = 0;
        this.discount_percentage_offer_name = null;
      }
    },

    addOfferToItems(offer) {
      const offer_items = JSON.parse(offer.items);
      offer_items.forEach((el) => {
        this.items.forEach((exist_item) => {
          if (exist_item.posa_row_id == el) {
            const item_offers = JSON.parse(exist_item.posa_offers);
            if (!item_offers.includes(offer.row_id)) {
              item_offers.push(offer.row_id);
              if (offer.offer === "Item Price") {
                exist_item.posa_offer_applied = 1;
              }
            }
            exist_item.posa_offers = JSON.stringify(item_offers);
          }
        });
      });
    },

    deleteOfferFromItems(offer) {
      const offer_items = JSON.parse(offer.items);
      offer_items.forEach((el) => {
        this.items.forEach((exist_item) => {
          if (exist_item.posa_row_id == el) {
            const item_offers = JSON.parse(exist_item.posa_offers);
            const updated_item_offers = item_offers.filter(
              (row_id) => row_id != offer.row_id
            );
            if (offer.offer === "Item Price") {
              exist_item.posa_offer_applied = 0;
            }
            exist_item.posa_offers = JSON.stringify(updated_item_offers);
          }
        });
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
          // printWindow.close();
          // NOTE : uncomoent this to auto closing printing window
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
        console.log('Invoice.vue:debugTableDimensions rows=', rows.length);
        rows.forEach((row, rIdx) => {
          console.log(`Invoice.vue:debug Row ${rIdx} height=${row.offsetHeight}`);
          [...row.children].forEach((cell, cIdx) => {
            const cs = window.getComputedStyle(cell);
            console.log(`Invoice.vue:debug Row${rIdx} Cell${cIdx} w=${cell.offsetWidth} h=${cell.offsetHeight} padT=${cs.paddingTop} padB=${cs.paddingBottom} padL=${cs.paddingLeft} padR=${cs.paddingRight} lineH=${cs.lineHeight}`);
          });
        });
      } catch (e) {
        console.error('Invoice.vue:debugTableDimensions error', e);
      }
    },
    printInvoice() {
      if (!this.invoice_doc || !this.items || !this.items.length) {
        evntBus.emit("show_mesage", {
          text: "لا توجد فاتورة للطباعة",
          color: "error",
        });
        return;
      }

      const paymentsComponent = this.getPaymentsComponent();
      if (!paymentsComponent) {
        evntBus.emit("show_mesage", {
          text: "تعذر الوصول إلى شاشة الدفع للطباعة",
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
          text: "يرجى اختيار طريقة دفع",
          color: "warning",
        });
        return;
      }

      evntBus.emit("show_loading", {
        text: "جاري معالجة الفاتورة للطباعة...",
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
            text: "تعذر تجهيز الفاتورة للطباعة: " + error.message,
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
          // تنظيف الذاكرة المؤقتة عند تحميل المكون
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
      // existing event bus bindings...
      this.debugTableDimensions();
    });
    evntBus.on("send_invoice_doc_payment", (doc) => {
      this.invoice_doc = doc;
    });
    evntBus.on("request_invoice_print", async () => {
      try {
        if (!this.canPrintInvoice()) {
          evntBus.emit("show_mesage", {
            text: "يرجى اختيار طريقة دفع قبل الطباعة",
            color: "warning",
          });
          return;
        }
        const invoice_doc = await this.process_invoice();
        evntBus.emit("send_invoice_doc_payment", invoice_doc);
        this.printInvoice();
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "تعذر تجهيز الفاتورة للطباعة: " + error.message,
          color: "error",
        });
        console.error("request_invoice_print error", error);
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
    
    // تنظيف الذاكرة المؤقتة
    this._cachedCalculations.clear();
    this._couponCache = null;
    
    // تنظيف Timers
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
      // Update toggle key when invoice type is changed from elsewhere
    },
    invoice_doc: {
      deep: true,
      handler(newDoc) {
        // Force update totals from backend when invoice changes
        evntBus.emit("update_invoice_doc", newDoc);
        if (newDoc && newDoc.name) {
          this.$forceUpdate();
        }
      },
    },
    discount_amount() {
      if (!this.discount_amount || this.discount_amount == 0) {
        this.additional_discount_percentage = 0;
      } else {
        this.additional_discount_percentage =
          (this.discount_amount / this.Total) * 100;
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
/* تنسيق حاوية العميل */
.customer-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* تنسيق عرض رقم الفاتورة */
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

/* تنسيق الفاتورة العادية - أزرق غامق */
.regular-invoice .invoice-number-text {
  color: #1976d2 !important;
  font-weight: bold !important;
}

/* تنسيق فاتورة المرتجع - أحمر غامق */
.return-invoice .invoice-number-text {
  color: #d32f2f !important;
  font-weight: bold !important;
}

/* تنسيق عدم وجود فاتورة - رمادي مائل */
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

/* زر الزيادة - أخضر مع شكل موجب */
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

/* زر النقصان - أصفر مع شكل سالب */
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