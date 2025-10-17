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
    - Simple retry on timestamp mismatch
    
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
            frappe.log_error(f"update_invoice: No name in data", "Update Invoice Error")
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
        # - Field validations (handled by validate hook)
        # - Tax and total calculations
        # - Business rule validations
        # - Automatic offers (handled by hooks)
        
        # Use optimized save with ignore_version=True for better concurrency
        doc.save(ignore_version=True)
        
        # Immediate commit for faster processing and lock release
        frappe.db.commit()
        
        # Return response using existing formatter
        from .invoice_response import get_minimal_invoice_response
        return get_minimal_invoice_response(doc)
        
    except frappe.exceptions.QueryTimeoutError as e:
        # Handle database timeouts gracefully as per improvement policy
        frappe.log_error("Query timeout in update_invoice", "Invoice Update Timeout")
        frappe.throw(_("Database is busy. Please try again in a moment."))
        
    except frappe.exceptions.TimestampMismatchError as e:
        # Handle timestamp mismatch with ignore_version approach
        frappe.log_error("Timestamp mismatch - using ignore_version", "Invoice Update Timestamp")
        try:
            # Get fresh document and save with ignore_version
            doc = frappe.get_doc("Sales Invoice", data.get("name"))
            doc.update(data)
            doc.save(ignore_version=True)
            frappe.db.commit()
            
            from .invoice_response import get_minimal_invoice_response
            return get_minimal_invoice_response(doc)
        except Exception as retry_error:
            frappe.log_error(f"Ignore version save failed: {str(retry_error)[:80]}", "Invoice Update Ignore Version Failed")
            raise
        
    except Exception as e:
        # Comprehensive error logging as per improvement policy
        frappe.log_error(f"Update error: {str(e)[:100]}", "Invoice Update Error")
        raise
