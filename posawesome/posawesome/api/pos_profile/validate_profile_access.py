# -*- coding: utf-8 -*-
"""
Validate Profile Access Function
Handles validating if user has access to POS Profile
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def validate_profile_access(profile_name, user):
    """
    POST - Validate if user has access to POS Profile
    """
    try:
        # Check if user is assigned to this profile
        user_exists = frappe.db.exists("POS Profile User", {
            "parent": profile_name,
            "user": user
        })
        
        if not user_exists:
            return {
                "success": False,
                "message": f"User {user} is not assigned to POS Profile {profile_name}"
            }
        
        # Check if profile is enabled
        profile_enabled = frappe.get_cached_value("POS Profile", profile_name, "disabled")
        
        if profile_enabled:
            return {
                "success": False,
                "message": f"POS Profile {profile_name} is disabled"
            }
        
        result = {
            "success": True,
            "message": "Access granted"
        }
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error validating access: {str(e)}"
        }
