# -*- coding: utf-8 -*-
"""
Get Draft Invoices API
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()  # type: ignore
def get_draft_invoices(pos_opening_shift):
    """
    GET - Get all draft invoices for a POS opening shift
    """
    try:
        filters = {
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 0,
            "is_pos": 1
        }
        
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=[
                "name", "customer", "grand_total", "outstanding_amount",
                "creation", "modified"
            ],
            order_by="modified desc"
        )
        
        data = []
        for invoice in invoices:
            data.append({
                "name": invoice.name,
                "customer": invoice.customer,
                "grand_total": invoice.grand_total,
                "outstanding_amount": invoice.outstanding_amount,
                "creation": invoice.creation,
                "modified": invoice.modified
            })
        
        return data
        
    except Exception as e:
        frappe.log_error(f"Error getting draft invoices: {str(e)}")
        return []
