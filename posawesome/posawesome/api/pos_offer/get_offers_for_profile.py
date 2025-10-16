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
        
        return data
        
    except Exception as e:
        return []
