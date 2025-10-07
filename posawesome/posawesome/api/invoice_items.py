# -*- coding: utf-8 -*-
"""
POS Invoice Items Management API

This module handles all item-related operations for POS invoices:
- Add items to invoice
- Update item quantities, rates, discounts
- Remove items from invoice
- Item validation and calculations
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def add_item_to_invoice(invoice_name, item_code, qty, rate, uom):
    """
    POST - Add item to invoice
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
    doc.append("items", {
        "item_code": item_code,
        "qty": qty,
        "rate": rate,
        "uom": uom
    })
    doc.save()
    return doc.as_dict()


@frappe.whitelist()  # type: ignore
def update_item_in_invoice(
    invoice_name, item_idx, qty=None, rate=None, discount_percentage=None
):
    """
    PUT - Update item in invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)

        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))

        item = doc.items[item_idx]

        if qty is not None:
            item.qty = flt(qty)
        if rate is not None:
            item.rate = flt(rate)
        if discount_percentage is not None:
            item.discount_percentage = flt(discount_percentage)

        doc.save()
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        frappe.throw(_("Error updating item: {0}").format(str(e)))


@frappe.whitelist()  # type: ignore
def delete_item_from_invoice(invoice_name, item_idx):
    """
    DELETE - Remove item from invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)

        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))

        doc.items.pop(item_idx)
        doc.save()
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        frappe.throw(_("Error deleting item: {0}").format(str(e)))


@frappe.whitelist()  # type: ignore
def calculate_item_discount_amount(price_list_rate, discount_percentage):
    """
    Calculate discount amount for an item
    """
    if not price_list_rate or not discount_percentage:
        return 0
    
    discount_amount = flt(price_list_rate) * flt(discount_percentage) / 100
    return discount_amount


@frappe.whitelist()  # type: ignore
def calculate_item_price(item_data):
    """
    Calculate item price with discounts and taxes
    """
    try:
        # Parse item data if it's a string
        if isinstance(item_data, str):
            import json
            item_data = json.loads(item_data)
        
        price_list_rate = flt(item_data.get("price_list_rate", 0))
        discount_percentage = flt(item_data.get("discount_percentage", 0))
        
        # Calculate discounted rate
        discount_amount = calculate_item_discount_amount(
            price_list_rate, discount_percentage
        )
        rate = price_list_rate - discount_amount
        
        return {
            "rate": rate,
            "discount_amount": discount_amount,
            "price_list_rate": price_list_rate
        }
    except Exception as e:
        frappe.throw(_("Error calculating item price: {0}").format(str(e)))


@frappe.whitelist()  # type: ignore
def validate_invoice_items(invoice_name):
    """
    Validate all items in an invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        
        validation_errors = []
        
        for idx, item in enumerate(doc.items):
            # Check if item exists
            if not frappe.db.exists("Item", item.item_code):
                validation_errors.append(
                    f"Item {item.item_code} does not exist (Row {idx + 1})"
                )
                continue
            
            # Check quantity
            if flt(item.qty) <= 0:
                validation_errors.append(
                    f"Quantity must be greater than 0 for item {item.item_code} (Row {idx + 1})"
                )
            
            # Check rate
            if flt(item.rate) < 0:
                validation_errors.append(
                    f"Rate cannot be negative for item {item.item_code} (Row {idx + 1})"
                )
        
        if validation_errors:
            return {
                "valid": False,
                "errors": validation_errors
            }
        
        return {
            "valid": True,
            "message": "All items are valid"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation error: {str(e)}"]
        }

