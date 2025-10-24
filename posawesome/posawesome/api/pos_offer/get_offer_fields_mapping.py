# -*- coding: utf-8 -*-
"""
Get Offer Fields Mapping Function
Handles field mapping for each offer type
"""

from __future__ import unicode_literals

import frappe


def get_offer_fields_mapping():
    """
    Get field mapping for each offer type
    """
    field_mapping = {
        "auto": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_type", "discount_percentage", "auto"],
        "manual": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_type", "discount_percentage", "auto"],
        "give_product": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "given_qty", "apply_item_code", "apply_item_group"],
        "loyalty": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "loyalty_program", "loyalty_points"],
        "rate": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "rate", "less_then"],
        "percentage": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_percentage"],
        "amount": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_amount"],
        "conditional": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "min_qty", "max_qty", "min_amt", "max_amt"],
        "unconditional": ["name", "title", "description", "apply_on", "item", "item_group", "brand", "discount_type", "discount_percentage", "discount_amount", "rate"]
    }

    return field_mapping
