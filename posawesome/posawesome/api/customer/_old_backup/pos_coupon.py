# -*- coding: utf-8 -*-
"""
POS Coupon Functions
Handles POS coupon operations
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_pos_coupon(coupon, customer, company):
    try:
        res = check_coupon_code(coupon, customer, company)
        return res
        
    except Exception as e:
        raise


@frappe.whitelist()
def get_active_gift_coupons(customer, company):
    try:
        coupons = []
        coupons_data = frappe.get_all(
            "POS Coupon",
            filters={
                "company": company,
                "coupon_type": "Gift Card",
                "customer": customer,
                "used": 0,
            },
            fields=["coupon_code"],
        )
        if len(coupons_data):
            coupons = [i.coupon_code for i in coupons_data]
        return coupons
        
    except Exception as e:
        raise
