# Copyright (c) 2025, abdopcnet and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, getdate
import json


@frappe.whitelist()
def get_offers_for_profile(profile):
    """
    GET - Get all offers for POS Profile
    """
    try:
        pos_profile = frappe.get_doc("POS Profile", profile)
        company = pos_profile.company
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
        # فلتر المستودع: يفحص المخزن إذا كان مطابق، ويتخطى التحقق إذا كان غير محدد في العرض
        if warehouse and warehouse.strip() and warehouse.strip() != "":
            filters["warehouse"] = ["in", ["", warehouse]]
        else:
            # إذا كان المستودع فارغاً، ابحث عن العروض التي لها مستودع فارغ
            filters["warehouse"] = ""
        
        # فلتر التاريخ - إصلاح المنطق
        if date:
            filters["valid_from"] = ["<=", date]
            filters["valid_upto"] = [">=", date]
        
        
        # الحقول الأساسية المطلوبة فقط للواجهة الأمامية - مطابقة لجدول tabPOS Offer
        essential_fields = [
            "name",                    # اسم العرض (مطلوب للتعريف)
            "title",                   # عنوان العرض (مطلوب للعرض)
            "description",             # وصف العرض (مطلوب للعرض)
            "apply_on",                # نوع التطبيق (مطلوب للمنطق)
            "offer",                   # نوع العرض (مطلوب للمنطق)
            "discount_type",           # نوع الخصم (مطلوب للعرض)
            "discount_percentage",     # نسبة الخصم (مطلوب للعرض)
            "discount_amount",         # مبلغ الخصم (مطلوب للعرض)
            "auto",                    # التطبيق التلقائي (مطلوب للمنطق)
            "coupon_based",            # يتطلب كوبون (مطلوب للمنطق)
            "min_qty",                 # الحد الأدنى للكمية (مطلوب للمنطق)
            "max_qty",                 # الحد الأقصى للكمية (مطلوب للمنطق)
            "min_amt",                 # الحد الأدنى للمبلغ (مطلوب للمنطق)
            "max_amt",                 # الحد الأقصى للمبلغ (مطلوب للمنطق)
            "valid_from",              # تاريخ البداية (مطلوب للمنطق)
            "valid_upto",              # تاريخ النهاية (مطلوب للمنطق)
            "replace_item",            # استبدال نفس المنتج (مطلوب للمنطق)
            "replace_cheapest_item"    # استبدال أرخص منتج (مطلوب للمنطق)
        ]
        
        # جلب العروض مع جميع الفلاتر
        data = frappe.get_all(
            "POS Offer",
            filters=filters,
            fields=essential_fields,
            order_by="auto DESC, title ASC"
        )
        
        
        frappe.log_error(f"pos_offer.py(get_offers_for_profile): Found {len(data)} offers", "POS Offer")
        return data
        
    except Exception as e:
        return []


@frappe.whitelist()
def get_offers(profile):
    """
    GET - Get all offers for POS Profile (مطابق للنسخة القديمة)
    """
    try:
        pos_profile = frappe.get_doc("POS Profile", profile)
        company = pos_profile.company
        warehouse = pos_profile.warehouse
        date = nowdate()

        values = {
            "company": company,
            "pos_profile": profile,
            "warehouse": warehouse,
            "valid_from": date,
            "valid_upto": date,
        }
        
        # استخدام SQL مباشر مثل النسخة القديمة
        data = (
            frappe.db.sql(
                """
            SELECT *
            FROM `tabPOS Offer`
            WHERE
            disable = 0 AND
            company = %(company)s AND
            (pos_profile is NULL OR pos_profile = '' OR pos_profile = %(pos_profile)s) AND
            (warehouse is NULL OR warehouse = '' OR warehouse = %(warehouse)s) AND
            (valid_from is NULL OR valid_from = '' OR valid_from <= %(valid_from)s) AND
            (valid_upto is NULL OR valid_upto = '' OR valid_upto >= %(valid_upto)s)
        """,
                values=values,
                as_dict=1,
            )
            or []
        )
        
        frappe.log_error(f"pos_offer.py(get_offers): Found {len(data)} offers", "POS Offer")
        return data
        
    except Exception as e:
        return []


