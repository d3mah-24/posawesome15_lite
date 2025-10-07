# -*- coding: utf-8 -*-
"""
Delete Invoice API
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()  # type: ignore
def delete_invoice(invoice_name):
    """
    DELETE - Delete invoice
    """
    frappe.delete_doc("Sales Invoice", invoice_name)
    return {"message": "Invoice deleted successfully"}
