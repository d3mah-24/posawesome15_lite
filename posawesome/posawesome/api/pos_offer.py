# Copyright (c) 2025, abdopcnet and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, getdate
import json

# متغير عام لتجميع التشخيصات
debug_log = []

def log_debug(message):
    """إضافة رسالة للتشخيص العام"""
    debug_log.append(str(message))

def clear_debug_log():
    """مسح التشخيص العام"""
    global debug_log
    debug_log = []

def save_debug_log():
    """حفظ التشخيص العام في سجل واحد"""
    global debug_log
    if debug_log:
        # حفظ في سجل الأخطاء فقط (بدون مسح)
        frappe.log_error(message="\n".join(debug_log), title="POS Offer API - تشخيص شامل")
        # لا نمسح debug_log هنا - نتركه للتجميع


@frappe.whitelist()
def get_offers_for_profile(profile):
    """
    GET - Get all offers for POS Profile
    """
    try:
        log_debug("=== بدء جلب العروض للملف الشخصي ===")
        log_debug(f"Profile: {profile}")
        
        pos_profile = frappe.get_doc("POS Profile", profile)
        company = pos_profile.company
        log_debug(f"Company: {company}")
        warehouse = pos_profile.warehouse
        date = nowdate()

        values = {
            "company": company,
            "pos_profile": profile,
            "warehouse": warehouse,
            "valid_from": date,
            "valid_upto": date,
        }
        
        # استخدام Frappe ORM بدلاً من SQL
        filters = {
            "disable": 0,
            "company": company,
        }
        
        # إضافة فلاتر اختيارية
        if profile:
            filters["pos_profile"] = ["in", ["", profile]]
        if warehouse:
            filters["warehouse"] = ["in", ["", warehouse]]
        if date:
            filters["valid_from"] = ["<=", date]
            filters["valid_upto"] = [">=", date]
        
        data = frappe.get_all(
            "POS Offer",
            filters=filters,
            fields=["*"],
            order_by="auto DESC, title ASC"
        )
        
        log_debug(f"تم جلب {len(data)} عرض")
        log_debug("=== انتهاء جلب العروض للملف الشخصي بنجاح ===")
        
        return data
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب العروض للملف الشخصي: {str(e)}")
        frappe.log_error(f"Error getting offers for profile: {str(e)}")
        return []
    finally:
        # لا نحفظ هنا - نتركه للتجميع في نهاية الملف
        pass


@frappe.whitelist()
def get_offers(invoice_name, offer_type=None, coupon_code=None):
    """
    GET - Main function to get offers based on type
    """
    try:
        log_debug("=== بدء جلب العروض حسب النوع ===")
        log_debug(f"Invoice Name: {invoice_name}")
        log_debug(f"Coupon Code: {coupon_code}")
        
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        log_debug(f"Invoice: {doc.name}, Company: {doc.company}")
        
        # Determine offer type if not provided
        if not offer_type:
            offer_type = determine_offer_type(doc)
            log_debug(f"تم تحديد نوع العرض: {offer_type}")
        
        log_debug(f"Offer Type: {offer_type}")
        
        # Get offers based on type
        result = get_offers_by_type_handler(offer_type, invoice_name, coupon_code)
        
        log_debug(f"تم جلب العروض من نوع: {offer_type}")
        log_debug("=== انتهاء جلب العروض حسب النوع بنجاح ===")
        
        return result
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب العروض حسب النوع: {str(e)}")
        frappe.log_error(f"Error getting offers by type: {str(e)}")
        return {
            "success": False,
            "offers": [],
            "count": 0,
            "error": str(e),
            "message": f"خطأ في جلب العروض حسب النوع: {str(e)}"
        }
    finally:
        # حفظ جميع التشخيصات في نهاية الدالة الرئيسية
        show_all_debug_logs()


