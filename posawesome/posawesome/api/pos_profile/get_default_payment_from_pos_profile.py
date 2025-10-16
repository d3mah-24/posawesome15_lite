# -*- coding: utf-8 -*-
"""
Get Default Payment From POS Profile Function
Handles getting default payment method from POS Profile
"""

from __future__ import unicode_literals

import frappe
from .get_payment_account import get_payment_account


@frappe.whitelist()
def get_default_payment_from_pos_profile(pos_profile, company):
    """
    Get default payment method from POS Profile
    """
    try:
        if not pos_profile:
            return None
            
        # Get POS Profile document
        pos_profile_doc = frappe.get_doc("POS Profile", pos_profile)
        
        # Find default payment method
        for payment in pos_profile_doc.payments:
            if payment.default:
                # Get account for this payment method
                account = get_payment_account(payment.mode_of_payment, company)
                result = {
                    "mode_of_payment": payment.mode_of_payment,
                    "account": account.get("account", "")
                }
                return result
        
        # If no default found, use first payment method
        if pos_profile_doc.payments:
            first_payment = pos_profile_doc.payments[0]
            account = get_payment_account(first_payment.mode_of_payment, company)
            result = {
                "mode_of_payment": first_payment.mode_of_payment,
                "account": account.get("account", "")
            }
            return result
            
        return None
        
    except Exception as e:
        return None
