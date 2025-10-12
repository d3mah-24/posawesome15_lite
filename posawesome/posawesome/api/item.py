# -*- coding: utf-8 -*-
"""
Item API
Handles all Item related operations
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _
from frappe.utils import nowdate
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups

# Item API - Simplified logging


@frappe.whitelist()
def get_items(pos_profile, price_list=None, item_group="", search_value="", customer=None):
    """
    GET - Get items for POS
    Returns items with prices and stock qty in a single optimized query
    
    Frontend expects:
    - item_code, item_name, stock_uom
    - rate, price_list_rate, base_rate, currency
    - actual_qty (stock quantity from warehouse)
    
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
        
        # Add item_group filter if provided
        if item_group and item_group.strip():
            where_conditions.append(f"`tabItem`.item_group = '{frappe.db.escape(item_group)}'")
        
        # Add search filter (item_code OR item_name)
        search_pattern = f"%{search_value}%" if search_value else "%%"
        where_conditions.append("(`tabItem`.name LIKE %s OR `tabItem`.item_name LIKE %s)")
        
        where_clause = " AND ".join(where_conditions)
        
        # Single optimized query with JOINs for price and stock
        query = f"""
            SELECT 
                `tabItem`.name as item_code,
                `tabItem`.item_name,
                `tabItem`.stock_uom,
                COALESCE(`tabItem Price`.price_list_rate, 0.01) as rate,
                COALESCE(`tabItem Price`.price_list_rate, 0.01) as price_list_rate,
                COALESCE(`tabItem Price`.price_list_rate, 0.01) as base_rate,
                COALESCE(`tabItem Price`.currency, %s) as currency,
                COALESCE(`tabBin`.actual_qty, 0) as actual_qty
            FROM `tabItem`
            LEFT JOIN `tabItem Price` 
                ON `tabItem`.name = `tabItem Price`.item_code 
                AND `tabItem Price`.selling = 1 
                AND `tabItem Price`.price_list = %s
                AND (`tabItem Price`.valid_from IS NULL OR `tabItem Price`.valid_from <= CURDATE())
                AND (`tabItem Price`.valid_upto IS NULL OR `tabItem Price`.valid_upto >= CURDATE())
            LEFT JOIN `tabBin`
                ON `tabItem`.name = `tabBin`.item_code
                AND `tabBin`.warehouse = %s
            WHERE {where_clause}
            ORDER BY `tabItem`.item_name ASC
            LIMIT 50
        """
        
        # Execute query with parameters
        items = frappe.db.sql(
            query,
            (
                pos_profile.get("currency", "USD"),
                price_list,
                warehouse,
                search_pattern,
                search_pattern
            ),
            as_dict=True
        )
        
        return items
        
    except Exception as e:
        frappe.log_error(f"item.py(get_items): Error {str(e)}", "Item API")
        return []


@frappe.whitelist()
def get_items_groups():
    """
    GET - Get item groups
    """
    try:
        result = frappe.get_all(
            "Item Group",
            filters={"is_group": 0},
            fields=["name", "parent_item_group"],
            order_by="name"
        )
        return result
    except Exception as e:
        frappe.log_error(f"item.py(get_items_groups): Error {str(e)}", "Item API")
        return []


@frappe.whitelist()
def search_items_barcode(pos_profile, barcode_value):
    """
    POST - Search items by barcode
    """
    pos_profile = json.loads(pos_profile)
    
    try:
        # Direct search in tabItem Barcode with join to tabItem and tabItem Price
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
                AND `tabItem`.has_variants = 0
            ORDER BY `tabItem Price`.valid_from DESC
            LIMIT 1
            """,
            (pos_profile.get("selling_price_list", ""), barcode_value),
            as_dict=True
        )
        
        if item_data:
            item = item_data[0]
            frappe.log_error(f"item.py(search_items_barcode): Found {item.get('item_code', 'N/A')}", "Item API")
            return item
        else:
            frappe.log_error(f"item.py(search_items_barcode): Not found {barcode_value}", "Item API")
            return {}
            
    except Exception as e:
        frappe.log_error(f"item.py(search_items_barcode): Error {str(e)}", "Item API")
        return {}


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
            frappe.log_error(f"item.py(search_scale_barcode): Found {item.get('item_code', 'N/A')} weight {weight}", "Item API")
            return item
        else:
            frappe.log_error(f"item.py(search_scale_barcode): Not found {barcode_value}", "Item API")
            return {}
            
    except Exception as e:
        frappe.log_error(f"item.py(search_scale_barcode): Error {str(e)}", "Item API")
        return {}


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
            frappe.log_error(f"item.py(search_private_barcode): Found {item.get('item_code', 'N/A')}", "Item API")
            return item
        else:
            frappe.log_error(f"item.py(search_private_barcode): Not found {barcode_value}", "Item API")
            return {}
            
    except Exception as e:
        frappe.log_error(f"item.py(search_private_barcode): Error {str(e)}", "Item API")
        return {}


# Item API - Simplified logging completed