def determine_offer_type(invoice_doc):
    """
    Determine the most appropriate offer type based on invoice data
    """
    try:
        log_debug("=== بدء تحديد نوع العرض المناسب ===")
        
        # Check if invoice has items
        if not invoice_doc.items:
            log_debug("لا توجد أصناف في الفاتورة")
            return "unconditional"
        
        # Check for auto offers first
        auto_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "auto": 1},
            fields=["name"]
        )
        
        if auto_offers:
            log_debug("تم العثور على عروض تلقائية")
            return "auto"
        
        # Check for manual offers
        manual_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "auto": 0},
            fields=["name"]
        )
        
        if manual_offers:
            log_debug("تم العثور على عروض يدوية")
            return "manual"
        
        # Check for coupon offers
        coupon_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "coupon_based": 1},
            fields=["name"]
        )
        
        if coupon_offers:
            log_debug("تم العثور على عروض كوبون")
            return "coupon"
        
        # Check for give product offers
        give_product_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "offer": "Give Product"},
            fields=["name"]
        )
        
        if give_product_offers:
            log_debug("تم العثور على عروض إعطاء منتج")
            return "give_product"
        
        # Check for loyalty offers
        loyalty_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "offer": "Loyalty Point"},
            fields=["name"]
        )
        
        if loyalty_offers:
            log_debug("تم العثور على عروض نقاط الولاء")
            return "loyalty"
        
        # Check for percentage offers
        percentage_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "discount_type": "Discount Percentage"},
            fields=["name"]
        )
        
        if percentage_offers:
            log_debug("تم العثور على عروض بنسبة خصم")
            return "percentage"
        
        # Check for conditional offers
        conditional_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "min_qty": [">", 0]},
            fields=["name"]
        )
        
        if conditional_offers:
            log_debug("تم العثور على عروض مشروطة")
            return "conditional"
        
        log_debug("لم يتم العثور على عروض خاصة، استخدام العروض غير المشروطة")
        return "unconditional"
        
    except Exception as e:
        log_debug(f"❌ خطأ في تحديد نوع العرض: {str(e)}")
        return "unconditional"


def get_offers_by_type_handler(offer_type, invoice_name, coupon_code=None):
    """
    Handler function to route to specific offer type functions
    """
    try:
        log_debug(f"توجيه إلى نوع العرض: {offer_type}")
        
        # Get field mapping for each offer type
        field_mapping = get_offer_fields_mapping()
        fields = field_mapping.get(offer_type, ["*"])
        
        # Get filter mapping for each offer type
        filter_mapping = get_offer_filters_mapping()
        filters = filter_mapping.get(offer_type, {"disable": 0})
        
        # Add coupon filter if needed
        if offer_type == "coupon" and coupon_code:
            filters["title"] = ["like", f"%{coupon_code}%"]
        
        log_debug(f"الحقول المطلوبة: {fields}")
        log_debug(f"الفلاتر: {filters}")
        
        # Get offers from database
        offers = frappe.get_all(
            "POS Offer",
            filters=filters,
            fields=fields
        )
        
        log_debug(f"تم جلب {len(offers)} عرض من نوع {offer_type}")
        
        # Check applicability
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        applicable_offers = []
        
        for offer in offers:
            if is_offer_applicable(offer, doc):
                applicable_offers.append(offer)
                log_debug(f"✅ عرض مناسب: {offer.name}")
        
        log_debug(f"تم العثور على {len(applicable_offers)} عرض مناسب")
        
        return {
            "success": True,
            "offers": applicable_offers,
            "count": len(applicable_offers),
            "message": f"تم العثور على {len(applicable_offers)} عرض {offer_type} مناسب"
        }
        
    except Exception as e:
        log_debug(f"❌ خطأ في معالج نوع العرض: {str(e)}")
        return {
            "success": False,
            "offers": [],
            "count": 0,
            "error": str(e),
            "message": f"خطأ في معالج نوع العرض: {str(e)}"
        }


def get_offer_fields_mapping():
    """
    Get field mapping for each offer type
    """
    return {
        "auto": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_type", "discount_percentage", "auto"],
        "manual": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_type", "discount_percentage", "auto"],
        "coupon": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_type", "discount_percentage", "coupon_based"],
        "give_product": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "given_qty", "apply_item_code", "apply_item_group"],
        "loyalty": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "loyalty_program", "loyalty_points"],
        "rate": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "rate", "less_then"],
        "percentage": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_percentage"],
        "amount": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_amount"],
        "conditional": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "min_qty", "max_qty", "min_amt", "max_amt"],
        "unconditional": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_type", "discount_percentage", "discount_amount", "rate"]
    }


def get_offer_filters_mapping():
    """
    Get filter mapping for each offer type
    """
    return {
        "auto": {"disable": 0, "auto": 1},
        "manual": {"disable": 0, "auto": 0},
        "coupon": {"disable": 0, "coupon_based": 1},
        "give_product": {"disable": 0, "offer": "Give Product"},
        "loyalty": {"disable": 0, "offer": "Loyalty Point"},
        "rate": {"disable": 0, "discount_type": "Rate"},
        "percentage": {"disable": 0, "discount_type": "Discount Percentage"},
        "amount": {"disable": 0, "discount_type": "Discount Amount"},
        "conditional": {"disable": 0, "min_qty": [">", 0]},
        "unconditional": {"disable": 0, "min_qty": 0, "max_qty": 0, "min_amt": 0, "max_amt": 0}
    }


