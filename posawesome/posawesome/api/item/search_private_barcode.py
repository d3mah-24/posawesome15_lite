# -*- coding: utf-8 -*-
"""
Search Private Barcode Function
Handles searching private barcode
"""

from __future__ import unicode_literals

import json
import frappe


@frappe.whitelist()
def search_private_barcode(pos_profile, barcode_value):
    """
    POST - Search private barcode
    """
    pos_profile = json.loads(pos_profile)
    
    try:
        # Search in custom barcode table (if exists)
        # This is a placeholder for custom barcode implementation
        
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
            WHERE `tabItem`.name = %s
                AND `tabItem`.disabled = 0 
                AND `tabItem`.is_sales_item = 1
                AND `tabItem`.is_fixed_asset = 0
                AND `tabItem`.has_variants = 0
            LIMIT 1
            """,
            (pos_profile.get("selling_price_list", ""), barcode_value),
            as_dict=True
        )
        
        if item_data:
            item = item_data[0]
            return item
        else:
            return {}
            
    except Exception as e:
        return {}
