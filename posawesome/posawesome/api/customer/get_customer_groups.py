# -*- coding: utf-8 -*-
"""
Customer Groups API
Handles customer group operations and filtering for POS profiles
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_customer_groups(pos_profile=None):
    """
    Get customer groups based on POS Profile configuration.
    
    Args:
        pos_profile (str or dict): POS Profile name or JSON data
        
    Returns:
        list: List of customer group names
    """
    try:
        customer_groups = []
        
        if pos_profile:
            # Parse pos_profile if it's a string
            if isinstance(pos_profile, str):
                if pos_profile.startswith('{'):
                    pos_profile_data = frappe.parse_json(pos_profile)
                else:
                    # It's a POS Profile name
                    pos_profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
                    pos_profile_data = pos_profile_doc.as_dict()
            else:
                pos_profile_data = pos_profile
            
            # Get customer groups from POS profile
            if pos_profile_data.get("customer_groups"):
                for cg_data in pos_profile_data.get("customer_groups", []):
                    if cg_data.get("customer_group"):
                        # Get child nodes for hierarchical customer groups
                        child_groups = get_child_customer_groups(cg_data.get("customer_group"))
                        customer_groups.extend(child_groups)
        
        # Remove duplicates and return
        result = list(set(customer_groups))
        return result
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_groups: {str(e)}")
        return []


def get_child_customer_groups(parent_group):
    """
    Get all child customer groups for a parent group (hierarchical).
    
    Args:
        parent_group (str): Parent customer group name
        
    Returns:
        list: List of customer group names including parent and all children
    """
    try:
        if not parent_group:
            return []
            
        # Start with the parent group
        groups = [parent_group]
        
        # Get all child groups recursively
        child_groups = frappe.get_all(
            "Customer Group",
            filters={"parent_customer_group": parent_group, "disabled": 0},
            fields=["name"]
        )
        
        for child in child_groups:
            # Recursively get children of children
            nested_children = get_child_customer_groups(child.name)
            groups.extend(nested_children)
        
        return list(set(groups))  # Remove duplicates
        
    except Exception as e:
        frappe.logger().warning(f"Error getting child customer groups: {e}")
        return [parent_group] if parent_group else []


def get_customer_group_condition(pos_profile=None):
    """
    Generate SQL condition for customer group filtering.
    
    Args:
        pos_profile (str or dict): POS Profile name or JSON data
        
    Returns:
        str: SQL WHERE condition for customer groups
    """
    try:
        base_condition = "disabled = 0"
        
        customer_groups = get_customer_groups(pos_profile)
        
        if customer_groups:
            # Escape group names for SQL safety
            escaped_groups = [frappe.db.escape(group) for group in customer_groups]
            group_condition = f"customer_group IN ({', '.join(escaped_groups)})"
            return f"{base_condition} AND {group_condition}"
        
        return base_condition
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_group_condition: {e}")
        return "disabled = 0"


@frappe.whitelist()
def get_customer_groups_list(search_term="", limit=50):
    """
    Get list of customer groups for selection/autocomplete.
    
    Args:
        search_term (str): Search term to filter groups
        limit (int): Maximum number of results
        
    Returns:
        list: List of customer group dictionaries
    """
    try:
        filters = {"disabled": 0}
        
        if search_term and search_term.strip():
            filters["name"] = ["like", f"%{search_term.strip()}%"]
        
        groups = frappe.get_all(
            "Customer Group",
            filters=filters,
            fields=["name", "customer_group_name", "parent_customer_group"],
            limit=limit,
            order_by="name asc"
        )
        
        return groups
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_groups_list: {str(e)}")
        return []