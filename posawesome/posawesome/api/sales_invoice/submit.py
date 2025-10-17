# -*- coding: utf-8 -*-
"""
Submit Invoice Function - ERPNext Natural Operations
Handles invoice submission using ERPNext's official submit method
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _


@frappe.whitelist()
def submit_invoice(name=None, data=None, invoice=None, invoice_data=None, print_invoice=False):
    """
    POST - Submit invoice using ERPNext's natural operations
    
    ERPNext Natural Approach:
    - Use ERPNext's official submit() method
    - Business logic (offers, payments) handled in before_submit hook
    - No manual processing, dual saves, or complex payment logic needed
    """
    try:
        # Handle different parameter formats for backward compatibility
        invoice_name = None
        
        if name:
            invoice_name = name
        elif data:
            data_dict = json.loads(data) if isinstance(data, str) else data
            invoice_name = data_dict.get("name")
        elif invoice:
            # The frontend passes the whole invoice document here
            invoice_dict = json.loads(invoice) if isinstance(invoice, str) else invoice  
            invoice_name = invoice_dict.get("name")
        elif invoice_data:
            invoice_data_dict = json.loads(invoice_data) if isinstance(invoice_data, str) else invoice_data
            invoice_name = invoice_data_dict.get("name")
        
        if not invoice_name:
            # Log what parameters we received to help debug
            frappe.log_error(f"submit_invoice: Missing name. name={name}", "Submit Invoice Missing Name")
            frappe.throw(_("Invoice name is required for submission"))

        # ERPNext Natural Submission
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # Use ERPNext's official submit method
        # This will automatically call all hooks:
        # - validate() 
        # - before_submit() (where offers and payments are handled)
        # - All ERPNext standard validations and calculations
        doc.submit()
        
        # Return success response using existing formatter
        from .invoice_response import get_minimal_invoice_response
        invoice_data = get_minimal_invoice_response(doc)
        
        # Return in the format expected by frontend
        result = {
            "success": True,
            "invoice": invoice_data,
            "print_invoice": print_invoice
        }
        return result
        
    except Exception as e:
        frappe.log_error(f"Error in submit_invoice: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
