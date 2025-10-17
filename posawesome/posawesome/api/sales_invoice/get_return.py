# -*- coding: utf-8 -*-
"""
Search Invoices for Return Function
Handles searching invoices for return operations
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_invoices_for_return(invoice_name, company):
    """
    Search invoices for return operations
    """
    try:
        if not invoice_name:
            return []

        # Search for invoices that can be returned
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "name": ["like", f"%{invoice_name}%"],
                "company": company,
                "docstatus": 1,  # Only submitted invoices
                "is_return": 0,  # Not already a return
                "outstanding_amount": [">", 0]  # Has outstanding amount
            },
            fields=["name", "customer", "grand_total", "outstanding_amount", "posting_date"],
            limit=20
        )

        return invoices

    except Exception as e:
        return []
