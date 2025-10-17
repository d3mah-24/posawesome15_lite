# -*- coding: utf-8 -*-
"""
Create Invoice Function - ERPNext Natural Operations
Handles new invoice creation using ERPNext's standard patterns
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _


@frappe.whitelist()
def create_invoice(data):
    """
    POST - Create new invoice using ERPNext's natural operations
    
    ERPNext Natural Approach:
    - Use frappe.new_doc() 
    - Let ERPNext handle auto-fill with set_missing_values()
    - Let ERPNext handle all calculations with save()
    - Business logic handled by hooks (validate, before_submit)
    - No manual flags, calculations, or dual saves needed
    """
    try:
        # Parse input data
        data = json.loads(data) if isinstance(data, str) else data
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        # Validate input
        if data.get("name"):
            frappe.throw(_("Use update_invoice for existing invoices"))

        if not data.get("items"):
            frappe.throw(_("Cannot create invoice without items"))

        doc = frappe.new_doc("Sales Invoice")
        doc.update(data)
        
        doc.set_missing_values() 
        doc.save()                
        
        from .invoice_response import get_minimal_invoice_response
        return get_minimal_invoice_response(doc)
        
    except Exception as e:
        frappe.log_error(f"Error in create_invoice: {str(e)}")
        raise