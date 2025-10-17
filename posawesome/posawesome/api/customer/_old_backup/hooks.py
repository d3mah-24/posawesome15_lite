# -*- coding: utf-8 -*-
"""
Customer Hooks Functions
Handles Customer hooks (after_insert, validate)
"""

from __future__ import unicode_literals

import frappe
from .referral_code import create_customer_referral_code, validate_referral_code
from .gift_coupon import create_gift_coupon


def after_insert(doc, method):
    create_customer_referral_code(doc)
    create_gift_coupon(doc)


def validate(doc, method):
    validate_referral_code(doc)
