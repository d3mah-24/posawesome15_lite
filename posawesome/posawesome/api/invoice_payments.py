# -*- coding: utf-8 -*-
"""
POS Invoice Payments Management API

This module handles all payment-related operations for POS invoices:
- Add payments to invoice
- Payment validation
- Payment calculations
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt


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

