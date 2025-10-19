# -*- coding: utf-8 -*-
"""
Updated to use ERPNext Sales Invoice native submission methods.
Minimal custom logic - relies on ERPNext's built-in submission workflow.
"""
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt


def before_submit(doc, method):
    """
    Minimal custom logic before submission.
    ERPNext handles most submission validations and business logic.
    """
    # Only run for POS invoices
    if not getattr(doc, 'is_pos', False):
        return
    
    # Basic payment validation (ERPNext usually handles this)
    _validate_payments(doc)


def _validate_payments(doc):
    """
    Basic payment validation.
    ERPNext handles most payment logic.
    """
    if not doc.payments:
        frappe.throw(_("At least one payment is required for POS Invoice"))
    
    # Simple total validation
    total_payments = sum(flt(payment.amount) for payment in doc.payments)
    if total_payments <= 0:
        frappe.throw(_("Payment amount must be greater than zero"))
