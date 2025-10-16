# -*- coding: utf-8 -*-
"""
Get Offer Filters Mapping Function
Handles filter mapping for each offer type
"""

from __future__ import unicode_literals

import frappe


def get_offer_filters_mapping():
    """
    Get filter mapping for each offer type
    """
    filter_mapping = {
        "auto": {"disable": 0, "auto": 1},
        "manual": {"disable": 0, "auto": 0},
        "coupon": {"disable": 0, "coupon_based": 1},
        "give_product": {"disable": 0, "offer": "Give Product"},
        "loyalty": {"disable": 0, "offer": "Loyalty Point"},
        "rate": {"disable": 0, "discount_type": "Rate"},
        "percentage": {"disable": 0, "discount_type": "Discount Percentage"},
        "amount": {"disable": 0, "discount_type": "Discount Amount"},
        "conditional": {"disable": 0, "min_qty": [">", 0]},
        "unconditional": {"disable": 0, "min_qty": 0, "max_qty": 0, "min_amt": 0, "max_amt": 0}
    }
    
    return filter_mapping