def determine_offer_type(invoice_doc):
    """
    Determine the most appropriate offer type based on invoice data
    """
    try:
        # Check if invoice has items
        if not invoice_doc.items:
            return "unconditional"
        
        # Check for auto offers first
        auto_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "auto": 1},
            fields=["name"]
        )
        
        if auto_offers:
            return "auto"
        
        # Check for manual offers
        manual_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "auto": 0},
            fields=["name"]
        )
        
        if manual_offers:
            return "manual"
        
        # Check for coupon offers
        coupon_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "coupon_based": 1},
            fields=["name"]
        )
        
        if coupon_offers:
            return "coupon"
        
        # Check for give product offers
        give_product_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "offer": "Give Product"},
            fields=["name"]
        )
        
        if give_product_offers:
            return "give_product"
        
        # Check for loyalty offers
        loyalty_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "offer": "Loyalty Point"},
            fields=["name"]
        )
        
        if loyalty_offers:
            return "loyalty"
        
        # Check for percentage offers
        percentage_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "discount_type": "Discount Percentage"},
            fields=["name"]
        )
        
        if percentage_offers:
            return "percentage"
        
        # Check for conditional offers
        conditional_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "min_qty": [">", 0]},
            fields=["name"]
        )
        
        if conditional_offers:
            return "conditional"
        
        return "unconditional"
        
    except Exception as e:
        return "unconditional"
    finally:
        frappe.log_error(f"pos_offer.py(determine_offer_type): Determined {offer_type if 'offer_type' in locals() else 'unconditional'}", "POS Offer")


def get_offers_by_type_handler(offer_type, invoice_name, coupon_code=None):
    """
    Handler function to route to specific offer type functions
    """
    try:
        # Get field mapping for each offer type
        field_mapping = get_offer_fields_mapping()
        fields = field_mapping.get(offer_type, ["*"])
        
        # Get filter mapping for each offer type
        filter_mapping = get_offer_filters_mapping()
        filters = filter_mapping.get(offer_type, {"disable": 0})
        
        # Add coupon filter if needed
        if offer_type == "coupon" and coupon_code:
            filters["title"] = ["like", f"%{coupon_code}%"]
        
        # Get offers from database
        offers = frappe.get_all(
            "POS Offer",
            filters=filters,
            fields=fields
        )
        
        # Check applicability
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        applicable_offers = []
        
        for offer in offers:
            if is_offer_applicable(offer, doc):
                applicable_offers.append(offer)
        
        return {
            "success": True,
            "offers": applicable_offers,
            "count": len(applicable_offers),
            "message": f"تم العثور على {len(applicable_offers)} عرض {offer_type} مناسب"
        }
        
    except Exception as e:
        return {
            "success": False,
            "offers": [],
            "count": 0,
            "error": str(e),
            "message": f"خطأ في معالج نوع العرض: {str(e)}"
        }
    finally:
        frappe.log_error(f"pos_offer.py(get_offers_by_type_handler): Found {len(applicable_offers) if 'applicable_offers' in locals() else 0} offers", "POS Offer")


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
    
    frappe.log_error(f"pos_offer.py(get_offer_fields_mapping): Returned {len(field_mapping)} mappings", "POS Offer")
    
    return field_mapping


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
    
    frappe.log_error(f"pos_offer.py(get_offer_filters_mapping): Returned {len(filter_mapping)} mappings", "POS Offer")
    
    return filter_mapping


def is_offer_applicable(offer, invoice_doc):
    """
    Helper function to check if offer is applicable based on POS Offer fields
    """
    try:
        # Check company (if offer has specific company, it must match)
        if offer.get('company') and offer.company != invoice_doc.company:
            return False
        
        # Check date validity
        if offer.get('valid_from') and getdate(offer.valid_from) > getdate():
            return False
        
        if offer.get('valid_upto') and getdate(offer.valid_upto) < getdate():
            return False
        
        # Check minimum amount (using min_amt field)
        if offer.get('min_amt') and invoice_doc.grand_total < offer.min_amt:
            return False
        
        # Check maximum amount (using max_amt field)
        if offer.get('max_amt') and invoice_doc.grand_total > offer.max_amt:
            return False
        
        # Check minimum quantity (using min_qty field)
        if offer.get('min_qty'):
            total_qty = sum(item.qty for item in invoice_doc.items)
            if total_qty < offer.min_qty:
                return False
        
        # Check maximum quantity (using max_qty field)
        if offer.get('max_qty'):
            total_qty = sum(item.qty for item in invoice_doc.items)
            if total_qty > offer.max_qty:
                return False
        
        # Check apply_on field
        if offer.get('apply_on') == "Item Code" and offer.get('item'):
            # Check specific item
            for item in invoice_doc.items:
                if item.item_code == offer.item:
                    return True
            return False
        
        elif offer.get('apply_on') == "Item Group" and offer.get('item_group'):
            # Check item group
            for item in invoice_doc.items:
                if item.item_group == offer.item_group:
                    return True
            return False
        
        elif offer.get('apply_on') == "Brand" and offer.get('brand'):
            # Check brand
            for item in invoice_doc.items:
                if item.brand == offer.brand:
                    return True
            return False
        
        elif offer.get('apply_on') == "Transaction":
            # Check transaction-level conditions
            return True
        
        # Default: if no specific conditions, offer is applicable
        return True
        
    except Exception as e:
        return False


@frappe.whitelist()
def get_applicable_offers(invoice_name):
    """
    GET - Get all applicable offers for invoice (مطابق للنسخة القديمة مع تحسينات)
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # الحصول على معلومات الملف الشخصي من الفاتورة
        pos_profile = doc.pos_profile if hasattr(doc, 'pos_profile') else None
        if not pos_profile:
            return []
        
        # استخدام دالة get_offers للحصول على العروض المناسبة للملف الشخصي
        all_offers = get_offers(pos_profile)
        
        applicable_offers = []
        
        for offer in all_offers:
            # Check if offer is applicable to this invoice
            if is_offer_applicable(offer, doc):
                applicable_offers.append(offer)
        
        frappe.log_error(f"pos_offer.py(get_applicable_offers): Found {len(applicable_offers)} offers", "POS Offer")
        return applicable_offers
        
    except Exception as e:
        return []


@frappe.whitelist()
def cleanup_duplicate_offers(invoice_name):
    """
    تنظيف العروض المكررة في الفاتورة
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        if not doc.posa_offers:
            return {"message": "لا توجد عروض في هذه الفاتورة"}
        
        # تجميع العروض حسب الاسم
        offers_by_name = {}
        for row in doc.posa_offers:
            if row.offer_name not in offers_by_name:
                offers_by_name[row.offer_name] = []
            offers_by_name[row.offer_name].append(row)
        
        # إزالة العروض المكررة
        removed_count = 0
        for offer_name, rows in offers_by_name.items():
            if len(rows) > 1:
                # الاحتفاظ بالصف الأول فقط
                for row in rows[1:]:
                    doc.remove(row)
                    removed_count += 1
        
        if removed_count > 0:
            doc.save()
            result = {
                "success": True,
                "message": f"تم إزالة {removed_count} عرض مكرر من الفاتورة {invoice_name}",
                "removed_count": removed_count
            }
            frappe.log_error(f"pos_offer.py(cleanup_duplicate_offers): Removed {removed_count} offers", "POS Offer")
            return result
        else:
            result = {
                "success": True,
                "message": "لا توجد عروض مكررة في هذه الفاتورة",
                "removed_count": 0
            }
            frappe.log_error(f"pos_offer.py(cleanup_duplicate_offers): No duplicates found", "POS Offer")
            return result
        
    except Exception as e:
        frappe.log_error(f"pos_offer.py(cleanup_duplicate_offers): Error {str(e)}", "POS Offer")
        return {
            "success": False,
            "error": str(e),
            "message": f"خطأ في تنظيف العروض المكررة: {str(e)}"
        }


@frappe.whitelist()
def debug_offers_for_profile(profile):
    """
    دالة تشخيص لجلب العروض - بدون فلاتر معقدة
    """
    try:
        # جلب جميع العروض بدون فلاتر
        all_offers = frappe.get_all(
            "POS Offer",
            fields=["name", "title", "company", "pos_profile", "warehouse", "valid_from", "valid_upto", "disable"]
        )
        
        # جلب العروض النشطة فقط
        active_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0},
            fields=["name", "title", "company", "pos_profile", "warehouse", "valid_from", "valid_upto"]
        )
        
        # جلب ملف POS
        pos_profile = frappe.get_doc("POS Profile", profile)
        company = pos_profile.company
        warehouse = pos_profile.warehouse
        date = nowdate()
        
        # جلب العروض الخاصة بالشركة
        company_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "company": company},
            fields=["name", "title", "company", "pos_profile", "warehouse", "valid_from", "valid_upto"]
        )
        
        return {
            "total_offers": len(all_offers),
            "active_offers": len(active_offers),
            "company_offers": len(company_offers),
            "profile_info": {
                "name": profile,
                "company": company,
                "warehouse": warehouse,
                "current_date": date
            },
            "all_offers": all_offers,
            "active_offers": active_offers,
            "company_offers": company_offers
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        frappe.log_error(f"pos_offer.py(debug_offers_for_profile): Total {len(all_offers) if 'all_offers' in locals() else 0}, Active {len(active_offers) if 'active_offers' in locals() else 0}", "POS Offer")