# -*- coding: utf-8 -*-
"""
Calculate Item Price API
"""

from __future__ import unicode_literals

import json

import frappe
from frappe import _


@frappe.whitelist()  # type: ignore
def calculate_item_price(item_data):
    """
    Calculate item price with discounts and taxes
    """
    try:
        # Parse item data if it's a string
        if isinstance(item_data, str):
            item_data = json.loads(item_data)
        
        price_list_rate = frappe.utils.flt(item_data.get("price_list_rate", 0))
        discount_percentage = frappe.utils.flt(item_data.get("discount_percentage", 0))
        
        # Calculate discounted rate
        discount_amount = calculate_item_discount_amount(
            price_list_rate, discount_percentage
        )
        rate = price_list_rate - discount_amount
        
        return {
            "rate": rate,
            "discount_amount": discount_amount,
            "price_list_rate": price_list_rate
        }
    except Exception as e:
        frappe.throw(_("Error calculating item price: {0}").format(str(e)))


def calculate_item_discount_amount(price_list_rate, discount_percentage):
    """
    Calculate discount amount for an item
    """
    if not price_list_rate or not discount_percentage:
        return 0
    
    discount_amount = frappe.utils.flt(price_list_rate) * frappe.utils.flt(discount_percentage) / 100
    return discount_amount
