# -*- coding: utf-8 -*-
"""
Calculate Payment Summary API
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def calculate_payment_summary(invoice_name):
    """
    Calculate payment summary for an invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        
        total_amount = flt(doc.grand_total)
        paid_amount = sum(flt(p.amount) for p in doc.payments)
        outstanding_amount = total_amount - paid_amount
        
        return {
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "outstanding_amount": outstanding_amount,
            "is_fully_paid": outstanding_amount <= 0,
            "payments": [p.as_dict() for p in doc.payments]
        }
        
    except Exception as e:
        frappe.throw(_("Error calculating payment summary: {0}").format(str(e)))
