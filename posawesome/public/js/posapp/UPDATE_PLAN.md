# خطة تحديث ملفات الواجهة لاستخدام api_mapper.js

## الهدف
تحديث جميع ملفات Vue لاستخدام `API_MAP` من `api_mapper.js` بدلاً من كتابة الـ API endpoints مباشرة.

## المسار المرجعي
`/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/api_mapper.js`

---

## الملفات المطلوب تحديثها (مرتبة حسب الأولوية)

### 1. الملفات الأساسية (أولوية عالية)

#### 1.1 Invoice.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/Invoice.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.sales_invoice.create.create_invoice` → `API_MAP.SALES_INVOICE.CREATE`
- `posawesome.posawesome.api.sales_invoice.update.update_invoice` → `API_MAP.SALES_INVOICE.UPDATE`
- `posawesome.posawesome.api.sales_invoice.submit.submit_invoice` → `API_MAP.SALES_INVOICE.SUBMIT`
- `posawesome.posawesome.api.sales_invoice.delete.delete_invoice` → `API_MAP.SALES_INVOICE.DELETE`
- `posawesome.posawesome.api.customer.get_customer.get_customer` → `API_MAP.CUSTOMER.GET_CUSTOMER`
- `posawesome.posawesome.api.item.batch.process_batch_selection` → `API_MAP.ITEM.PROCESS_BATCH_SELECTION`
- `posawesome.posawesome.api.pos_offer.get_applicable_offers.get_applicable_offers` → `API_MAP.POS_OFFER.GET_APPLICABLE_OFFERS`
- `posawesome.posawesome.api.pos_profile.get_default_payment_from_pos_profile.get_default_payment_from_pos_profile` → `API_MAP.POS_PROFILE.GET_DEFAULT_PAYMENT`
- `frappe.client.get` → `API_MAP.FRAPPE.CLIENT_GET`
- `frappe.client.delete` → `API_MAP.FRAPPE.CLIENT_DELETE`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- استبدال 10 مواضع API calls

#### 1.2 ItemsSelector.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/ItemsSelector.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.item.get_items.get_items` → `API_MAP.ITEM.GET_ITEMS`
- `posawesome.posawesome.api.item.get_items_groups.get_items_groups` → `API_MAP.ITEM.GET_ITEMS_GROUPS`
- `posawesome.posawesome.api.item.get_items_barcode.get_items_barcode` → `API_MAP.ITEM.GET_ITEMS_BARCODE`
- `posawesome.posawesome.api.item.get_scale_barcode.get_scale_barcode` → `API_MAP.ITEM.GET_SCALE_BARCODE`
- `posawesome.posawesome.api.item.get_private_barcode.get_private_barcode` → `API_MAP.ITEM.GET_PRIVATE_BARCODE`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- حذف `const API_METHODS` الموجود
- استبدال 8 مواضع API calls

#### 1.3 Customer.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/Customer.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.customer.get_many_customers.get_many_customers` → `API_MAP.CUSTOMER.GET_MANY_CUSTOMERS`
- `posawesome.posawesome.api.customer.get_many_customers.get_customers_count` → `API_MAP.CUSTOMER.GET_CUSTOMERS_COUNT`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- حذف `const API_METHODS` الموجود
- استبدال 2 مواضع API calls

### 2. ملفات الدفع والإدارة (أولوية متوسطة)

#### 2.1 Payments.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/Payments.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.sales_invoice.submit.submit_invoice` → `API_MAP.SALES_INVOICE.SUBMIT`
- `frappe.client.get` → `API_MAP.FRAPPE.CLIENT_GET`
- `posawesome.posawesome.api.customer.get_customer_credit.get_customer_credit` → `API_MAP.CUSTOMER.GET_CUSTOMER_CREDIT`
- `posawesome.posawesome.api.customer.get_many_customer_addresses.get_many_customer_addresses` → `API_MAP.CUSTOMER.GET_MANY_CUSTOMER_ADDRESSES`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- حذف `const API_METHODS` الموجود
- استبدال 4 مواضع API calls

#### 2.2 UpdateCustomer.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/UpdateCustomer.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.customer.create_customer.create_customer` → `API_MAP.CUSTOMER.CREATE_CUSTOMER`
- `posawesome.posawesome.api.customer.update_customer.update_customer` → `API_MAP.CUSTOMER.UPDATE_CUSTOMER`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- حذف `const API_METHODS` الموجود
- استبدال 2 مواضع API calls

