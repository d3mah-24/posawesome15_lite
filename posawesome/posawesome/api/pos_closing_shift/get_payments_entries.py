# -*- coding: utf-8 -*-
# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_payments_entries(pos_opening_shift):
    """
    GET - Get payment entries for opening shift
    """
    try:
        return frappe.get_all(
            "Payment Entry",
            filters={
                "docstatus": 1,
                "reference_no": pos_opening_shift,
                "payment_type": "Receive",
            },
            fields=[
                "name",
                "mode_of_payment",
                "paid_amount",
                "reference_no",
                "posting_date",
                "party",
            ],
        )
        
    except Exception as e:
        frappe.log_error(f"[get_payments_entries.py][get_payments_entries] Error: {str(e)}")
        return []
