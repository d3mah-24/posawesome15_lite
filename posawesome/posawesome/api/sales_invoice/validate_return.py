# -*- coding: utf-8 -*-
"""
Validate Return Items Function
Handles validation of return items against original invoice
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import flt


def validate_return_items(return_against, invoice_items):
    """
    Validate return items against original invoice
    """
    try:
        if not return_against:
            return {"valid": True, "message": "No return against specified"}
        
        # Get original invoice
        original_invoice = frappe.get_doc("Sales Invoice", return_against)
        
        # Check if return quantities are valid
        for item in invoice_items:
            original_item = None
            for orig_item in original_invoice.items:
                if orig_item.item_code == item["item_code"]:
                    original_item = orig_item
                    break
            
            if not original_item:
                return {
                    "valid": False,
                    "message": f"Item {item['item_code']} not found in original invoice"
                }
            
            if flt(item["qty"]) > flt(original_item.qty):
                return {
                    "valid": False,
                    "message": f"Return quantity for {item['item_code']} exceeds original quantity"
                }
        
        result = {"valid": True, "message": "Return items are valid"}
        return result
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error validating return items: {str(e)}"
        }
