# 🗺️ خريطة ملف Invoice.vue - POS Awesome

> شرح مبسط لتسلسل الكود وأجزاء الملف

---

## 📋 نظرة عامة

**الملف:** `Invoice.vue`  
**الوظيفة:** إدارة الفاتورة الرئيسية في نظام نقاط البيع  
**الحجم:** ~3700 سطر  
**اللغة:** Vue.js + JavaScript  

---

## 🏗️ هيكل الملف

### 1. **القسم الأول: Template (الواجهة)**
```vue
<template>
  <!-- جدول العناصر -->
  <v-data-table>
    <!-- أزرار زيادة/نقصان الكمية -->
    <button @click="increaseQuantity(item)">
    <button @click="decreaseQuantity(item)">
    
    <!-- حقول الإدخال -->
    <input v-model="item.qty" @change="onQtyChange(item)">
    <input @change="setItemRate(item, $event)">
  </v-data-table>
</template>
```

**الدور:** عرض واجهة الفاتورة مع الجدول والحقول والأزرار

---

### 2. **القسم الثاني: Data (البيانات)**
```javascript
data() {
  return {
    items: [],              // قائمة العناصر
    invoice_doc: null,      // بيانات الفاتورة
    customer: null,         // العميل
    pos_profile: null,      // إعدادات نقطة البيع
    
    // مؤقتات للتحكم في التحديثات
    _itemOperationTimer: null,
    _autoUpdateTimer: null,
  }
}
```

**الدور:** تخزين جميع البيانات والمتغيرات المطلوبة

---

### 3. **القسم الثالث: Methods (الدوال)**

#### 🔢 **إدارة الكمية**
```javascript
increaseQuantity(item) {
  item.qty = item.qty + 1;           // زيادة الكمية
  evntBus.emit("item_updated", item); // إرسال إشارة التحديث
}

decreaseQuantity(item) {
  item.qty = Math.max(0, item.qty - 1); // نقصان الكمية
  evntBus.emit("item_updated", item);   // إرسال إشارة التحديث
}

onQtyChange(item) {
  item.qty = Number(item.qty);        // تحديث الكمية من الحقل
  this.refreshTotals();               // إعادة حساب المجاميع
  this.debouncedItemOperation();       // بدء عملية التحديث المؤجلة
}
```

**الدور:** التعامل مع تغيير كميات العناصر

---

#### ⏰ **نظام التحديث المؤجل**
```javascript
debouncedItemOperation() {
  // إلغاء المؤقت السابق
  clearTimeout(this._itemOperationTimer);
  
  // انتظار ثانية واحدة، ثم إرسال التحديث
  this._itemOperationTimer = setTimeout(() => {
    this.sendInvoiceUpdate();
  }, 1000);
}

sendInvoiceUpdate() {
  const doc = this.get_invoice_doc("item-update");
  this.auto_update_invoice(doc, "item-update");
}
```

**الدور:** تجميع التحديثات وإرسالها للسيرفر بعد ثانية واحدة من توقف المستخدم

---

#### 💰 **إدارة الأسعار والخصومات**
```javascript
setItemRate(item, event) {
  item.rate = parseFloat(event.target.value);
  this.refreshTotals();
  this.debouncedItemOperation();
}

setDiscountPercentage(item, event) {
  item.discount_percentage = parseFloat(event.target.value);
  this.refreshTotals();
  this.debouncedItemOperation();
}
```

**الدور:** تحديث أسعار العناصر ونسب الخصم

---

#### 📤 **إرسال البيانات للسيرفر**
```javascript
auto_update_invoice(doc, reason) {
  return frappe.call({
    method: "posawesome.posawesome.api.sales_invoice.update_invoice.update_invoice",
    args: { data: doc }
  });
}

get_invoice_doc(reason) {
  // تجميع جميع بيانات الفاتورة
  return {
    name: this.invoice_doc?.name,
    items: this.items,
    customer: this.customer,
    // ... باقي البيانات
  };
}
```

**الدور:** إرسال بيانات الفاتورة المحدثة إلى الخادم

---

#### 🔄 **إدارة الأحداث**
```javascript
// استقبال إشارات التحديث
evntBus.on("item_updated", (item) => {
  this.debouncedItemOperation("item-updated");
});

evntBus.on("item_added", (item) => {
  this.debouncedItemOperation("item-added");
});
```

**الدور:** الاستماع للأحداث من المكونات الأخرى وتنفيذ الإجراءات المناسبة

---

## 🔄 تسلسل العمل

### **عندما يضغط المستخدم على زر الزيادة:**

1. **الضغط على الزر:**
   ```javascript
   @click="increaseQuantity(item)"
   ```

2. **تنفيذ الدالة:**
   ```javascript
   increaseQuantity(item) {
     item.qty = item.qty + 1;           // الكمية تصبح 2
     evntBus.emit("item_updated", item); // إرسال إشارة
   }
   ```

3. **استقبال الإشارة:**
   ```javascript
   evntBus.on("item_updated", (item) => {
     this.debouncedItemOperation("item-updated");
   });
   ```

4. **بدء المؤقت:**
   ```javascript
   debouncedItemOperation() {
     clearTimeout(this._itemOperationTimer);
     this._itemOperationTimer = setTimeout(() => {
       this.sendInvoiceUpdate();
     }, 1000); // انتظار ثانية
   }
   ```

5. **إرسال التحديث:**
   ```javascript
   sendInvoiceUpdate() {
     const doc = this.get_invoice_doc("item-update");
     this.auto_update_invoice(doc, "item-update");
   }
   ```

---

## 🎯 المكونات الرئيسية

| المكون | الوظيفة | مثال |
|--------|---------|------|
| **Template** | عرض الواجهة | الجدول، الأزرار، الحقول |
| **Data** | تخزين البيانات | items, invoice_doc, customer |
| **Methods** | تنفيذ العمليات | increaseQuantity, sendInvoiceUpdate |
| **Events** | التواصل بين المكونات | evntBus.emit, evntBus.on |
| **Timers** | التحكم في التوقيت | setTimeout, clearTimeout |

---

## 🔧 المتغيرات المهمة

```javascript
// بيانات الفاتورة
this.items              // قائمة العناصر
this.invoice_doc        // بيانات الفاتورة من الخادم
this.customer           // بيانات العميل

// مؤقتات التحكم
this._itemOperationTimer // مؤقت التحديث المؤجل
this._autoUpdateTimer   // مؤقت التحديث التلقائي

// إعدادات النظام
this.pos_profile        // إعدادات نقطة البيع
this.float_precision    // دقة الأرقام العشرية
```

---

## 📊 مثال عملي

**المستخدم يضغط على زر الزيادة مرتين بسرعة:**

```
الوقت: 0ms    → الضغطة الأولى  → الكمية تصبح 2
الوقت: 100ms  → الضغطة الثانية → الكمية تصبح 3
الوقت: 1000ms → إرسال التحديث → طلب API واحد للخادم
الوقت: 1200ms → استقبال الرد   → الكمية تبقى 3 ✅
```

**النتيجة:** لا توجد طلبات متعددة، الكمية لا ترجع للخلف!

---

## 🎉 الخلاصة

**الملف منظم في أقسام واضحة:**
- **الواجهة:** Template
- **البيانات:** Data  
- **العمليات:** Methods
- **التواصل:** Events
- **التوقيت:** Timers

**المنطق بسيط:** تحديث فوري في الواجهة + إرسال مؤجل للسيرفر بعد ثانية واحدة.
