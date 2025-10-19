# -*- coding: utf-8 -*-
"""
Updated to use ERPNext Sales Invoice native methods only.
No custom calculations - everything handled by ERPNext core.
"""
from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def update_invoice(data):
    """
    Update Sales Invoice using ERPNext native methods only.
    Uses Sales Invoice + is_pos=1 + update_stock=1 approach.
    """
    try:
        # Parse JSON data
        if isinstance(data, str):
            data = json.loads(data)
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        if not data.get("name"):
            frappe.throw(_("Invoice name is required for update operations"))

        # Get existing Sales Invoice document
        doc = frappe.get_doc("Sales Invoice", data.get("name"))

        # Verify it's still a draft
        if doc.docstatus != 0:
            frappe.throw(_("Cannot update submitted Sales Invoice"))

        # Handle empty items (deletion case)
        if data.get("items") is not None and not data.get("items"):
            frappe.delete_doc("Sales Invoice", doc.name, ignore_permissions=True, force=True)
            frappe.db.commit()
            return {"message": "Invoice deleted successfully"}

        # Update document with new data
        doc.update(data)
        
        # Ensure POS settings are maintained
        doc.is_pos = 1
        doc.update_stock = 1

        # Let ERPNext handle all calculations using native methods
        doc.calculate_taxes_and_totals()

        # Save using ERPNext native save
        doc.save()
        frappe.db.commit()

        # Return updated document
        return doc.as_dict()

    except frappe.exceptions.ValidationError as ve:
        # Handle validation errors gracefully
        frappe.log_error(f"Validation error in update_invoice: {str(ve)}", "Invoice Update Validation")
        frappe.throw(_("Validation error: {0}").format(str(ve)))

    except Exception as e:
        # Log and re-raise any other errors
        frappe.log_error(f"Error in update_invoice: {str(e)}", "Invoice Update Error")
        frappe.throw(_("Error updating invoice: {0}").format(str(e)))
