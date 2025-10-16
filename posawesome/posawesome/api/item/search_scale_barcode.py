# -*- coding: utf-8 -*-
"""
Search Scale Barcode Function
Handles searching scale barcode
"""

from __future__ import unicode_literals

import json
import frappe


@frappe.whitelist()
def search_scale_barcode(pos_profile, barcode_value):
    """
    POST - Search scale barcode
    """
    pos_profile = json.loads(pos_profile)
    
    try:
        # Search for scale barcode pattern (weight-based pricing)
        # Scale barcodes typically have format: ITEM_CODE + WEIGHT
        # This is a simplified implementation
        
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
            WHERE `tabItem`.name LIKE %s
                AND `tabItem`.disabled = 0 
                AND `tabItem`.is_sales_item = 1
                AND `tabItem`.is_fixed_asset = 0
            LIMIT 1
            """,
            (pos_profile.get("selling_price_list", ""), f"{barcode_value[:6]}%"),
            as_dict=True
        )
        
        if item_data:
            item = item_data[0]
            # Extract weight from barcode (simplified)
            weight = float(barcode_value[6:]) / 1000  # Convert to kg
            item["qty"] = weight
            return item
        else:
            return {}
            
    except Exception as e:
        return {}
