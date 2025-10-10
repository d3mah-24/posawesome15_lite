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

# متغير عام لتجميع التشخيصات
debug_log = []

def log_debug(message):
    """إضافة رسالة للتشخيص العام"""
    debug_log.append(str(message))

def clear_debug_log():
    """مسح التشخيص العام"""
    global debug_log
    debug_log = []

def save_debug_log():
    """حفظ التشخيص العام في سجل واحد"""
    global debug_log
    if debug_log:
        # حفظ في سجل الأخطاء فقط (بدون مسح)
        frappe.log_error(message="\n".join(debug_log), title="Item API - تشخيص شامل")
        # لا نمسح debug_log هنا - نتركه للتجميع


@frappe.whitelist()
def get_items(pos_profile, price_list=None, item_group="", search_value="", customer=None):
    """
    GET - Get items for POS
    """
    try:
        pos_profile = json.loads(pos_profile)
        
        if not price_list:
            price_list = pos_profile.get("selling_price_list")
        
        # Simple filters - only enabled sales items (exclude templates)
        filters = {
            "disabled": 0,
            "is_sales_item": 1,
            "has_variants": 0  # Exclude template items
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
            # Get price for each item
            price_data = frappe.get_all(
                "Item Price",
                filters={
                    "item_code": item.item_code,
                    "price_list": price_list,
                    "selling": 1
                },
                fields=["price_list_rate"],
                limit=1
            )
            
            if price_data and price_data[0]["price_list_rate"]:
                item["rate"] = price_data[0]["price_list_rate"]
                item["price_list_rate"] = item["rate"]
                item["base_rate"] = item["rate"]
            else:
                # Set default price to avoid "No price" error
                item["rate"] = 0.01  # Minimum price to avoid validation error
                item["price_list_rate"] = 0.01
                item["base_rate"] = 0.01
            
            result.append(item)
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Error getting items: {str(e)}")
        return []


@frappe.whitelist()
def get_items_groups():
    """
    GET - Get item groups
    """
    try:
        return frappe.get_all(
            "Item Group",
            filters={"is_group": 0},
            fields=["name", "parent_item_group"],
            order_by="name"
        )
    except Exception as e:
        frappe.log_error(f"Error getting item groups: {str(e)}")
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
            return item
        else:
            frappe.log_error(f"❌ Barcode not found: {barcode_value}", "Items Barcode")
            return {}
            
    except Exception as e:
        frappe.log_error(f"❌ Error searching barcode: {str(e)}", "Items Barcode")
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
            return item
        else:
            return {}
            
    except Exception as e:
        frappe.log_error(f"❌ Error searching scale barcode: {str(e)}", "Scale Barcode")
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
            return item_data[0]
        else:
            return {}
            
    except Exception as e:
        frappe.log_error(f"❌ Error searching private barcode: {str(e)}", "Private Barcode")
        return {}


# دالة لحفظ جميع التشخيصات في Error Log
def show_all_debug_logs():
    """حفظ جميع التشخيصات المجمعة في Error Log"""
    global debug_log
    if debug_log:
        # حفظ في سجل الأخطاء فقط
        frappe.log_error(message="\n".join(debug_log), title="Item API - جميع التشخيصات المجمعة")
        
        # مسح التشخيصات بعد الحفظ
        debug_log = []
