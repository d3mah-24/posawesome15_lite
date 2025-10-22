# -*- coding: utf-8 -*-
# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_pos_invoices(pos_opening_shift):
    """
    GET - Get POS invoices for opening shift
    """
    try:
        _submit_printed_invoices(pos_opening_shift)
        data = frappe.db.sql(
            """
        select
            name
        from
            `tabSales Invoice`
        where
            docstatus = 1 and posa_pos_opening_shift = %s
        """,
            (pos_opening_shift),
            as_dict=1,
        )

        data = [frappe.get_doc("Sales Invoice", d.name).as_dict() for d in data]

        return data
        
    except Exception as e:
        frappe.log_error(f"[get_pos_invoices.py][get_pos_invoices] Error: {str(e)}")
        return []


def _submit_printed_invoices(pos_opening_shift):
    """Helper function to submit printed invoices"""
    try:
        invoices_list = frappe.get_all(
            "Sales Invoice",
            filters={
                "posa_pos_opening_shift": pos_opening_shift,
                "docstatus": 0,
                "posa_is_printed": 1,
            },
        )
        for invoice in invoices_list:
            invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
            invoice_doc.submit()
    except Exception as e:
        frappe.log_error(f"[get_pos_invoices.py][_submit_printed_invoices] Error: {str(e)}")
