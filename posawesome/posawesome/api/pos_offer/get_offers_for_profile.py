# -*- coding: utf-8 -*-
"""
Get Offers for Profile Function
Handles getting offers for POS Profile
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import nowdate


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

        # الحقول الأساسية المطلوبة فقط للواجهة الأمامية - مطابقة لجدول POS Offer الفعلي
        essential_fields = [
            "name",                    # اسم العرض (مطلوب للتعريف)
            "title",                   # عنوان العرض (مطلوب للعرض)
            "description",             # وصف العرض (مطلوب للعرض)
            "offer_type",              # نوع العرض (مطابق للدكتايب الفعلي)
            "discount_type",           # نوع الخصم (مطلوب للعرض)
            "discount_percentage",     # نسبة الخصم (مطلوب للعرض)
            "auto",                    # التطبيق التلقائي (مطلوب للمنطق)
            "min_qty",                 # الحد الأدنى للكمية (مطلوب للمنطق)
            "max_qty",                 # الحد الأقصى للكمية (مطلوب للمنطق)
            "min_amt",                 # الحد الأدنى للمبلغ (مطلوب للمنطق)
            "max_amt",                 # الحد الأقصى للمبلغ (مطلوب للمنطق)
            "valid_from",              # تاريخ البداية (مطلوب للمنطق)
            "valid_upto",              # تاريخ النهاية (مطلوب للمنطق)
            "item_code",               # كود المنتج (مطلوب للمنطق)
            "item_group",              # مجموعة المنتج (مطلوب للمنطق)
            "brand",                   # العلامة التجارية (مطلوب للمنطق)
            "customer",                # العميل (مطلوب للمنطق)
            "customer_group"          # مجموعة العميل (مطلوب للمنطق)
        ]

        # جلب العروض مع جميع الفلاتر
        data = frappe.get_all(
            "POS Offer",
            filters=filters,
            fields=essential_fields,
            order_by="auto DESC, title ASC"
        )

        return data

    except Exception as e:
        frappe.log_error(f"Error in get_offers_for_profile: {str(e)}", "POS Offers Error")
        return []
