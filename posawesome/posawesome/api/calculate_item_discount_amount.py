# -*- coding: utf-8 -*-
"""
Calculate Item Discount Amount API
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def calculate_item_discount_amount(price_list_rate, discount_percentage):
    """
    Calculate discount amount for an item
    """
    if not price_list_rate or not discount_percentage:
        return 0
    
    discount_amount = flt(price_list_rate) * flt(discount_percentage) / 100
    return discount_amount
