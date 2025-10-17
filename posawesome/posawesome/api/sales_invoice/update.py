# -*- coding: utf-8 -*-
"""
Update Invoice Function - ERPNext Natural Operations  
Handles invoice updates using ERPNext's standard patterns
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _


@frappe.whitelist()
def update_invoice(data):
    """
    PUT - Update invoice using ERPNext's natural operations
    
    ERPNext Natural Approach:
    - Use frappe.get_doc() to get latest version
    - Let ERPNext handle concurrency and timestamp validation
    - Let ERPNext handle all calculations with save()
    - Business logic handled by hooks (validate, before_submit)
    - No retry mechanisms, manual timestamp handling, or dual saves needed
    
    This replaces 439 lines of complex logic with ~30 lines!
    """
    try:
        # Parse input data
        data = json.loads(data) if isinstance(data, str) else data
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        # Validate input
        if not data.get("name"):
            # Log more details about the call to help debug
            frappe.log_error(f"update_invoice called without name. Data keys: {list(data.keys()) if data else 'None'}")
            frappe.throw(_("Invoice name is required for update operations"))

        # ERPNext Natural Update - Get fresh document
        doc = frappe.get_doc("Sales Invoice", data.get("name"))
        
        # Validate draft status  
        if doc.docstatus != 0:
            frappe.throw(_("Cannot update submitted invoice"))

        # Handle empty items case
        if data.get("items") is not None and not data.get("items"):
            # If no items, delete the invoice
            frappe.delete_doc("Sales Invoice", doc.name, ignore_permissions=True)
            return None

        # Update document with new data
        doc.update(data)
        
        # Let ERPNext handle everything naturally:
        # - Timestamp validation and concurrency
        # - Field validations (handled by validate hook)
        # - Tax and total calculations
        # - Business rule validations
        # - Automatic offers (handled by hooks)
        doc.save()
        
        # Return response using existing formatter
        from .invoice_response import get_minimal_invoice_response
        return get_minimal_invoice_response(doc)
        
    except Exception as e:
        frappe.log_error(f"Error in update_invoice: {str(e)}")
        raise
