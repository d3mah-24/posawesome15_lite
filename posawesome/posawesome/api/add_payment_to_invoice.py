# -*- coding: utf-8 -*-
"""
Add Payment To Invoice API
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()  # type: ignore
def add_payment_to_invoice(invoice_name, mode_of_payment, amount):
    """
    POST - Add payment to invoice
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
    doc.append("payments", {
        "mode_of_payment": mode_of_payment,
        "amount": amount
    })
    doc.save()
    return doc.as_dict()
