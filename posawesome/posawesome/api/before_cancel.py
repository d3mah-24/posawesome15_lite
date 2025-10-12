# -*- coding: utf-8 -*-
"""
Before Cancel Hook for Sales Invoice
"""

from __future__ import unicode_literals

import frappe

from posawesome.posawesome.api.update_coupon import update_coupon

# Before Cancel API - Simplified logging


def before_cancel(doc, method):
    """
    Before cancel hook for Sales Invoice
    """
    # Call pre-cancel functions
    update_coupon(doc, "cancelled")
    
    # Additional validation before canceling POS invoices
    if doc.is_pos:
        # Check if invoice is already submitted
        if doc.docstatus != 1:
            frappe.throw("Only submitted invoices can be canceled")
        
        # Check if there are any related transactions
        # (This could be extended to check for returns, etc.)
        pass
    
    frappe.log_error(f"before_cancel.py(before_cancel): Completed for {doc.name}", "Before Cancel")


# Before Cancel API - Simplified logging completed
