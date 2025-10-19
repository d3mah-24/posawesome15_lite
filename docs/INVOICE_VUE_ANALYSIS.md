# 📊 تحليل شامل لملف Invoice.vue

## 📈 الإحصائيات العامة

```
إجمالي الأسطر: 3,633 سطر
├─ Template (HTML): 280 سطر (8%)
├─ Script (JavaScript): 2,217 سطر (61%)
└─ Style (CSS): 1,136 سطر (31%)

عدد Methods: ~70 دالة
عدد Computed Properties: 13
عدد Watchers: ~5
عدد Event Listeners: ~25
```

---

## 🏗️ البنية الأساسية

### 1️⃣ **القسم الأول: Template (الواجهة)**

#### أ) **Customer Section** - قسم العميل
```vue
<div class="compact-customer-section">
  <Customer></Customer>
</div>
```
**الدور:**
- عرض بيانات العميل الحالي
- السماح بتغيير العميل
- ربط الفاتورة بالعميل

---

#### ب) **Items Table** - جدول الأصناف
```vue
<v-data-table
  :headers="dynamicHeaders"
  :items="items"
  item-key="posa_row_id"
>
```

**الأعمدة (Columns):**

| العمود | المفتاح | الدور | قابل للتعديل؟ |
|--------|---------|------|---------------|
| **اسم الصنف** | `item_name` | عرض اسم المنتج | ❌ للقراءة فقط |
| **الكمية** | `qty` | كمية الصنف | ✅ نعم (+/-/input) |
| **الوحدة** | `uom` | وحدة القياس | ❌ للقراءة فقط |
| **السعر الأساسي** | `price_list_rate` | السعر من قائمة الأسعار | ❌ للقراءة فقط |
| **السعر بعد الخصم** | `rate` | السعر النهائي | ✅ نعم (إذا مسموح) |
| **نسبة الخصم** | `discount_percentage` | خصم % | ✅ نعم (إذا مسموح) |
| **مبلغ الخصم** | `discount_amount` | مبلغ الخصم محسوب | ❌ محسوب تلقائيًا |
| **المجموع** | `amount` | qty × rate | ❌ محسوب تلقائيًا |
| **حذف** | `actions` | زر الحذف | ✅ نعم |

**Templates للأعمدة:**
```vue
<template v-slot:item.qty="{ item }">
  <!-- أزرار +/- + input field -->
</template>

<template v-slot:item.rate="{ item }">
  <!-- input لتعديل السعر -->
</template>

<template v-slot:item.discount_percentage="{ item }">
  <!-- input لتعديل نسبة الخصم -->
</template>
```

---

#### ج) **Financial Summary** - ملخص الحسابات
```vue
<div class="financial-summary">
  <div>Total Qty</div>        <!-- إجمالي الكميات -->
  <div>Inv Disc %</div>        <!-- خصم الفاتورة % -->
  <div>Items Disc</div>        <!-- مجموع خصومات الأصناف -->
  <div>Before Disc</div>       <!-- المجموع قبل الخصم -->
  <div>Net Total</div>         <!-- الصافي -->
  <div>Tax</div>               <!-- الضريبة -->
  <div>Grand Total</div>       <!-- الإجمالي النهائي -->
</div>
```

---

#### د) **Action Buttons** - أزرار العمليات
```vue
<button @click="printInvoice">Print</button>     <!-- طباعة -->
<button @click="show_payment">Pay</button>       <!-- الدفع -->
<button @click="open_returns">Return</button>    <!-- مرتجع -->
<button @click="quick_return">Quick Return</button>
<button @click="cancel_invoice">Cancel</button>  <!-- إلغاء -->
```

---

## 💾 القسم الثاني: Data (البيانات)

### أ) **POS Configuration** - إعدادات نقطة البيع
```javascript
data() {
  return {
    pos_profile: null,           // ملف نقطة البيع
    pos_opening_shift: null,     // وردية الافتتاح
    stock_settings: null,        // إعدادات المخزون
  }
}
```

### ب) **Invoice Documents** - مستندات الفاتورة
```javascript
invoice_doc: null,    // الفاتورة الحالية (من Server)
return_doc: null,     // فاتورة المرتجع (إن وجدت)
```

### ج) **Customer Data** - بيانات العميل
```javascript
customer: "",         // اسم/كود العميل
customer_info: {},    // معلومات العميل التفصيلية
```

