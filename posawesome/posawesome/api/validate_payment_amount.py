# -*- coding: utf-8 -*-
"""
Validate Payment Amount API
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def validate_payment_amount(invoice_name, payment_amount):
    """
    Validate if payment amount is valid for the invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        
        # Calculate total amount
        total_amount = flt(doc.grand_total)
        payment_amount = flt(payment_amount)
        
        # Calculate existing payments
        existing_payments = sum(flt(p.amount) for p in doc.payments)
        
        # Calculate remaining amount
        remaining_amount = total_amount - existing_payments
        
        if payment_amount > remaining_amount:
            return {
                "valid": False,
                "message": f"Payment amount ({payment_amount}) exceeds remaining amount ({remaining_amount})"
            }
        
        if payment_amount <= 0:
            return {
                "valid": False,
                "message": "Payment amount must be greater than 0"
            }
        
        return {
            "valid": True,
            "remaining_amount": remaining_amount,
            "total_amount": total_amount
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }
