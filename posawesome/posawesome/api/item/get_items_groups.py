# -*- coding: utf-8 -*-
"""
Get Items Groups Function
Handles getting item groups
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_items_groups():
    """
    GET - Get item groups
    """
    try:
        result = frappe.get_all(
            "Item Group",
            filters={"is_group": 0},
            fields=["name", "parent_item_group"],
            order_by="name"
        )
        return result
    except Exception as e:
        return []