### د) **Items Management** - إدارة الأصناف
```javascript
items: [],            // قائمة الأصناف في الفاتورة
                      // كل صنف له:
                      // - item_code, item_name
                      // - qty, uom
                      // - price_list_rate, rate
                      // - discount_percentage, discount_amount
                      // - amount, net_amount
                      // - posa_row_id (unique ID)
```

### هـ) **Offers & Promotions** - العروض والكوبونات
```javascript
posa_offers: [],      // العروض المطبقة
posa_coupons: [],     // الكوبونات المستخدمة
```

### و) **State Management** - إدارة الحالة
```javascript
_itemOperationTimer: null,    // Timer للـ debounce
_updatingFromAPI: false,      // Flag لمنع التحديثات المتكررة
```

---

## 🧮 القسم الثالث: Computed Properties (الخصائص المحسوبة)

### 1. **dynamicHeaders** - أعمدة الجدول الديناميكية
```javascript
computed: {
  dynamicHeaders() {
    // يُظهر/يُخفي الأعمدة حسب إعدادات pos_profile
    // مثلاً: إخفاء عمود الخصم إذا غير مسموح
  }
}
```

### 2. **total_qty** - إجمالي الكميات
```javascript
total_qty() {
  return this.items.reduce((sum, item) => sum + item.qty, 0);
}
```

### 3. **total_before_discount** - المجموع قبل الخصم
```javascript
total_before_discount() {
  return this.items.reduce((sum, item) => {
    return sum + (item.qty * item.price_list_rate);
  }, 0);
}
```

### 4. **hasItems** - هل يوجد أصناف؟
```javascript
hasItems() {
  return this.items && this.items.length > 0;
}
```

### 5. **hasChosenPayment** - هل تم اختيار طريقة دفع؟
```javascript
hasChosenPayment() {
  return this.invoice_doc?.payments?.some(p => p.amount > 0);
}
```

---

## ⚙️ القسم الرابع: Methods (الدوال) - مقسّمة حسب الوظيفة

### 🔵 **المجموعة A: عمليات الأصناف (Item Operations)**

#### 1. **add_item(item)** - إضافة صنف
```javascript
async add_item(item) {
  // 1. التحقق من البيانات
  // 2. البحث عن صنف موجود
  // 3. إذا موجود: زيادة الكمية
  // 4. إذا جديد: إضافته للقائمة
  // 5. إذا أول صنف: إنشاء فاتورة جديدة
  // 6. وإلا: تحديث الفاتورة الموجودة
}
```
**متى يُستدعى؟**
- عند اختيار صنف من قائمة الأصناف
- عند مسح Barcode
- Event: `evntBus.on("add_item")`

---

#### 2. **remove_item(item)** - حذف صنف
```javascript
remove_item(item) {
  // 1. إيجاد index الصنف
  // 2. حذفه من المصفوفة
  // 3. إذا آخر صنف: حذف الفاتورة
  // 4. وإلا: تحديث الفاتورة
}
```

---

#### 3. **increaseQuantity(item)** - زيادة الكمية (+)
```javascript
increaseQuantity(item) {
  item.qty = item.qty + 1;
  this.$forceUpdate();
  evntBus.emit("item_updated", item);
}
```

#### 4. **decreaseQuantity(item)** - تقليل الكمية (-)
```javascript
decreaseQuantity(item) {
  item.qty = Math.max(0, item.qty - 1);
  if (item.qty === 0) {
    this.remove_item(item);
  } else {
    evntBus.emit("item_updated", item);
  }
}
```

---

#### 5. **onQtyChange(item)** - عند تغيير الكمية يدويًا
```javascript
onQtyChange(item) {
  item.qty = Number(item.qty) || 0;
  this.refreshTotals();
  this.debouncedItemOperation("qty-change");
}
```

---

#### 6. **setItemRate(item, event)** - تعديل السعر
```javascript
setItemRate(item, event) {
  // 1. قراءة السعر الجديد
  // 2. تحديث item.rate
  // 3. إعادة حساب نسبة الخصم
  // 4. تحديث الفاتورة (debounced)
}
```

---

#### 7. **setDiscountPercentage(item, event)** - تعديل نسبة الخصم
```javascript
setDiscountPercentage(item, event) {
  // 1. قراءة النسبة
  // 2. التحقق من الحد الأقصى
  // 3. حساب السعر الجديد
  // 4. تحديث الفاتورة (debounced)
}
```

