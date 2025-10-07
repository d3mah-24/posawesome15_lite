# -*- coding: utf-8 -*-
"""
Submit Invoice Simple API
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()  # type: ignore
def submit_invoice_simple(invoice_name):
    """
    POST - Submit invoice (simple version)
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
    doc.submit()
    return doc.as_dict()
