# -*- coding: utf-8 -*-
"""
Validate Invoice Items API
"""

from __future__ import unicode_literals

import frappe


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
            if frappe.utils.flt(item.qty) <= 0:
                validation_errors.append(
                    f"Quantity must be greater than 0 for item {item.item_code} (Row {idx + 1})"
                )
            
            # Check rate
            if frappe.utils.flt(item.rate) < 0:
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