---

#### 8. **getDiscountAmount(item)** - حساب مبلغ الخصم
```javascript
getDiscountAmount(item) {
  // محلي (Local): لا يستدعي Server
  return (item.price_list_rate * item.discount_percentage) / 100;
}
```

---

### 🟢 **المجموعة B: عمليات الفاتورة (Invoice Operations)**

#### 9. **create_draft_invoice()** - إنشاء فاتورة جديدة
```javascript
async create_draft_invoice() {
  const doc = this.get_invoice_doc("draft");
  const result = await this.create_invoice(doc);
  
  if (result) {
    this.invoice_doc = result;
    // تحديث الحقول المحسوبة فقط
    this.updateItemsCalculatedFields(result.items);
  }
}
```
**متى يُستدعى؟**
- عند إضافة أول صنف للفاتورة الفارغة

---

#### 10. **auto_update_invoice()** - التحديث التلقائي
```javascript
async auto_update_invoice(doc, reason) {
  // 1. تحديد: create أم update؟
  // 2. إرسال للـ Backend
  // 3. استقبال النتيجة
  // 4. تحديث الحقول المحسوبة فقط (لا تستبدل items)
  // 5. تحديث invoice_doc بالـ totals
}
```
**متى يُستدعى؟**
- بعد تعديل qty/rate/discount
- بعد إضافة/حذف صنف
- عبر `debouncedItemOperation()`

---

#### 11. **update_invoice(doc)** - تحديث فاتورة موجودة
```javascript
update_invoice(doc) {
  return new Promise((resolve, reject) => {
    frappe.call({
      method: API_MAP.SALES_INVOICE.UPDATE,
      args: { data: doc },
      callback: (r) => {
        if (r.message) {
          this.invoice_doc = r.message;
          resolve(r.message);
        }
      }
    });
  });
}
```

---

#### 12. **create_invoice(doc)** - إنشاء فاتورة (API Call)
```javascript
create_invoice(doc) {
  frappe.call({
    method: API_MAP.SALES_INVOICE.CREATE,
    args: { data: doc },
    callback: (r) => {
      this.invoice_doc = r.message;
      resolve(r.message);
    }
  });
}
```

---

#### 13. **get_invoice_doc(reason)** - تجهيز بيانات الفاتورة
```javascript
get_invoice_doc(reason) {
  return {
    name: this.invoice_doc?.name,
    doctype: "Sales Invoice",
    is_pos: 1,
    customer: this.customer,
    items: this.get_invoice_items_minimal(),
    discount_amount: this.discount_amount,
    additional_discount_percentage: this.additional_discount_percentage,
    // ... باقي الحقول
  };
}
```

---

#### 14. **get_invoice_items_minimal()** - تجهيز الأصناف للإرسال
```javascript
get_invoice_items_minimal() {
  return this.items.map(item => ({
    item_code: item.item_code,
    qty: item.qty,
    rate: item.rate,
    uom: item.uom,
    discount_percentage: item.discount_percentage,
    // فقط البيانات الأساسية، لا نرسل كل الحقول
  }));
}
```

---

#### 15. **cancel_invoice()** - إلغاء الفاتورة
```javascript
cancel_invoice() {
  // 1. حذف الفاتورة من Server
  // 2. تفريغ items
  // 3. إعادة تعيين customer
  // 4. تصفير المجاميع
}
```

---

#### 16. **delete_draft_invoice()** - حذف المسودة
```javascript
delete_draft_invoice() {
  frappe.call({
    method: API_MAP.SALES_INVOICE.DELETE,
    args: { invoice_name: this.invoice_doc.name }
  }).then(() => {
    this.reset_invoice_session();
  });
}
```

---

#### 17. **new_invoice(data)** - فاتورة جديدة أو تحميل موجودة
```javascript
new_invoice(data = {}) {
  if (!data.name) {
    // فاتورة جديدة فارغة
    this.items = [];
    this.customer = this.pos_profile?.customer;
    this.invoice_doc = "";
  } else {
    // تحميل فاتورة موجودة
    this.invoice_doc = data;
    this.items = data.items || [];
    this.customer = data.customer;
  }
}
```

---

### 🟡 **المجموعة C: عمليات الدفع (Payment Operations)**

