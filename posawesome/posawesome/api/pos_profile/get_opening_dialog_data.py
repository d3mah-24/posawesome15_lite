# -*- coding: utf-8 -*-
"""
Get Opening Dialog Data Function
Handles getting opening dialog data
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_opening_dialog_data():
    """
    GET - Get opening dialog data
    """
    try:
        data = {}
        data["companies"] = frappe.get_list("Company", limit_page_length=0, order_by="name")
        
        data["pos_profiles_data"] = frappe.get_list(
            "POS Profile",
            filters={"disabled": 0},
            fields=["name", "company", "currency"],
            limit_page_length=0,
            order_by="name",
        )

        pos_profiles_list = []
        for i in data["pos_profiles_data"]:
            pos_profiles_list.append(i.name)

        payment_method_table = "POS Payment Method"
        data["payments_method"] = frappe.get_list(
            payment_method_table,
            filters={"parent": ["in", pos_profiles_list]},
            fields=["default", "mode_of_payment", "allow_in_returns","parent"],
            limit_page_length=0,
            order_by="parent, idx",
            ignore_permissions=True,
        )
        
        # Set currency from pos profile
        for mode in data["payments_method"]:
            mode["currency"] = frappe.get_cached_value(
                "POS Profile", mode["parent"], "currency"
            )

        return data
        
    except Exception as e:
        return {}
        
