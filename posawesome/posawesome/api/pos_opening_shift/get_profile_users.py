# -*- coding: utf-8 -*-
# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_profile_users(doctype, txt, searchfield, start, page_len, filters):
    """
    GET - Retrieve users registered in POS Profile
    """
    try:
        pos_profile = filters.get("parent")

        # Use frappe.get_all instead of direct SQL
        users = frappe.get_all(
            "POS Profile User",
            filters={
                "parent": pos_profile,
                "user": ["like", f"%{txt}%"]
            },
            fields=["user"],
            order_by="user",
            limit_start=start,
            limit_page_length=page_len
        )

        # Convert result to required format
        result = [[user.user] for user in users]
        
        frappe.log_error(f"[get_profile_users.py][get_profile_users] Retrieved {len(result)} users for profile: {pos_profile}")
        return result
        
    except Exception as e:
        frappe.log_error(f"[get_profile_users.py][get_profile_users] Error: {str(e)}")
        frappe.throw(f"Error retrieving profile users: {str(e)}")
