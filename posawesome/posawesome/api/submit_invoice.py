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

        # Submit the invoice
        doc.submit()

        return doc.as_dict()

    except Exception as e:
        frappe.log_error(f"Error submitting invoice: {str(e)}")
        raise
