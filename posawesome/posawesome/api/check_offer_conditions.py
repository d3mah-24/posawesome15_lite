# -*- coding: utf-8 -*-
"""
Check Offer Conditions API
"""

from __future__ import unicode_literals

import json

import frappe
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def check_offer_conditions(offer_data, qty, amount):
    """
    Check if offer conditions are met
    """
    try:
        if isinstance(offer_data, str):
            offer_data = json.loads(offer_data)
        
        min_qty = flt(offer_data.get("min_qty", 0))
        min_amount = flt(offer_data.get("min_amount", 0))
        
        if min_qty > 0 and flt(qty) < min_qty:
            return {
                "valid": False,
                "message": f"Minimum quantity required: {min_qty}"
            }
        
        if min_amount > 0 and flt(amount) < min_amount:
            return {
                "valid": False,
                "message": f"Minimum amount required: {min_amount}"
            }
        
        return {
            "valid": True,
            "message": "Offer conditions met"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error checking conditions: {str(e)}"
        }
