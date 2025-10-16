# -*- coding: utf-8 -*-
"""
Get Profile Warehouses Function
Handles getting POS Profile warehouses
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_profile_warehouses(profile_name):
    """
    GET - Get POS Profile warehouses
    """
    try:
        warehouses = frappe.get_all(
            "POS Profile Warehouse",
            filters={"parent": profile_name},
            fields=["warehouse"],
            order_by="idx"
        )
        
        result = [w.warehouse for w in warehouses]
        return result
        
    except Exception as e:
        return []
