# -*- coding: utf-8 -*-
"""
Unified Barcode Handler
Intelligently determines barcode type and returns item details with price
All barcode types handled in one place using Frappe ORM
"""

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_barcode_item(pos_profile, barcode_value):
    """
    Main entry point for all barcode scanning.
    Automatically determines barcode type and returns item with price.
    
    Args:
        pos_profile: JSON string of POS Profile with settings
        barcode_value: Scanned barcode string
        
    Returns:
        dict: Item details {item_code, item_name, uom, rate, qty, etc.}
              Empty dict {} if item not found
    """
    try:
        # Parse POS Profile
        if isinstance(pos_profile, str):
            pos_profile = json.loads(pos_profile)
        
        # Log input
        frappe.log_error(
            f"=== BARCODE SCAN ===\n"
            f"Barcode: {barcode_value}\n"
            f"Length: {len(barcode_value)}\n"
            f"POS Profile: {pos_profile.get('name')}",
            "Barcode Input"
        )
        
        # Try scale barcode first (highest priority - specific format)
        result = _get_scale_barcode(pos_profile, barcode_value)
        if result:
            frappe.log_error(
                f"✓ Scale barcode matched\nItem: {result.get('item_code')}\nQty: {result.get('qty')}",
                "Barcode Success - Scale"
            )
            return result
        
        # Try private barcode second (medium priority - specific prefixes)
        result = _get_private_barcode(pos_profile, barcode_value)
        if result:
            frappe.log_error(
                f"✓ Private barcode matched\nItem: {result.get('item_code')}",
                "Barcode Success - Private"
            )
            return result
        
        # Try normal barcode last (fallback - search Item Barcode table)
        result = _get_normal_barcode(pos_profile, barcode_value)
        if result:
            frappe.log_error(
                f"✓ Normal barcode matched\nItem: {result.get('item_code')}",
                "Barcode Success - Normal"
            )
            return result
        
        # Not found in any category
        frappe.log_error(
            f"✗ Barcode not found: {barcode_value}",
            "Barcode Not Found"
        )
        return {}
        
    except Exception as e:
        frappe.log_error(
            f"Barcode processing error: {str(e)}\nBarcode: {barcode_value}",
            "Barcode Error"
        )
        return {}


def _get_scale_barcode(profile, barcode):
    """
    Handle scale/weight barcodes.
    Format: PREFIX + ITEM_CODE + WEIGHT
    Example: 44 + 12003 + 10010 = "4412003100100"
    
    Returns item with calculated weight as qty
    """
    try:
        # Get scale barcode configuration
        enabled = profile.get("posa_enable_scale_barcode")
        if not enabled or enabled != 1:
            return None
        
        # Get format settings (convert to string if needed)
        prefix = str(profile.get("posa_scale_barcode_start", ""))
        total_length = profile.get("posa_scale_barcode_lenth")
        item_code_length = profile.get("posa_scale_item_code_length")
        weight_length = profile.get("posa_weight_length")
        
        # Validate configuration
        if not all([prefix, total_length, item_code_length, weight_length]):
            return None
        
        # Check if barcode matches scale format
        if not barcode.startswith(prefix) or len(barcode) != total_length:
            return None
        
        # Extract item code and weight
        prefix_len = len(prefix)
        item_code_part = barcode[prefix_len:prefix_len + item_code_length]
        weight_part = barcode[prefix_len + item_code_length:prefix_len + item_code_length + weight_length]
        
        # Log extraction
        frappe.log_error(
            f"Scale barcode extraction:\n"
            f"Prefix: {prefix} (len={prefix_len})\n"
            f"Item Code: {item_code_part}\n"
            f"Weight Raw: {weight_part}",
            "Scale Barcode Parse"
        )
        
        # Fetch item with price using ORM
        item_data = _fetch_item_with_price(item_code_part, profile.get("selling_price_list"))
        if not item_data:
            return None
        
        # Calculate weight (convert grams to kg, remove trailing zeros)
        try:
            weight_value = flt(weight_part) / 1000  # Convert to kg
            # Remove trailing zeros: 10010 → 10.01 kg (not 10.010)
            item_data["qty"] = flt(weight_value, 3)
        except:
            item_data["qty"] = 1
        
        return item_data
        
    except Exception as e:
        frappe.log_error(f"Scale barcode error: {str(e)}", "Scale Barcode Error")
        return None


