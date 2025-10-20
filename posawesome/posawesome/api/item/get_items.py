# -*- coding: utf-8 -*-
"""
Get Items Function
Handles getting items for POS
"""

from __future__ import unicode_literals

import json
import frappe


@frappe.whitelist()
def get_items(pos_profile, price_list=None, item_group="", search_value="", customer=None):
    """
    GET - Get items for POS
    Returns items with prices and stock qty in a single optimized query
    
    Frontend expects (ItemsSelector.vue):
    - item_code, item_name, stock_uom, item_group
    - rate, price_list_rate, base_rate, currency
    - actual_qty (stock quantity from warehouse)
    
    Frontend calls:
    1. get_items() - line 461 (initial load)
    2. performLiveSearch() - line 702 (live search with 200ms debounce)
    3. _performItemSearch() - line 746 (manual search)
    4. update_items_details() - line 824 (refresh item details)
    5. search_barcode_from_server() - line 898 (barcode search)
    
    Uses JOIN to avoid N+1 query problem (1 query instead of 51)
    """
    try:
        pos_profile = json.loads(pos_profile)
        
        if not price_list:
            price_list = pos_profile.get("selling_price_list")
        
        # Get warehouse from POS Profile
        warehouse = pos_profile.get("warehouse", "")
        
        # Build WHERE conditions dynamically
        where_conditions = [
            "`tabItem`.disabled = 0",
            "`tabItem`.is_sales_item = 1",
            "`tabItem`.has_variants = 0"
        ]
        
        # Build parameters dictionary
        params = {
            "price_list": price_list,
            "warehouse": warehouse
        }
        
        # Add item_group filter if provided (case-insensitive)
        if item_group and item_group.strip():
            where_conditions.append("`tabItem`.item_group LIKE %(item_group)s")
            params["item_group"] = f"%{item_group}%"
        
        # Add search filter (item_code OR item_name)
        if search_value:
            where_conditions.append("(`tabItem`.name LIKE %(search)s OR `tabItem`.item_name LIKE %(search)s)")
            params["search"] = f"%{search_value}%"
        
        where_clause = " AND ".join(where_conditions)
        
        # Single optimized query with JOINs for price and stock
        items = frappe.db.sql(
            f"""
            SELECT 
                `tabItem`.name as item_code,
                `tabItem`.item_name,
                `tabItem`.item_group,
                `tabItem`.stock_uom,
                `tabItem Price`.price_list_rate,
                `tabItem Price`.price_list_rate as rate,
                `tabItem Price`.price_list_rate as base_rate,
                `tabItem Price`.currency,
                COALESCE(`tabBin`.actual_qty, 0) as actual_qty
            FROM `tabItem`
            LEFT JOIN `tabItem Price` 
                ON `tabItem`.name = `tabItem Price`.item_code 
                AND `tabItem Price`.selling = 1 
                AND `tabItem Price`.price_list = %(price_list)s
                AND (`tabItem Price`.valid_from IS NULL OR `tabItem Price`.valid_from <= CURDATE())
                AND (`tabItem Price`.valid_upto IS NULL OR `tabItem Price`.valid_upto >= CURDATE())
            LEFT JOIN `tabBin`
                ON `tabItem`.name = `tabBin`.item_code
                AND `tabBin`.warehouse = %(warehouse)s
            WHERE {where_clause}
            ORDER BY `tabItem`.item_name ASC
            LIMIT 50
            """,
            params,
            as_dict=True
        )
        
        return items
        
    except Exception as e:
        return []
