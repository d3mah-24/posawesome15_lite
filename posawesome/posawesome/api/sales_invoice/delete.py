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
        # Try to get document with shorter wait time
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        if doc.docstatus != 0:
            frappe.throw(_("Cannot delete submitted invoice"))
        
        doc.flags.ignore_permissions = True
        doc.delete()
        
        result = {"message": "Invoice deleted successfully"}
        return result
        
    except frappe.QueryTimeoutError:
        # Document is locked by another transaction (update_invoice in progress)
        # This is expected in POS with rapid operations
        frappe.clear_last_message()
        return {"message": "Invoice is being updated, deletion skipped"}
        
    except Exception as e:
        # Shorten error message to avoid CharacterLengthExceededError
        error_msg = str(e)[:100]  # Limit to 100 chars
        frappe.throw(_("Error deleting invoice: {0}").format(error_msg))
