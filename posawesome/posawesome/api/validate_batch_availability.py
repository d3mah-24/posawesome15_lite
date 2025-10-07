# -*- coding: utf-8 -*-
"""
Validate Batch Availability API
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import flt

from erpnext.stock.doctype.batch.batch import (
    get_batch_qty,
)


@frappe.whitelist()  # type: ignore
def validate_batch_availability(item_code, batch_no, warehouse, qty):
    """
    Validate if a batch has sufficient quantity
    """
    try:
        if isinstance(qty, str):
            qty = flt(qty)
        
        available_qty = get_batch_qty(batch_no, warehouse)
        
        if available_qty < qty:
            return {
                "valid": False,
                "message": f"Insufficient quantity in batch {batch_no}. Available: {available_qty}, Required: {qty}",
                "available_qty": available_qty,
                "required_qty": qty
            }
        
        return {
            "valid": True,
            "message": "Batch has sufficient quantity",
            "available_qty": available_qty,
            "required_qty": qty
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error validating batch: {str(e)}",
            "available_qty": 0,
            "required_qty": qty
        }
