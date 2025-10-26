import { createApp } from 'vue';
import Home from './Home.vue';

// Define Vue 3 feature flags for better tree-shaking and performance
// See: https://link.vuejs.org/feature-flags
if (typeof window !== 'undefined') {
    window.__VUE_OPTIONS_API__ = true;
    window.__VUE_PROD_DEVTOOLS__ = false;
    window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false;
}

// Translation maps for different languages
const TRANSLATIONS = {
  ar: {
    // From your example plus extracted text
    "POS Awesome": "نقاط البيع المميزة",
    "Menu": "قائمة",
    "List": "قائمة",
    "Images": "صور",
    "Offers": "العروض",
    "Applied": "مطبق",
    "Qty": "الكمية",
    "Close Shift": "غلق الوردية",
    "Print Last Receipt": "طباعة اخر فاتورة",
    "Logout": "خروج من النظام",
    "About": "عن",
    "Invoices": "الفواتير",
    "Payments": "المدفوعات",
    "UnAllocated Payments": "المدفوعات غير المخصصة",
    "Search MPESA Payments": "بحث عن مدفوعات موبايل",
    "Search": "بحث",
    "Submit": "تسجيل",
    "Select Shift": "اختار الوردية",
    "Outstanding Amounts": "إجمالي المبالغ المستحقة",
    "Selected Total :": "إجمالي المحدد :",
    "Total Outstanding Amounts": "إجمالي المبالغ المستحقة",
    "Total Selected :": "إجمالي المحدد :",
    "Unallocated Payments": "المدفوعات غير المخصصة",
    "Search for Mobile Payments": "بحث عن مدفوعات موبايل",
    "Remaining Amount": "المبلغ المتبقي",
    "Change Amount": "المبلغ المرتجع",
    "Get": "الحصول على",
    "Request": "طلب",
    "Pay from Customer Points": "دفع من نقاط العميل",
    "Customer Points Balance": "رصيد نقاط العميل",
    "Customer Credit Redeemed": "رصيد العميل المسترد",
    "Cash Credit Balance": "رصيد ائتماني نقدي",
    "Net Total (Without Tax)": "الصافي بدون ضريبة",
    "Tax": "الضريبة",
    "Total Before Discount": "الإجمالي قبل الخصم",
    "Total Discount": "إجمالي الخصم",
    "Invoice Total": "إجمالي الفاتورة",
    "Rounded Total": "الإجمالي المقرب",
    "Purchase Order Number": "رقم طلب الشراء",
    "Purchase Order Date": "تاريخ طلب الشراء",
    "Is Write Off Amount?": "هل مبلغ مشطوب",
    "Is Credit Sale?": "هل بيع بالاجل",
    "Is Cash Return?": "هل هو استرداد نقدي؟",
    "Due Date": "تاريخ الاستحقاق",
    "Use Customer Credit": "استخدام رصيد العميل",
    "Available Credit": "الرصيد المتاح",
    "Credit to Redeem": "استرداد الرصيد",
    "Sales Person": "مندوب البيع",
    "Sales Person not found": "مندوب البيع غير موجود",
    "Payment Number": "رقم الدفع",
    "Full Name": "الاسم الكامل",
    "Phone Number": "رقم الهاتف",
    "Please select a customer": "برجاء اختيار عميل",
    "Please make a payment or select a payment": "برجاء إجراء دفعة أو اختيار دفعة",
    "Please select an invoice": "برجاء اختيار فاتورة",
    "Processing payment": "جاري معالجة الدفع",
    "Item Name": "اسم الصنف",
    "Code": "الرمز",
    "Price": "السعر",
    "Available Quantity": "الكمية المتاحة",
    "Unit of Measure": "وحدة القياس",
    "Unit": "الوحدة",
    "Discount": "خصم",
    "Another offer currently applied": "عرض آخر مطبق حالياً",
    "Company": "الشركة",
    "POS Profile": "ملف نقاط البيع",
    "Edit Price": "تعديل السعر",
    "Mode of Payment": "طريقة الدفع",
    "Opening Amount": "المبلغ الافتتاحي",
    "Close Cashier Shift": "اغلاق وردية الكاشير",
    "Edit Amount": "تعديل المبلغ",
    "Close": "إغلاق",
    "Expected Total": "الإجمالي المتوقع",
    "Closing Total": "اجمالي الاغلاق",
    "Add New Address": "إضافة عنوان جديد",
    "Address": "العنوان",
    "Address Line 1": "عنوان السطر 1",
    "Address Line 2": "عنوان السطر 2",
    "City": "المدينة",
    "State": "الولاية",
    "Quantity": "الكمية",
    "Item Group": "مجموعة الصنف",
    "Coupons": "الكوبونات",
    "Shipping Cost": "تكلفة النقل",
    "No shipping costs available": "لا توجد تكاليف نقل متاحة",
    "Shipping Cost Price": "سعر تكلفة النقل",
    "Document Date": "تاريخ المستند",
    "Item Code": "كود الصنف",
    "UOM": "الوحدة",
    "Rate": "السعر",
    "Discount Percentage": "نسبة الخصم",
    "Discount Amount": "قيمة الخصم",
    "Price List Rate": "السعر الثابت",
    "Available Qty": "الرصيد المتاح",
    "Stock Qty": "رصيد المخزن",
    "Stock UOM": "وحدة المخزن",
    "Promotional Scheme Applied": "تم تطبيق عرض",
    "Serial No Qty": "عدد السيريال",
    "Serial No": "رقم السيريال",
    "Batch No.Available Qty": "رقم الباتش.الكمية المتاحة",
    "Batch Expiry": "إنتهاء صلاحية الباتش",
    "Batch No": "رقم الباتش",
    "Additional Notes": "ملاحظات إضافية",
    "Total Qty": "إجمالي الكمية",
    "Additional Discount": "الخصم علي الفاتورة",
    "Apply Additional Discount": "خصم علي الفاتورة",
    "Items Discount": "خصم الأصناف",
    "Please select customer": "برجاء اختيار عميل",
    "Please make payment or select payments": "برجاء إجراء دفعة أو اختيار دفعة",
    "Please select invoice": "برجاء اختيار فاتورة",
    "Processing Payment": "جاري معالجة الدفع",
    "Name": "اسم",
    "Apply On": "تطبيق على",
    "Offer": "عرض",
    "Add": "إضافة",
    "Coupon": "كوبون",
    "Type": "النوع",
    "POS Offer": "عرض نقاط البيع",
    "Update Customer": "تحديث العميل",
    "New Customer": "تسجيل عميل جديد",
    "Customer Name": "إسم العميل",
    "Tax ID": "رقم التعريف الضريبي",
    "Email": "البريد الإلكتروني",
    "Gender": "الجنس",
    "Referral Code": "رمز الإحالة",
    "Date of Birth": "تاريخ الميلاد",
    "Customer Group": "مجموعة العميل",
    "Group not found": "المجموعة غير موجودة",
    "Territory": "المنطقة",
    "Territory not found": "المنطقة غير موجودة",
    "Loyalty Program": "برنامج الولاء",
    "Loyalty Points": "نقاط الولاء",
    "Register Customer": "تسجيل العميل",
    "Customer name is required.": "اسم العميل مطلوب.",
    "Customer group name is required.": "اسم مجموعة العميل مطلوب.",
    "Customer territory name is required.": "اسم منطقة العميل مطلوب.",
    "Customer created successfully.": "تم إنشاء العميل بنجاح.",
    "Customer updated successfully.": "تم تحديث العميل بنجاح.",
    "Failed to create customer.": "فشل إنشاء العميل.",
    "Cancel current invoice?": "إالغاء الفاتورة الحالية ?",
    "Cancel Invoice": "إالغاء الفاتورة",
    "Back": "رجوع",
    "Amount": "القيمة",
    "Return": "مرتجع فاتورة",
    "Drafts": "الفواتير المحفوظه",
    "Cancel": "إلغاء",
    "Save as Draft": "حفظ وانشاء جديد",
    "Pay": "دفع",
    "Print Draft": "طباعة المسودة",
    "Total": "الإجمالي",
    "This serial number {0} is already added!": "رقم السيريال هذا {0} قد تم إضافته بالفعل!",
    "No items found!": "لا توجد عناصر!",
    "Discount percentage for item '{0}' cannot exceed {1}%": "نسبة الخصم للصنف '{0}' لايمكن ان تجاوز {1}%",
    "Available quantity '{0}' for item '{1}' is insufficient": "الكمية الموجوده هذه '{0}' للصنف '{1}' غير كافية",
    "Quantity for item '{0}' cannot be zero (0)": "الكمية للصنف '{0}' لا يمكن أن تكون صفر (0)",
    "Allowed discount for item {0} {1}": "الخصم المسموح للصنف {0} {1}",
    "Serial numbers selected for item {0} are invalid": "الأرقام التسلسلية المحددة للصنف {0} غير صحيحة",
    "Discount percentage cannot be higher than {0}%": "لا يمكن أن تكون نسبة الخصم أعلى من {0}%",
    "Return invoice total is invalid": "مجموع فاتورة الإرجاع غير صحيح",
    "Return invoice total should not be higher than {0}": "مجموع فاتورة الإرجاع لا يجب أن يكون أعلى من {0}",
    "Quantity for item {0} cannot be greater than {1}": "الكمية للصنف {0} لا يمكن أن تكون أكبر من {1}",
    "You are not allowed to print pending invoices": "لا يُسمح لك بطباعة الفواتير المعلقة",
    "Loyalty points offer applied": "تم تطبيق عرض نقاط الولاء",
    // Additional text from Invoice.vue (excluding duplicates)
    "inv_disc%": "خصم الفاتورة %",
    "items_dis": "خصم الأصناف",
    "before_disc": "قبل الخصم",
    "net_total": "الصافي",
    "grand_total": "الإجمالي الكلي",
    "Print": "طباعة",
    "Quick Return": "مرتجع سريع",
    "Scan Barcode": "مسح الباركود",
    "Search Item": "بحث عن الصنف",
    "Clear Cache": "مسح الذاكرة المؤقتة",
    "About System": "حول النظام",
    "No last receipt": "لا يوجد اخر فاتورة"
  },
  es: {
    "POS Awesome": "POS Awesome",
    "Menu": "Menú",
    "Close Shift": "Cerrar Turno",
    "Logout": "Cerrar sesión"
  },
  pt: {
    "POS Awesome": "POS Awesome",
    "Menu": "Menu",
    "Close Shift": "Fechar Turno",
    "Logout": "Sair"
  }
};

