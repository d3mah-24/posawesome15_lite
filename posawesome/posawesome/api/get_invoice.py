# -*- coding: utf-8 -*-
"""
Get Invoice API
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()  # type: ignore
def get_invoice(invoice_name):
    """
    GET - Get invoice with all data
    """
    if not invoice_name:
        return None

    doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
    return doc.as_dict()
