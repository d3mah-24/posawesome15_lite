# -*- coding: utf-8 -*-
"""
Updated to use ERPNext Sales Invoice native methods only.
Uses ERPNext's standard submit workflow.
"""
from __future__ import unicode_literals
import json
import frappe
from frappe import _


@frappe.whitelist()
def submit_invoice(data=None, name=None, invoice=None, invoice_data=None):
    """
    Submit Sales Invoice using ERPNext native methods only.
    Uses ERPNext's standard submission workflow.
    """
    try:
        # Determine invoice name from any parameter
        invoice_name = name or (
            (json.loads(data) if isinstance(data, str) else data or {}).get("name") if data else None
        ) or (
            (json.loads(invoice) if isinstance(invoice, str) else invoice or {}).get("name") if invoice else None
        ) or (
            (json.loads(invoice_data) if isinstance(invoice_data, str) else invoice_data or {}).get("name") if invoice_data else None
        )

        if not invoice_name:
            frappe.throw(_("Invoice name is required for submission"))

        # Get Sales Invoice document
        doc = frappe.get_doc("Sales Invoice", invoice_name)

        # Check if already submitted
        if doc.docstatus == 1:
            frappe.throw(_("Invoice is already submitted"))
        elif doc.docstatus == 2:
            frappe.throw(_("Cannot submit cancelled invoice"))

        # Update with any new data if provided
        if data:
            data_dict = json.loads(data) if isinstance(data, str) else data
            doc.update(data_dict)

        # Ensure POS settings are maintained
        doc.is_pos = 1
        doc.update_stock = 1

        # Use ERPNext native methods for calculation and submission
        doc.calculate_taxes_and_totals()
        doc.validate()
        doc.save()
        doc.submit()

        # Return submitted document
        return {
            "success": True,
            "message": "Invoice submitted successfully",
            "invoice": doc.as_dict()
        }

    except frappe.exceptions.ValidationError as ve:
        frappe.logger().error(f"Validation error in submit_invoice: {str(ve)}")
        frappe.throw(_("Validation error: {0}").format(str(ve)))

    except Exception as e:
        frappe.logger().error(f"Error in submit_invoice: {str(e)}")
        frappe.throw(_("Error submitting invoice: {0}").format(str(e)))
