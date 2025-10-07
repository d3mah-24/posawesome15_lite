# -*- coding: utf-8 -*-
"""
Update Coupon API
"""

from __future__ import unicode_literals

import frappe

from posawesome.posawesome.doctype.pos_coupon.pos_coupon import update_coupon_code_count


def update_coupon(doc, transaction_type):
    """
    Update coupon usage count
    """
    for coupon in getattr(doc, "posa_coupons", []):
        if not coupon.applied:
            continue
        update_coupon_code_count(coupon.coupon, transaction_type)
