# -*- coding: utf-8 -*-
"""
POS Offers - Simple & Clean
One file for all offer operations
"""

from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, flt


@frappe.whitelist()
def get_offers(profile):
    """
    جلب كل العروض المناسبة للـ POS Profile

    Args:
        profile: اسم POS Profile

    Returns:
        list: قائمة العروض
    """
    try:
        pos_profile = frappe.get_doc("POS Profile", profile)
        company = pos_profile.company
        warehouse = pos_profile.warehouse
        date = nowdate()

        # SQL بسيط - يتعامل مع NULL بشكل صحيح
        data = frappe.db.sql("""
            SELECT *
            FROM `tabPOS Offer`
            WHERE
                disable = 0
                AND company = %(company)s
                AND (pos_profile IS NULL OR pos_profile = '' OR pos_profile = %(profile)s)
                AND (warehouse IS NULL OR warehouse = '' OR warehouse = %(warehouse)s)
                AND (valid_from IS NULL OR valid_from = '' OR valid_from <= %(date)s)
                AND (valid_upto IS NULL OR valid_upto = '' OR valid_upto >= %(date)s)
            ORDER BY auto DESC, discount_percentage DESC, title ASC
        """, {
            "company": company,
            "profile": profile,
            "warehouse": warehouse,
            "date": date
        }, as_dict=1)

        return data or []

    except Exception as e:
        frappe.log_error(f"Error in get_offers: {str(e)}", "POS Offers Error")
        return []


@frappe.whitelist()
def get_applicable_offers(invoice_name):
    """
    جلب العروض المطبقة على فاتورة محددة

    Args:
        invoice_name: اسم الفاتورة

    Returns:
        list: قائمة العروض المطبقة
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)

        if not doc.pos_profile:
            return []

        # جلب كل العروض
        all_offers = get_offers(doc.pos_profile)

        # فحص كل عرض
        applicable = []
        for offer in all_offers:
            if is_offer_applicable(offer, doc):
                applicable.append(offer)

        return applicable

    except Exception as e:
        frappe.log_error(f"Error in get_applicable_offers: {str(e)}", "POS Offers Error")
        return []


def is_offer_applicable(offer, invoice):
    """
    فحص هل العرض ينطبق على الفاتورة

    Args:
        offer: dict - بيانات العرض
        invoice: doc - فاتورة Sales Invoice

    Returns:
        bool: True إذا كان العرض ينطبق
    """
    try:
        # فحص الكمية
        if offer.get('min_qty'):
            total_qty = sum(flt(item.qty) for item in invoice.items)
            if total_qty < flt(offer.min_qty):
                return False

        if offer.get('max_qty'):
            total_qty = sum(flt(item.qty) for item in invoice.items)
            if total_qty > flt(offer.max_qty):
                return False

        # فحص المبلغ
        if offer.get('min_amt'):
            if flt(invoice.grand_total) < flt(offer.min_amt):
                return False

        if offer.get('max_amt'):
            if flt(invoice.grand_total) > flt(offer.max_amt):
                return False

        # فحص نوع العرض
        offer_type = offer.get('offer_type')

        if not offer_type or offer_type == "":
            # عرض عام - ينطبق على الكل
            return True

        if offer_type == "grand_total":
            # عرض على الإجمالي - تم الفحص بالأعلى
            return True

        if offer_type == "item_code":
            # عرض على منتج محدد
            if not offer.get('item_code'):
                return False
            for item in invoice.items:
                if item.item_code == offer.item_code:
                    return True
            return False

        if offer_type == "item_group":
            # عرض على مجموعة منتجات
            if not offer.get('item_group'):
                return False
            for item in invoice.items:
                if item.item_group == offer.item_group:
                    return True
            return False

        if offer_type == "brand":
            # عرض على براند محدد
            if not offer.get('brand'):
                return False
            for item in invoice.items:
                if hasattr(item, 'brand') and item.brand == offer.brand:
                    return True
            return False

        if offer_type == "customer":
            # عرض على عميل محدد
            if not offer.get('customer'):
                return False
            return offer.customer == invoice.customer

        if offer_type == "customer_group":
            # عرض على مجموعة عملاء
            if not offer.get('customer_group'):
                return False
            try:
                customer_doc = frappe.get_doc("Customer", invoice.customer)
                return customer_doc.customer_group == offer.customer_group
            except:
                return False

        return False

    except Exception as e:
        frappe.log_error(f"Error in is_offer_applicable: {str(e)}", "POS Offers Error")
        return False


def apply_offer_to_invoice(doc, offer):
    """
    تطبيق عرض على الفاتورة وتسجيله في posa_offers

    Args:
        doc: Sales Invoice document
        offer: dict - بيانات العرض

    Returns:
        bool: True إذا تم التطبيق بنجاح
    """
    try:
        # تطبيق الخصم على الفاتورة
        if offer.get("discount_percentage"):
            doc.additional_discount_percentage = flt(offer.get("discount_percentage"))

        # تسجيل العرض في child table
        doc.append("posa_offers", {
            "offer_name": offer.get("name"),
            "offer_type": offer.get("offer_type"),
            "discount_percentage": offer.get("discount_percentage"),
            "row_id": ""  # فارغ للعروض على grand_total، يمكن استخدامه لربط العرض بمنتج معين
        })

        frappe.log_error(f"[DEBUG] Applied offer {offer.get('name')} to invoice", "POS Offers Debug")
        return True

    except Exception as e:
        frappe.log_error(f"Error applying offer to invoice: {str(e)}", "POS Offers Error")
        return False