// Function to apply translations based on language
function applyTranslations(language) {
  if (!language || language === 'en') return; // English is default
  
  const translations = TRANSLATIONS[language];
  if (translations) {
    window.__messages = window.__messages || {};
    $.extend(window.__messages, translations);
  }
}

// Listen for POS Profile load event to apply translations
if (typeof window !== 'undefined') {
  window.addEventListener('posProfileLoaded', function(e) {
    const posProfile = e.detail.pos_profile;
    if (posProfile && posProfile.posa_language) {
      applyTranslations(posProfile.posa_language);
    }
  });
}

// Define SetVueGlobals function to set up Vue global properties
function SetVueGlobals(app) {
    // Set up global properties that components might need
    app.config.globalProperties.$frappe = frappe;
    app.config.globalProperties.$__ = __; // Frappe's translation function
    
    // Make common Frappe utilities available globally
    if (typeof frappe !== 'undefined') {
        app.config.globalProperties.$call = frappe.call;
        app.config.globalProperties.$format = frappe.format;
        app.config.globalProperties.$db = frappe.db;
    }
}

frappe.provide('frappe.PosApp');

frappe.PosApp.posapp = class {
    constructor({ parent }) {
        this.$parent = $(document);
        this.page = parent.page;
        this.make_body();
    }

    make_body() {
        this.$el = this.$parent.find('.main-section');

        const app = createApp(Home);

        SetVueGlobals(app);
        app.mount(this.$el[0]);
    }

    setup_header() {
        // Implement header setup logic here
    }
};