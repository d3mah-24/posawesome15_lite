# -*- coding: utf-8 -*-
"""
Simple get_items function using Frappe ORM only
Returns: item_code, item_name, rate, actual_qty
Price must match stock_uom (no unit conversion)
"""

import json
import frappe
from frappe.utils import nowdate
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups


@frappe.whitelist()
def get_items(
    pos_profile, price_list=None, item_group="", search_value="", customer=None
):
    """
    Ultra simple function - only items with prices
    Returns: item_code, item_name, rate, actual_qty
    """
    try:
        pos_profile = json.loads(pos_profile)
        
        if not price_list:
            price_list = pos_profile.get("selling_price_list")
        
        # Simple filters - only enabled sales items
        filters = {
            "disabled": 0,
            "is_sales_item": 1
        }
        
        # Search filter - only by item_code or item_name
        if search_value:
            filters["name"] = ["like", f"%{search_value}%"]
        
        # Get items using ORM
        items = frappe.get_all(
            "Item",
            filters=filters,
            fields=["name as item_code", "item_name", "stock_uom"],
            limit=50,
            order_by="item_name asc"
        )
        
        result = []
        for item in items:
            item_code = item['item_code']
            
            # Get price for this item - MUST have price
            price = frappe.get_value(
                "Item Price",
                {
                    "item_code": item_code,
                    "price_list": price_list,
                    "selling": 1
                },
                ["price_list_rate", "currency"]
            )
            
            # Only add items that have prices
            if price and price[0] > 0:
                result.append({
                    "item_code": item_code,
                    "item_name": item['item_name'],
                    "rate": price[0],
                    "currency": price[1],
                    "actual_qty": 0,  # Simple - no stock check
                    "stock_uom": item['stock_uom']
                })
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Error in get_items: {str(e)}")
        return []


@frappe.whitelist()
def get_items_simple_test():
    """
    Simple test function to debug items loading
    """
    # Get first 10 items without any filters
    items = frappe.get_all(
        "Item",
        filters={"disabled": 0},
        fields=["name as item_code", "item_name", "stock_uom"],
        limit=10
    )
    
    result = []
    for item in items:
        # Get any price for this item
        price = frappe.get_value(
            "Item Price",
            {"item_code": item['item_code'], "selling": 1},
            ["price_list_rate", "currency"]
        )
        
        if price:
            result.append({
                "item_code": item['item_code'],
                "item_name": item['item_name'],
                "rate": price[0],
                "currency": price[1],
                "stock_uom": item['stock_uom']
            })
    
    frappe.log_error(f"Test function returning {len(result)} items")
    return result


@frappe.whitelist()
def get_items_groups():
    """
    Get list of item groups for POS interface
    """
    return frappe.get_all(
        "Item Group",
        filters={"is_group": 0},
        fields=["name"],
        limit=200,
        order_by="name"
    )