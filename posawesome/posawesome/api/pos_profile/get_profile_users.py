# -*- coding: utf-8 -*-
"""
Get Profile Users Function
Handles getting POS Profile users
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_profile_users(profile_name):
    """
    GET - Get POS Profile users
    """
    try:
        users = frappe.get_all(
            "POS Profile User",
            filters={"parent": profile_name},
            fields=["user"],
            order_by="idx"
        )
        
        result = [u.user for u in users]
        return result
        
    except Exception as e:
        return []