#### 2.3 Returns.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/Returns.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.sales_invoice.get_return.get_invoices_for_return` → `API_MAP.SALES_INVOICE.GET_INVOICES_FOR_RETURN`
- `frappe.client.get` → `API_MAP.FRAPPE.CLIENT_GET`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- حذف `const API_METHODS` الموجود
- استبدال 2 مواضع API calls

### 3. ملفات الإعدادات والمساعدة (أولوية منخفضة)

#### 3.1 OpeningDialog.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/OpeningDialog.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.pos_profile.get_opening_dialog_data.get_opening_dialog_data` → `API_MAP.POS_PROFILE.GET_OPENING_DIALOG_DATA`
- `posawesome.posawesome.api.pos_opening_shift.create_opening_voucher.create_opening_voucher` → `API_MAP.POS_OPENING_SHIFT.CREATE_OPENING_VOUCHER`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- حذف `const API_METHODS` الموجود
- استبدال 2 مواضع API calls

#### 3.2 Pos.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/Pos.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.pos_opening_shift.get_current_shift_name.get_current_shift_name` → `API_MAP.POS_OPENING_SHIFT.GET_CURRENT_SHIFT_NAME`
- `posawesome.posawesome.api.pos_offer.get_offers_for_profile.get_offers_for_profile` → `API_MAP.POS_OFFER.GET_OFFERS_FOR_PROFILE`
- `frappe.client.get` → `API_MAP.FRAPPE.CLIENT_GET`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- حذف `const API_METHODS` الموجود
- استبدال 3 مواضع API calls

#### 3.3 PosCoupons.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/PosCoupons.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.customer.get_customer_coupons.get_pos_coupon` → `API_MAP.CUSTOMER.GET_POS_COUPON`
- `posawesome.posawesome.api.customer.get_customer_coupons.get_customer_coupons` → `API_MAP.CUSTOMER.GET_CUSTOMER_COUPONS`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- حذف `const API_METHODS` الموجود
- استبدال 2 مواضع API calls

#### 3.4 NewAddress.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/pos/NewAddress.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.customer.create_customer_address.create_customer_address` → `API_MAP.CUSTOMER.CREATE_CUSTOMER_ADDRESS`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- استبدال 1 موضع API call

#### 3.5 Navbar.vue
**المسار:** `/home/frappe/frappe-bench-15/apps/posawesome/posawesome/public/js/posapp/components/Navbar.vue`
**APIs المستخدمة:**
- `posawesome.posawesome.api.pos_opening_shift.get_user_shift_invoice_count.get_user_shift_invoice_count` → `API_MAP.POS_OPENING_SHIFT.GET_USER_SHIFT_INVOICE_COUNT`
- `frappe.ping` → `API_MAP.FRAPPE.PING`

**التحديثات المطلوبة:**
- إضافة `import API_MAP from "../api_mapper";`
- استبدال 2 مواضع API calls

---

## إحصائيات التحديث

### إجمالي الملفات: 10 ملفات
### إجمالي API calls المطلوب تحديثها: 42 موضع

**توزيع API calls:**
- Sales Invoice APIs: 7 مواضع
- Customer APIs: 15 موضع
- Item APIs: 11 موضع
- POS Profile APIs: 3 مواضع
- POS Offer APIs: 2 موضع
- POS Opening Shift APIs: 4 مواضع

---

## خطوات التنفيذ المقترحة

1. **البدء بالملفات الأساسية** (Invoice.vue, ItemsSelector.vue, Customer.vue)
2. **ملفات الدفع والإدارة** (Payments.vue, UpdateCustomer.vue, Returns.vue)
3. **ملفات الإعدادات** (OpeningDialog.vue, Pos.vue, PosCoupons.vue, NewAddress.vue, Navbar.vue)

## نمط التحديث المطلوب

```javascript
// قبل التحديث
method: "posawesome.posawesome.api.sales_invoice.create.create_invoice"

// بعد التحديث
import API_MAP from "../api_mapper";
method: API_MAP.SALES_INVOICE.CREATE
```

---

## ملاحظات مهمة

1. **حذف const API_METHODS** من كل ملف بعد التحديث
2. **إضافة import** في بداية كل ملف
3. **التأكد من المسار النسبي** للـ import حسب موقع الملف
4. **اختبار كل ملف** بعد التحديث للتأكد من عدم وجود أخطاء

---

## المرحلة التالية

بعد الانتهاء من تحديث الملفات، يمكن:
- إزالة كود الحسابات المحلية من Invoice.vue
- تحسين performance عبر تقليل API calls المكررة
- إضافة error handling موحد