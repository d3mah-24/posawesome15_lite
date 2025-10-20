# -*- coding: utf-8 -*-
"""
Updated to use ERPNext Sales Invoice native deletion methods only.
Uses ERPNext's standard delete workflow with proper permission checks.
"""
from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def delete_invoice(invoice_name):
    """
    Delete Sales Invoice using ERPNext native methods only.
    Uses ERPNext's standard deletion workflow.
    """
    try:
        if not invoice_name:
            frappe.throw(_("Invoice name is required"))

        # Get document using ERPNext
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # Check permissions using ERPNext
        if not doc.has_permission("delete"):
            frappe.throw(_("Not permitted to delete this invoice"))
        
        # Only allow deletion of draft documents
        if doc.docstatus != 0:
            frappe.throw(_("Cannot delete submitted invoice. Use cancel instead."))
        
        # Use ERPNext native delete method
        doc.delete()
        
        return {
            "success": True,
            "message": "Invoice deleted successfully"
        }
        
    except frappe.exceptions.DoesNotExistError:
        frappe.throw(_("Invoice {0} does not exist").format(invoice_name))
        
    except frappe.exceptions.PermissionError as pe:
        frappe.throw(_("Permission denied: {0}").format(str(pe)))
        
    except frappe.exceptions.ValidationError as ve:
        frappe.throw(_("Validation error: {0}").format(str(ve)))
        
    except Exception as e:
        frappe.logger().error(f"Error in delete_invoice: {str(e)}")
        frappe.throw(_("Error deleting invoice: {0}").format(str(e)))