#### 18. **show_payment()** - عرض شاشة الدفع
```javascript
async show_payment() {
  // 1. التحقق: عميل موجود + أصناف موجودة
  // 2. معالجة الفاتورة (process_invoice)
  // 3. إضافة طريقة دفع افتراضية إذا لزم
  // 4. إرسال الفاتورة لشاشة الدفع
  // 5. عرض شاشة الدفع
}
```

---

#### 19. **process_invoice()** - معالجة الفاتورة قبل الدفع
```javascript
async process_invoice() {
  const doc = this.get_invoice_doc("payment");
  return await this.update_invoice(doc);
}
```

---

#### 20. **printInvoice()** - طباعة الفاتورة
```javascript
printInvoice() {
  // 1. التحقق من وجود طريقة دفع
  // 2. معالجة الفاتورة
  // 3. Submit الفاتورة (تحويلها من Draft إلى Submitted)
  // 4. فتح صفحة الطباعة
}
```

---

#### 21. **get_payments()** - الحصول على طرق الدفع
```javascript
get_payments() {
  // 1. من invoice_doc إذا موجودة
  // 2. أو من pos_profile
  // 3. معالجة التقريب إذا لزم
  return payments;
}
```

---

### 🔴 **المجموعة D: عمليات خاصة (Special Operations)**

#### 22. **updateItemsCalculatedFields(apiItems)** - تحديث الحقول المحسوبة فقط
```javascript
updateItemsCalculatedFields(apiItems) {
  // ⚠️ هذه الدالة هي الحل لمشكلة اختفاء price_list_rate
  
  this.items.forEach(localItem => {
    const apiItem = apiItems.find(
      a => a.item_code === localItem.item_code
    );
    
    if (apiItem) {
      // ✅ نُحدّث فقط الحقول المحسوبة
      localItem.amount = apiItem.amount;
      localItem.net_amount = apiItem.net_amount;
      localItem.discount_amount = apiItem.discount_amount;
      
      // ❌ لا نُحدّث: price_list_rate, rate, qty
      //    (هذه user inputs يجب الحفاظ عليها)
    }
  });
}
```

---

#### 23. **mergeItemsFromAPI(apiItems)** - دمج الأصناف (DEPRECATED)
```javascript
mergeItemsFromAPI(apiItems) {
  // ⚠️ DEPRECATED - لا تُستخدم بعد الآن
  // السبب: كانت تستبدل items بالكامل
  //         مما يسبب اختفاء price_list_rate
  
  // استُبدلت بـ updateItemsCalculatedFields()
}
```

---

#### 24. **debouncedItemOperation(operation)** - التأخير قبل التحديث
```javascript
debouncedItemOperation(operation) {
  // مهمة جدًا: تمنع استدعاء API بعد كل keystroke
  
  clearTimeout(this._itemOperationTimer);
  
  this._itemOperationTimer = setTimeout(() => {
    this.sendInvoiceUpdate();
  }, 1000); // انتظر ثانية واحدة
}
```
**لماذا مهمة؟**
- المستخدم يكتب "15" في الكمية
- بدون debounce: سيرسل "1" ثم "15" (2 requests)
- مع debounce: ينتظر حتى ينتهي المستخدم، ثم يرسل "15" (1 request)

---

#### 25. **sendInvoiceUpdate()** - إرسال التحديث للـ Server
```javascript
sendInvoiceUpdate() {
  if (!this.invoice_doc?.name) return;
  
  const doc = this.get_invoice_doc("item-update");
  this.auto_update_invoice(doc, "item-update");
}
```

---

### 🟣 **المجموعة E: العروض والكوبونات (Offers & Coupons)**

#### 26. **handelOffers()** - معالجة العروض
```javascript
handelOffers() {
  if (this.items.length > 1) {
    this._processOffers();
  }
}
```

#### 27. **_processOffers()** - معالجة العروض من Server
```javascript
_processOffers() {
  frappe.call({
    method: API_MAP.POS_OFFER.GET_APPLICABLE_OFFERS,
    args: { invoice_name: this.invoice_doc.name },
    callback: (r) => {
      this.updatePosOffers(r.message);
    }
  });
}
```

---

### 🟠 **المجموعة F: الدوال المساعدة (Helper Functions)**

#### 28. **refreshTotals()** - تحديث العرض
```javascript
refreshTotals() {
  this.$forceUpdate(); // يُجبر Vue على إعادة الرسم
}
```