def is_offer_applicable(offer, invoice_doc):
    """
    Helper function to check if offer is applicable based on POS Offer fields
    """
    try:
        log_debug(f"فحص صحة العرض: {offer.title}")
        
        # Check company (if offer has specific company, it must match)
        if offer.company and offer.company != invoice_doc.company:
            log_debug(f"❌ الشركة غير متطابقة: {offer.company} != {invoice_doc.company}")
            return False
        elif not offer.company:
            log_debug(f"✅ العرض ينطبق على جميع الشركات")
        
        # Check date validity
        if offer.valid_from and getdate(offer.valid_from) > getdate():
            log_debug(f"❌ العرض لم يبدأ بعد: {offer.valid_from}")
            return False
        
        if offer.valid_upto and getdate(offer.valid_upto) < getdate():
            log_debug(f"❌ العرض انتهى: {offer.valid_upto}")
            return False
        
        # Check minimum amount (using min_amt field)
        if offer.min_amt and invoice_doc.grand_total < offer.min_amt:
            log_debug(f"❌ المبلغ أقل من الحد الأدنى: {invoice_doc.grand_total} < {offer.min_amt}")
            return False
        
        # Check maximum amount (using max_amt field)
        if offer.max_amt and invoice_doc.grand_total > offer.max_amt:
            log_debug(f"❌ المبلغ أكبر من الحد الأقصى: {invoice_doc.grand_total} > {offer.max_amt}")
            return False
        
        # Check apply_on field
        if offer.apply_on == "Item Code" and offer.item:
            # Check specific item
            for item in invoice_doc.items:
                if item.item_code == offer.item:
                    log_debug(f"✅ العرض مناسب للصنف: {item.item_code}")
                    return True
            log_debug(f"❌ الصنف غير موجود: {offer.item}")
            return False
        
        elif offer.apply_on == "Item Group" and offer.item_group:
            # Check item group
            for item in invoice_doc.items:
                if item.item_group == offer.item_group:
                    log_debug(f"✅ العرض مناسب لمجموعة الصنف: {item.item_group}")
                    return True
            log_debug(f"❌ مجموعة الصنف غير موجودة: {offer.item_group}")
            return False
        
        elif offer.apply_on == "Brand" and offer.brand:
            # Check brand
            for item in invoice_doc.items:
                if item.brand == offer.brand:
                    log_debug(f"✅ العرض مناسب للماركة: {item.brand}")
                    return True
            log_debug(f"❌ الماركة غير موجودة: {offer.brand}")
            return False
        
        elif offer.apply_on == "Transaction":
            # Check transaction-level conditions
            log_debug("✅ العرض مناسب للمعاملة")
            return True
        
        # Check minimum quantity (using min_qty field)
        if offer.min_qty:
            total_qty = sum(item.qty for item in invoice_doc.items)
            if total_qty < offer.min_qty:
                log_debug(f"❌ الكمية أقل من الحد الأدنى: {total_qty} < {offer.min_qty}")
                return False
        
        # Check maximum quantity (using max_qty field)
        if offer.max_qty:
            total_qty = sum(item.qty for item in invoice_doc.items)
            if total_qty > offer.max_qty:
                log_debug(f"❌ الكمية أكبر من الحد الأقصى: {total_qty} > {offer.max_qty}")
                return False
        
        log_debug("✅ العرض مناسب")
        return True
        
    except Exception as e:
        log_debug(f"❌ خطأ في فحص صحة العرض: {str(e)}")
        frappe.log_error(f"Error checking offer applicability: {str(e)}")
        return False


@frappe.whitelist()
def get_applicable_offers(invoice_name):
    """
    GET - Get all applicable offers for invoice (legacy function for compatibility)
    """
    try:
        log_debug("=== بدء جلب جميع العروض المناسبة ===")
        log_debug(f"Invoice Name: {invoice_name}")
        
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        log_debug(f"Invoice: {doc.name}, Company: {doc.company}")
        
        # Get all active offers
        offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0},
            fields=["*"]
        )
        
        log_debug(f"تم جلب {len(offers)} عرض نشط")
        
        applicable_offers = []
        
        for offer in offers:
            # Check if offer is applicable to this invoice
            if is_offer_applicable(offer, doc):
                applicable_offers.append(offer)
                log_debug(f"✅ عرض مناسب: {offer.name}")
        
        log_debug(f"تم العثور على {len(applicable_offers)} عرض مناسب")
        log_debug("=== انتهاء جلب جميع العروض المناسبة بنجاح ===")
        
        return applicable_offers
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب جميع العروض المناسبة: {str(e)}")
        frappe.log_error(f"Error getting applicable offers: {str(e)}")
        return []
    finally:
        # لا نحفظ هنا - نتركه للتجميع في نهاية الملف
        pass


# دالة لحفظ جميع التشخيصات في Error Log
def show_all_debug_logs():
    """حفظ جميع التشخيصات المجمعة في Error Log"""
    global debug_log
    if debug_log:
        frappe.log_error(message="\n".join(debug_log), title="POS Offer API - تشخيص شامل")
        clear_debug_log()


# يمكن استدعاء show_all_debug_logs() عند الحاجة لحفظ جميع التشخيصات