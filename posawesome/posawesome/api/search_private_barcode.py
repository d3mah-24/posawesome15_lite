# -*- coding: utf-8 -*-
"""
دالة البحث في الباركود الخاص
Search Private Barcode Function
"""

import json
import frappe
from frappe import _


@frappe.whitelist()
def search_private_barcode(pos_profile, barcode_value):
    """
    البحث في الباركود الخاص - دالة مبسطة
    """
    pos_profile = json.loads(pos_profile)
    
    try:
        # فحص الحقول المطلوبة
        if not pos_profile.get("posa_private_barcode_prefixes"):
            frappe.log_error(f"❌ حقل posa_private_barcode_prefixes مفقود", "Private Barcode")
            return {}
        
        if not pos_profile.get("posa_private_item_code_length"):
            frappe.log_error(f"❌ حقل posa_private_item_code_length مفقود", "Private Barcode")
            return {}
        
        # استخراج كود الصنف من الباركود الخاص بناءً على الحقول المدخلة
        # الواجهة تضمن أن الباركود يبدأ بأحد البادئات المحددة
        prefixes = pos_profile.get("posa_private_barcode_prefixes", "").split(',')
        prefixes = [p.strip() for p in prefixes if p.strip()]
        
        # العثور على البادئة المستخدمة
        used_prefix = next((prefix for prefix in prefixes if barcode_value.startswith(prefix)), None)
        
        # استخراج كود الصنف بناءً على طول البادئة
        item_code_start = len(used_prefix)
        item_code_length = int(pos_profile.get("posa_private_item_code_length"))
        
        item_code = barcode_value[item_code_start:item_code_start + item_code_length]
        
        # البحث المباشر في tabItem مع ربط tabItem Price
        item_data = frappe.db.sql(
            """
            SELECT 
                `tabItem`.name as item_code,
                `tabItem`.item_name,
                `tabItem`.stock_uom as uom,
                `tabItem`.has_batch_no,
                `tabItem`.has_serial_no,
                `tabItem Price`.price_list_rate as rate,
                `tabItem Price`.currency,
                1 as qty
            FROM `tabItem`
            LEFT JOIN `tabItem Price` ON `tabItem`.name = `tabItem Price`.item_code 
                AND `tabItem Price`.selling = 1 
                AND `tabItem Price`.price_list = %s
                AND (`tabItem Price`.valid_from IS NULL OR `tabItem Price`.valid_from <= CURDATE())
                AND (`tabItem Price`.valid_upto IS NULL OR `tabItem Price`.valid_upto >= CURDATE())
            WHERE `tabItem`.name = %s
                AND `tabItem`.disabled = 0 
                AND `tabItem`.is_sales_item = 1
                AND `tabItem`.is_fixed_asset = 0
            ORDER BY `tabItem Price`.valid_from DESC
            LIMIT 1
            """,
            (pos_profile.get("selling_price_list", ""), item_code),
            as_dict=True
        )
        
        if item_data:
            item = item_data[0]
            return item
        else:
            frappe.log_error(f"❌ لم يجد باركود خاص: {item_code}", "Private Barcode")
            return {}
            
    except Exception as e:
        frappe.log_error(f"❌ خطأ في البحث بالباركود الخاص: {str(e)}", "Private Barcode")
        return {}