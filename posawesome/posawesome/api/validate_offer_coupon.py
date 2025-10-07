# -*- coding: utf-8 -*-
"""
Validate Offer Coupon API
"""

from __future__ import unicode_literals

import json

import frappe


@frappe.whitelist()  # type: ignore
def validate_offer_coupon(offer_data):
    """
    Validate offer coupon code
    """
    try:
        if isinstance(offer_data, str):
            offer_data = json.loads(offer_data)
        
        coupon_code = offer_data.get("coupon_code")
        if not coupon_code:
            return {"valid": False, "message": "Coupon code is required"}
        
        # Check if coupon exists and is valid
        coupon = frappe.get_doc("POS Coupon", coupon_code)
        
        if coupon.disabled:
            return {"valid": False, "message": "Coupon is disabled"}
        
        if coupon.maximum_use > 0 and coupon.used >= coupon.maximum_use:
            return {"valid": False, "message": "Coupon usage limit exceeded"}
        
        return {
            "valid": True,
            "coupon": coupon.as_dict(),
            "message": "Coupon is valid"
        }
        
    except frappe.DoesNotExistError:
        return {"valid": False, "message": "Invalid coupon code"}
    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}
