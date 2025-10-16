# -*- coding: utf-8 -*-
"""
Update Opening Shift Data Function
Handles updating opening shift data
"""

from __future__ import unicode_literals

import frappe


def update_opening_shift_data(data, pos_profile):
    """
    Helper function to update opening shift data
    """
    try:
        data["pos_profile"] = frappe.get_doc("POS Profile", pos_profile)
        data["company"] = frappe.get_doc("Company", data["pos_profile"].company)
        allow_negative_stock = frappe.get_value(
            "Stock Settings", None, "allow_negative_stock"
        )
        data["stock_settings"] = {}
        data["stock_settings"].update({"allow_negative_stock": allow_negative_stock})
    except Exception as e:
        pass