#### 29. **generateRowId()** - توليد ID فريد
```javascript
generateRowId() {
  return Date.now().toString(36) + Math.random().toString(36);
}
```

#### 30. **makeid(length)** - توليد ID عشوائي
```javascript
makeid(length) {
  return crypto.randomUUID().substring(0, length);
}
```

---

## 🔄 القسم الخامس: Event Bus (نظام الأحداث)

### Events التي يستمع لها (mounted):

```javascript
mounted() {
  // 1. إعدادات POS
  evntBus.on("register_pos_profile", (data) => {
    this.pos_profile = data.pos_profile;
  });
  
  // 2. عمليات الأصناف
  evntBus.on("add_item", (item) => {
    this.add_item(item);
  });
  
  evntBus.on("item_updated", (item) => {
    this.debouncedItemOperation("item-updated");
  });
  
  evntBus.on("item_removed", (item) => {
    this.debouncedItemOperation("item-removed");
  });
  
  // 3. عمليات العميل
  evntBus.on("update_customer", (customer) => {
    this.customer = customer;
  });
  
  evntBus.on("fetch_customer_details", () => {
    this.fetch_customer_details();
  });
  
  // 4. عمليات الفاتورة
  evntBus.on("new_invoice", () => {
    this.cancel_invoice();
  });
  
  evntBus.on("load_invoice", (data) => {
    this.new_invoice(data);
  });
  
  // 5. عمليات العروض
  evntBus.on("update_invoice_offers", (data) => {
    this.updateInvoiceOffers(data);
  });
  
  evntBus.on("update_invoice_coupons", (data) => {
    this.posa_coupons = data;
    this.debouncedItemOperation();
  });
  
  // 6. عمليات الدفع
  evntBus.on("send_invoice_doc_payment", (doc) => {
    this.invoice_doc = doc;
  });
  
  evntBus.on("payments_updated", (payments) => {
    if (this.invoice_doc) {
      this.invoice_doc.payments = payments;
    }
  });
}
```

---

## 🎨 القسم السادس: Styling (التنسيقات)

### المشكلة: 1,136 سطر CSS!

**أكبر الكتل:**
1. **Customer Section** (~150 سطر)
2. **Items Table** (~300 سطر)
3. **Quantity Controls** (~150 سطر)
4. **Payment Controls** (~200 سطر)
5. **Financial Summary** (~150 سطر)
6. **Action Buttons** (~100 سطر)

**الحل المقترح:**
```vue
<!-- بدلاً من: -->
<style scoped>
  /* 1,136 سطر CSS */
</style>

<!-- استخدم: -->
<style src="./Invoice.css" scoped></style>
```

---

## 🔍 القسم السابع: تدفق البيانات (Data Flow)

### سيناريو 1: إضافة صنف جديد

```
1. المستخدم يختار صنف
   ↓
2. ItemsSelector.vue → evntBus.emit("add_item", item)
   ↓
3. Invoice.vue → add_item(item)
   ↓
4. items.push(new_item) + تعيين price_list_rate
   ↓
5. إذا أول صنف → create_draft_invoice()
   وإلا → debouncedItemOperation("item-added")
   ↓
6. بعد ثانية → sendInvoiceUpdate()
   ↓
7. auto_update_invoice() → Backend
   ↓
8. Backend يحسب: amount, taxes, totals
   ↓
9. updateItemsCalculatedFields(response.items)
   - يُحدّث: amount, net_amount, discount_amount
   - يحتفظ بـ: price_list_rate, rate, qty
   ↓
10. invoice_doc = response (totals only)
```

---

### سيناريو 2: تعديل الكمية

```
1. المستخدم يضغط زر "+"
   ↓
2. increaseQuantity(item)
   ↓
3. item.qty++
   ↓
4. $forceUpdate() - تحديث العرض فورًا
   ↓
5. evntBus.emit("item_updated", item)
   ↓
6. debouncedItemOperation("qty-change")
   ↓
7. [انتظار 1 ثانية]
   ↓
8. sendInvoiceUpdate() → Backend
   ↓
9. updateItemsCalculatedFields() - تحديث الحقول المحسوبة
```

---

### سيناريو 3: الدفع

