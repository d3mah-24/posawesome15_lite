# -*- coding: utf-8 -*-
"""
New optimized get_items function for POS Awesome
Standalone function with all required fields for frontend
"""

import json
import frappe
from frappe.utils import nowdate
from erpnext.stock.doctype.batch.batch import get_batch_qty
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups


@frappe.whitelist()
def get_items(
    pos_profile, price_list=None, item_group="", search_value="", customer=None
):
    """
    Optimized lightweight function to get items - based on ERPNext approach
    Only returns essential fields for fast performance
    """
    pos_profile = json.loads(pos_profile)
    today = nowdate()
    warehouse = pos_profile.get("warehouse")
    
    if not price_list:
        price_list = pos_profile.get("selling_price_list")
    
    # Build lightweight conditions
    conditions = ["item.disabled = 0", "item.is_sales_item = 1", "item.is_fixed_asset = 0"]
    
    # Item group condition
    if item_group:
        conditions.append(f"item.item_group LIKE '%{item_group}%'")
    
    # Search condition
    if search_value:
        conditions.append(f"(item.name LIKE '%{search_value}%' OR item.item_name LIKE '%{search_value}%')")
    
    # POS Profile item groups condition
    item_groups = get_item_groups(pos_profile.get("name"))
    if item_groups:
        item_groups_str = "', '".join(item_groups)
        conditions.append(f"item.item_group IN ('{item_groups_str}')")
    
    # Template items condition
    if not pos_profile.get("posa_show_template_items"):
        conditions.append("item.has_variants = 0")
    
    where_clause = " AND ".join(conditions)
    
    # Lightweight SQL query - only essential fields
    sql_query = f"""
    SELECT 
        item.name AS item_code,
        item.item_name,
        item.description,
        item.stock_uom,
        item.image,
        item.is_stock_item,
        item.has_variants,
        item.variant_of,
        item.item_group,
        item.has_batch_no,
        item.has_serial_no,
        item.max_discount,
        item.brand
    FROM `tabItem` item
    WHERE {where_clause}
    ORDER BY item.item_name ASC
    LIMIT 50
    """
    
    # Execute lightweight query
    items_data = frappe.db.sql(sql_query, as_dict=True)
    
    # Process items with minimal additional queries
    result = []
    for item in items_data:
        item_code = item['item_code']
        
        # Get stock quantity - lightweight query
        stock_qty = frappe.db.sql(f"""
            SELECT COALESCE(SUM(qty_after_transaction), 0) as qty
            FROM `tabStock Ledger Entry`
            WHERE item_code = %s AND warehouse = %s AND is_cancelled = 0
            ORDER BY posting_date DESC, posting_time DESC
            LIMIT 1
        """, (item_code, warehouse), as_dict=True)
        
        item['actual_qty'] = stock_qty[0]['qty'] if stock_qty else 0
        
        # Get price - lightweight query
        price_data = frappe.db.sql(f"""
            SELECT price_list_rate, currency
            FROM `tabItem Price`
            WHERE item_code = %s AND price_list = %s AND selling = 1
                AND (valid_from IS NULL OR valid_from <= %s)
                AND (valid_upto IS NULL OR valid_upto >= %s)
            ORDER BY valid_from DESC
            LIMIT 1
        """, (item_code, price_list, today, today), as_dict=True)
        
        if price_data:
            item['rate'] = price_data[0]['price_list_rate']
            item['currency'] = price_data[0]['currency']
        else:
            item['rate'] = 0
            item['currency'] = pos_profile.get("currency", "SAR")
        
        # Filter by stock if required
        if pos_profile.get("posa_display_items_in_stock") and item['actual_qty'] <= 0:
            continue
            
        result.append(item)
    
    return result


def get_item_attributes(item_code):
    """
    Get item attributes for template items
    """
    try:
        attributes = frappe.db.get_all(
            "Item Variant Attribute",
            fields=["attribute"],
            filters={"parenttype": "Item", "parent": item_code},
            order_by="idx asc",
        )

        optional_attributes = get_item_optional_attributes(item_code)

        for a in attributes:
            values = frappe.db.get_all(
                "Item Attribute Value",
                fields=["attribute_value", "abbr"],
                filters={"parenttype": "Item Attribute", "parent": a.attribute},
                order_by="idx asc",
            )
            a.values = values
            if a.attribute in optional_attributes:
                a.optional = True

        return attributes
    except Exception as e:
        frappe.logger().error(f'Error in get_item_attributes: {e}')
        return []

@frappe.whitelist()
def get_items_groups():
    """
    Get list of item groups for POS interface
    Returns list of item group names
    """
    return frappe.db.sql(
        """
        SELECT name 
        FROM `tabItem Group`
        WHERE is_group = 0
        ORDER BY name
        LIMIT 200
        """,
        as_dict=1,
    )