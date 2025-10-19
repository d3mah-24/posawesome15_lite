# 🚀          سريع لـ Invoice.vue

## 📊 الإحصائيات
- **إجم الأسطر:** 3,633
- **Template:** 280 سطر (8%)
- **Script:** 2,217 سطر (61%)
- **Style:** 1,136 سط (31%)

---

## 🏗️ الأقسام الرئيسية

### 1️⃣ الو (Template)
```
 Customer Section (قسم العمي)
 Items Table (جدول الأصناف)
  ├─ Qty Controls (أزرار +/-)
  ├─ Price Input (تعديل السعر)
 Discount Input (تعديل الخصم)  └
 Financial Summary (ملخص الحسابات)
  ├─ Total Qty (إجمالي الكميات)
  ├─ Net Total (الصافي)
  └─ Grand Total (الإجم)
 Action Buttons (أزرار العمليات)
   ├─ Print (طباعة)
   ├─ Pay (دفع)
   └─ Cancel (إلغاء)
```

### 2️⃣ البيانات (Data)
```javascript
{
  pos_profile: {...},        // إعدادات نقطة البيع
  invoice_doc: {...},        // الفاتورة من Server
  items: [...],              // الأصناف (LOCAL!)
  customer: "...",           // العميل
  posa_offers: [...],        // العروض
}
```

### 3️⃣ الدوال (Methods) - 70+ دالة

#### 🔵 عمليات الأصناف (10 دوال)
```javascript
add_item(item)              // إضافة ص
remove_item(item)           // حذف صنف
increaseQuantity(item)      // زيادة الكمية +
decreaseQuantity(item)      // تقليل الكمية -
onQtyChange(item)           // تغيير الكمية يدوياً
setItemRate(item)           // تعديل السعر
setDiscountPercentage(item) // تعديل الخصم
```

#### 🟢 عمليات الفاتورة (15 دالة)
```javascript
create_draft_invoice()      // إنشاء فاتورة جديدة
auto_update_invoice()       // التحديث التلقائي
update_invoice()            // تحديث فاتورة موجودة
get_invoice_doc()           // تجهيز بيانات للإرسال
cancel_invoice()            // إلغاء الفاتورة
new_invoice(data)           // فاتورة جديدة أو تحميل
```

#### 🟡 عمليات الدفع (5 دوال)
```javascript
show_payment()              // عرض شاشة الدفع
process_invoice()           //  قبل الدفع
printInvoice()              // طب الفاتورة
get_payments()              // طرق ال
```

#### 🔴 الدوال الحرجة (الحل!)
```javascript
updateItemsCalculatedFields(apiItems)  // ⭐ THE SOLUTION
// يُحدّث فقط: amount, net_amount, discount_amount
// يحتفظ بـ: price_list_rate, rate, qty

debouncedItemOperation()    // ⏱️ تأخير قبل API
// ينتظر ثانية واحدة بعد آخر تعديل
```

---

## 🔄 تدفق البيانات

### سيناريو: إضافة صنف
```
1. User يختار صنف
   ↓
2. add_item(item)
   ↓
3. items.push(new_item)  ✅ price_list_rate محفوظ
   ↓
4. create_draft_invoice() أو debouncedItemOperation()
   
5. Backend يحسب: amount, taxes, totals
   ↓
6. updateItemsCalculatedFields()  ✅ يحدّث المحسوب فقط
   ↓
7. price_list_rate لا يزال موجوداً ✅
```

---

## ⚠️ نقاط حرجة

### ✅ الصح
```javascript
// 1.         price_list_rate عند الإضافة
new_item.price_list_rate = item.price_list_rate || item.rate;
new_item.base_rate = item.base_rate || item.price_list_rate;

// 2. حدّث الحقول المحسوبة فقط
this.updateItemsCalculatedFields(apiItems);

// 3. استخدم debounce
this.debouncedItemOperation();
```

#### ❌ الخ

```javascript
// 1. لا تستبدل items كاملة
this.items = apiItems;  // ❌ يمسح price_list_rate

// 2. لا تستخدم mergeItemsFromAPI
this.mergeItemsFromAPI(apiItems);  // ❌ DEPRECATED

// 3. لا ترسل API 
this.auto_update_invoice();  // ❌ بدون debounce
```

---

## 🎯 الحل النهائي

### المشكلة
```
price_list_rate يختفي بعد إضافة صنف
```

### السب
```javascript
// القديم (خطأ):
this.items = apiResponse.items;  // استبدال كامل
```

### الحل
```javascript
// الجديد (صح):
this.updateItemsCalculatedFields(apiItems);
// يحدّث: amount, net_amount, discount_amount
// يحتفظ: price_list_rate, rate, qty
```

---

## 📋 قائمة التحقق

 تعديل الكود:

- [ ] هل price_list_rate محفوظ في add_item()?
- [ ] هل تستخدم updateItemsCalculatedFields() بدلاً م mergeItemsFromAPI()?
- [ ] هل تستخدم debouncedItemOperation() للـ user inputs?
- [ ] هل Backend يح والـ Frontend يعرض فقط?
- [ ] هل items[] محلي و يُستبدل من API?

---

## 🔗 ملفات ذات صلة

1. **Backend:**
   - `posawesome/api/sales_invoice/create.py`
   - `posawesome/api/sales_invoice/update.py`
   - `posawesome/api/sales_invoice/invoice_response.py`

2. **Frontend:**
   - `Invoice.vue` (هذ الملف)
   - `Customer.vue`
   - `Payment.vue`
   - `ItemsSelector.vue`

3. **Documentation:**
   - `INVOICE_VUE_ANALYSIS.md` (تحليل مفصل)
   - `INVOICE_VUE_VISUAL_GUIDE.txt` (مخططات بصرية)

---

## 
1. **قبل التعديل:**
   - اقرأ  في VISUAL_GUIDE.txtال
   - افهم الدوال في ANALYSIS.md

2. **عند الإضافة:**
   - لا تُضف logic في Template
   - اجعل الدوال صغيرة (< 50 سطر)
   - اس/home/frappe/frappe-bench-15/apps/posawesome/docs/INVOICE_QUICK_REFERENCE_AR.md computed للقيم المحسوبة

3. **عند الاختبار:**
   - اختبر إضافة صنف → price_list_rate موجود؟
   - اختبر تعديل qty → يحفظ السعر؟
   - اختبر الخصم → يحسب صح؟

---

**تم إنشاؤه:** 2025-10-19
**آخر تح:** بعد حل مشكلة price_list_rate
