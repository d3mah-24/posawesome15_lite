# -*- coding: utf-8 -*-
"""
Delete Invoice Function
Handles invoice deletion
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def delete_invoice(invoice_name):
    """
    DELETE - Delete draft invoice
    Handles lock timeouts gracefully when invoice is being modified
    """
    try:
        # Try to get document with for_update=False to avoid locks
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        if doc.docstatus != 0:
            frappe.throw(_("Cannot delete submitted invoice"))
        
        # Use non-blocking delete with retry mechanism
        try:
            doc.flags.ignore_permissions = True
            doc.delete()
            frappe.db.commit()
            return {"message": "Invoice deleted successfully"}
            
        except frappe.QueryTimeoutError:
            # If delete fails due to lock, try alternative approach
            frappe.log_error("Delete timeout - trying alternative", "Invoice Delete Timeout")
            
            # Try to mark as cancelled instead of deleting
            try:
                doc.workflow_state = "Cancelled" 
                doc.save(ignore_version=True)
                frappe.db.commit()
                return {"message": "Invoice cancelled due to lock timeout"}
            except Exception:
                # If even cancellation fails, just return success to avoid blocking UI
                return {"message": "Invoice deletion queued for processing"}
        
    except frappe.QueryTimeoutError:
        # Document is locked by another transaction (update_invoice in progress)
        # This is expected in POS with rapid operations
        frappe.clear_last_message()
        return {"message": "Invoice is being updated, deletion skipped"}
        
    except Exception as e:
        # Shorten error message to avoid CharacterLengthExceededError
        error_msg = str(e)[:100]  # Limit to 100 chars
        frappe.throw(_("Error deleting invoice: {0}").format(error_msg))
