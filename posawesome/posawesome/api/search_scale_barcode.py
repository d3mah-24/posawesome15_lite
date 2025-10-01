# -*- coding: utf-8 -*-
"""
دالة البحث في باركود الميزان
Search Scale Barcode Function
"""

import json
import frappe
from frappe import _


@frappe.whitelist()
def search_scale_barcode(pos_profile, barcode_value):
    """
    البحث في باركود الميزان - دالة مبسطة
    """
    pos_profile = json.loads(pos_profile)
    
    try:
        # استخراج البيانات بناءً على الحقول المدخلة
        item_code_start = len(str(pos_profile.get("posa_scale_barcode_start")))      # طول البادئة
        item_code_length = int(pos_profile.get("posa_scale_item_code_length"))       # طول كود الصنف
        weight_length = int(pos_profile.get("posa_weight_length"))                    # طول الوزن
        
        item_code_part = barcode_value[item_code_start:item_code_start + item_code_length]
        weight_part = barcode_value[item_code_start + item_code_length:item_code_start + item_code_length + weight_length]
        
        # حساب الوزن
        weight = float(weight_part) / 1000  # تحويل من جرام إلى كيلو
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
                %s as qty
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
            (weight, pos_profile.get("selling_price_list", ""), item_code_part),
            as_dict=True
        )
        
        if item_data:
            item = item_data[0]
            return item
        else:
            frappe.log_error(f"❌ لم يجد باركود الميزان: {item_code_part}", "Scale Barcode")
            return {}
            
    except Exception as e:
        frappe.log_error(f"❌ خطأ في البحث بالباركود: {str(e)}", "Scale Barcode")
        return {}
