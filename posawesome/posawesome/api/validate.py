# -*- coding: utf-8 -*-
"""
Validate Hook for Sales Invoice
"""

from __future__ import unicode_literals

import frappe

from posawesome.posawesome.api.validate_shift import validate_shift


def validate(doc, method):
    """
    Validate hook for Sales Invoice
    """
    # Call all validation functions
    validate_shift(doc)
    
    # Validate POS-specific business rules
    if doc.is_pos:
        # Check if POS Profile allows zero-rated items
        allow_zero_rated_items = frappe.get_cached_value(
            "POS Profile",
            doc.pos_profile,
            "posa_allow_zero_rated_items"
        )
        
        for item in doc.items:
            if not item.rate or item.rate == 0:
                if allow_zero_rated_items:
                    item.is_free_item = 1
                else:
                    frappe.throw(
                        f"Rate cannot be zero for item {item.item_code}. "
                        "Please enable 'Allow Zero Rated Items' in POS Profile "
                        "or set a valid rate for this item."
                    )
            else:
                item.is_free_item = 0
