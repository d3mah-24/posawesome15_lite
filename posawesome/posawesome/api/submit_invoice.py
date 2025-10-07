# -*- coding: utf-8 -*-
"""
Submit Invoice API
"""

from __future__ import unicode_literals

import json

import frappe


@frappe.whitelist()  # type: ignore
def submit_invoice(invoice, data):
    """
    Submit invoice with additional processing
    """
    try:
        if isinstance(invoice, str):
            invoice = json.loads(invoice)
        if isinstance(data, str):
            data = json.loads(data)

        # Get the invoice document
        doc = frappe.get_doc("Sales Invoice", invoice["name"])

        # Apply any additional data
        if data:
            doc.update(data)
        
        # Fix rounding issues before submit
        if doc.is_pos and doc.payments:
            total_payments = sum(frappe.utils.flt(p.amount) for p in doc.payments)
            grand_total = frappe.utils.flt(doc.grand_total)
            difference = total_payments - grand_total
            
            # Auto-adjust if difference is small (rounding issue)
            if abs(difference) <= 1.0 and difference != 0:
                doc.payments[0].amount = frappe.utils.flt(doc.payments[0].amount) - difference

        # Submit the invoice
        doc.submit()

        return doc.as_dict()

    except Exception as e:
        frappe.log_error(f"Error submitting invoice: {str(e)}")
        raise
