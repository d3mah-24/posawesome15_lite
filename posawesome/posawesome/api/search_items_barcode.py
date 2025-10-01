# -*- coding: utf-8 -*-
"""
دالة البحث في باركود الأصناف
Search Items Barcode Function
"""

import json
import frappe
from frappe import _


@frappe.whitelist()
def search_items_barcode(pos_profile, barcode_value):
    """
    البحث المباشر في باركود الأصناف - دالة مكتملة
    """
    pos_profile = json.loads(pos_profile)
    
    try:
        # البحث المباشر في tabItem Barcode مع ربط tabItem و tabItem Price
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
            FROM `tabItem Barcode`
            INNER JOIN `tabItem` ON `tabItem Barcode`.parent = `tabItem`.name
            LEFT JOIN `tabItem Price` ON `tabItem`.name = `tabItem Price`.item_code 
                AND `tabItem Price`.selling = 1 
                AND `tabItem Price`.price_list = %s
                AND (`tabItem Price`.valid_from IS NULL OR `tabItem Price`.valid_from <= CURDATE())
                AND (`tabItem Price`.valid_upto IS NULL OR `tabItem Price`.valid_upto >= CURDATE())
            WHERE `tabItem Barcode`.barcode = %s
                AND `tabItem`.disabled = 0 
                AND `tabItem`.is_sales_item = 1
                AND `tabItem`.is_fixed_asset = 0
            ORDER BY `tabItem Price`.valid_from DESC
            LIMIT 1
            """,
            (pos_profile.get("selling_price_list", ""), barcode_value),
            as_dict=True
        )
        
        if item_data:
            item = item_data[0]
            return item
        else:
            frappe.log_error(f"❌ لم يجد باركود: {barcode_value}", "Items Barcode")
            return {}
            
    except Exception as e:
        frappe.log_error(f"❌ خطأ في البحث بالباركود: {str(e)}", "Items Barcode")
        return {}