def _get_private_barcode(profile, barcode):
    """
    Handle private barcodes with custom prefixes.
    Format: PREFIX + ITEM_CODE + CUSTOM_DATA
    Example: 91 + 12003 + 100100 = "9112003100100"
    
    Supports multiple prefixes: 91, 92, 93, etc.
    Returns item with qty=1
    """
    try:
        # Get private barcode configuration
        enabled = profile.get("posa_enable_private_barcode")
        if not enabled or enabled != 1:
            return None
        
        # Get format settings
        prefixes_str = str(profile.get("posa_private_barcode_prefixes", ""))
        total_length = profile.get("posa_private_barcode_lenth")
        item_code_length = profile.get("posa_private_item_code_length")
        
        # Validate configuration
        if not all([prefixes_str, total_length, item_code_length]):
            return None
        
        # Check barcode length
        if len(barcode) != total_length:
            return None
        
        # Parse prefixes (comma-separated: "91,92,93")
        prefixes = [p.strip() for p in prefixes_str.split(",")]
        
        # Check if barcode starts with any valid prefix
        matched_prefix = None
        for prefix in prefixes:
            if barcode.startswith(prefix):
                matched_prefix = prefix
                break
        
        if not matched_prefix:
            return None
        
        # Extract item code
        prefix_len = len(matched_prefix)
        item_code_part = barcode[prefix_len:prefix_len + item_code_length]
        
        # Log extraction
        frappe.log_error(
            f"Private barcode extraction:\n"
            f"Prefix: {matched_prefix}\n"
            f"Item Code: {item_code_part}",
            "Private Barcode Parse"
        )
        
        # Fetch item with price using ORM
        item_data = _fetch_item_with_price(item_code_part, profile.get("selling_price_list"))
        if not item_data:
            return None
        
        # Private barcodes always have qty=1
        item_data["qty"] = 1
        
        return item_data
        
    except Exception as e:
        frappe.log_error(f"Private barcode error: {str(e)}", "Private Barcode Error")
        return None


def _get_normal_barcode(profile, barcode):
    """
    Handle normal barcodes from Item Barcode table.
    Searches for exact barcode match in child table.
    
    Returns item with qty=1
    """
    try:
        # Search Item Barcode table using ORM
        barcode_entry = frappe.db.get_value(
            "Item Barcode",
            filters={"barcode": barcode},
            fieldname="parent"
        )
        
        if not barcode_entry:
            return None
        
        # Log found item
        frappe.log_error(
            f"Normal barcode found:\n"
            f"Barcode: {barcode}\n"
            f"Item Code: {barcode_entry}",
            "Normal Barcode Parse"
        )
        
        # Fetch item with price using ORM
        item_data = _fetch_item_with_price(barcode_entry, profile.get("selling_price_list"))
        if not item_data:
            return None
        
        # Normal barcodes always have qty=1
        item_data["qty"] = 1
        
        return item_data
        
    except Exception as e:
        frappe.log_error(f"Normal barcode error: {str(e)}", "Normal Barcode Error")
        return None


def _fetch_item_with_price(item_code, price_list):
    """
    Central query for all barcode types.
    Returns only required fields for invoice creation.
    
    Returns:
        dict: {item_code, item_name, stock_uom, max_discount, price_list_rate}
              or None if not found/invalid
    """
    try:
        # Single optimized query joining Item and Item Price
        result = frappe.db.sql(
            """
            SELECT 
                `tabItem`.name as item_code,
                `tabItem`.item_name,
                `tabItem`.stock_uom,
                `tabItem`.max_discount,
                COALESCE(`tabItem Price`.price_list_rate, 0) as price_list_rate
            FROM `tabItem`
            LEFT JOIN `tabItem Price` 
                ON `tabItem`.name = `tabItem Price`.item_code
                AND `tabItem Price`.selling = 1
                AND `tabItem Price`.price_list = %(price_list)s
            WHERE `tabItem`.name = %(item_code)s
                AND `tabItem`.disabled = 0
                AND `tabItem`.is_fixed_asset = 0
            LIMIT 1
            """,
            {
                "item_code": item_code,
                "price_list": price_list
            },
            as_dict=True
        )
        
        if not result:
            frappe.log_error(
                f"Item not found or not sellable: {item_code}",
                "Item Fetch Error"
            )
            return None
        
        item = result[0]
        
        # Log if no price found
        if not item.get("price_list_rate"):
            frappe.log_error(
                f"No price found for item: {item_code} in price list: {price_list}",
                "Price Not Found"
            )
        
        # Return clean response
        return {
            "item_code": item.get("item_code"),
            "item_name": item.get("item_name"),
            "stock_uom": item.get("stock_uom"),
            "uom": item.get("stock_uom"),  # Default UOM
            "max_discount": item.get("max_discount", 0),
            "price_list_rate": item.get("price_list_rate", 0),
            "rate": item.get("price_list_rate", 0),  # Same as price_list_rate
        }
        
    except Exception as e:
        frappe.log_error(
            f"Error fetching item: {item_code}\nError: {str(e)}",
            "Item Fetch Error"
        )
        return None