```
1. المستخدم يضغط "Pay"
   ↓
2. show_payment()
   ↓
3. التحقق: customer + items
   ↓
4. process_invoice() → update_invoice()
   ↓
5. Backend يحسب المجاميع النهائية
   ↓
6. إضافة طريقة دفع افتراضية إذا لزم
   ↓
7. evntBus.emit("send_invoice_doc_payment", invoice_doc)
   ↓
8. evntBus.emit("show_payment", "true")
   ↓
9. Payment.vue يظهر ويستقبل invoice_doc
```

---

## ⚠️ القسم الثامن: المشاكل والحلول

### المشكلة 1: اختفاء price_list_rate

**السبب:**
```javascript
// ❌ القديم (الخطأ):
this.items = apiItems; // استبدال كامل
```

**الحل:**
```javascript
// ✅ الجديد (الصح):
this.updateItemsCalculatedFields(apiItems);
// يُحدّث فقط: amount, net_amount, discount_amount
// يحتفظ بـ: price_list_rate, rate, qty
```

---

### المشكلة 2: استدعاءات API كثيرة

**السبب:**
```javascript
// كل keystroke يستدعي API
onQtyInput(item) {
  this.auto_update_invoice(); // ❌ مباشرة
}
```

**الحل:**
```javascript
// Debounce: انتظر حتى ينتهي المستخدم
onQtyInput(item) {
  this.debouncedItemOperation(); // ✅ بعد ثانية
}
```

---

### المشكلة 3: الكود كبير جدًا

**الحل المقترح:**

#### أ) تقسيم الكومبوننت
```
Invoice.vue (300 سطر)
├─ CustomerSection.vue
├─ ItemsTable.vue
│  ├─ ItemRow.vue
│  └─ ItemActions.vue
├─ FinancialSummary.vue
├─ PaymentControls.vue
└─ composables/
   ├─ useInvoice.js
   ├─ useItems.js
   └─ usePayments.js
```

#### ب) استخدام Composition API
```javascript
// بدلاً من Options API (methods, data, computed)
import { useInvoice } from '@/composables/useInvoice';

export default {
  setup() {
    const { 
      items, 
      invoice_doc,
      addItem,
      updateQty,
      showPayment 
    } = useInvoice();
    
    return { items, invoice_doc, addItem, updateQty, showPayment };
  }
}
```

---

## 📊 القسم التاسع: مقارنة بـ ERPNext الأصلي

| الميزة | ERPNext (1,169 سطر) | POSAwesome (3,633 سطر) |
|--------|---------------------|------------------------|
| **Framework** | Frappe Form | Vue.js Manual |
| **State** | Auto-managed | Manual arrays |
| **Calculations** | Backend-first | Mixed |
| **Styling** | Frappe CSS | 1,136 سطر inline |
| **Items Update** | Auto-calculate | Manual merge |
| **Events** | Form hooks | Event bus |
| **Complexity** | ⭐⭐ بسيط | ⭐⭐⭐⭐⭐ معقد |

---

## ✅ القسم العاشر: التوصيات النهائية

### 1. **اتبع نهج ERPNext:**
- Backend يحسب كل شيء
- Frontend فقط للعرض والإدخال
- لا تُعيد حساب الضرائب في Frontend

### 2. **احتفظ بـ Local State:**
```javascript
// ✅ صح
this.items[index].qty = 5; // Local
this.updateItemsCalculatedFields(apiResponse); // Server calculations

// ❌ خطأ
this.items = apiResponse.items; // يمسح price_list_rate
```

### 3. **استخدم Debounce:**
- 1 ثانية للـ qty/rate/discount
- فوري للـ add/remove

### 4. **قسّم الكومبوننت:**
- كل كومبوننت < 300 سطر
- CSS في ملفات منفصلة
- Logic في composables

---

## 🎯 الخلاصة

**Invoice.vue هو قلب نظام POS:**
- ✅ يدير الأصناف والكميات
- ✅ يحسب المجاميع والخصومات
- ✅ يتعامل مع العروض والكوبونات
- ✅ يُجهّز الفاتورة للدفع
- ❌ لكنه كبير جدًا ومعقد

**الحل:**
1. استخدم `updateItemsCalculatedFields()` بدلاً من `mergeItemsFromAPI()`
2. احتفظ بـ `price_list_rate` محليًا
3. Backend فقط للحسابات
4. Frontend فقط للعرض

---

**التحليل انتهى! 📊**
