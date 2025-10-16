# -*- coding: utf-8 -*-
"""
Customer Gift Coupon Functions
Handles gift coupon operations
"""

from __future__ import unicode_literals

import frappe


def create_gift_coupon(doc):
    if doc.posa_referral_code:
        coupon = frappe.new_doc("POS Coupon")
        coupon.customer = doc.name
        coupon.referral_code = doc.posa_referral_code
        coupon.create_coupon_from_referral()
