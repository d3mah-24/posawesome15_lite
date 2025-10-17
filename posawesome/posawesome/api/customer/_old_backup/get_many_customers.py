# -*- coding: utf-8 -*-
"""
Get Many Customers API  
Handles searching and retrieving multiple customers with filtering
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _


@frappe.whitelist()
def get_many_customers(search_term="", pos_profile=None, limit=50, offset=0, filters=None):
    """
    Search and retrieve multiple customers with advanced filtering.
    
    Args:
        search_term (str): Search query (name, mobile, email, or customer ID)
        pos_profile (str): POS Profile name or JSON string for filtering
        limit (int): Maximum number of results to return (default: 50)
        offset (int): Number of records to skip for pagination (default: 0)
        filters (str): Additional JSON filters to apply
        
    Returns:
        list: List of customer dictionaries with essential fields
    """
    try:
        frappe.logger().debug(f"get_many_customers called with search_term='{search_term}', limit={limit}")
        
        # Base filters
        query_filters = {"disabled": 0}
        
        # Parse additional filters if provided
        if filters:
            try:
                additional_filters = frappe.parse_json(filters)
                query_filters.update(additional_filters)
            except Exception as filter_error:
                frappe.logger().warning(f"Could not parse additional filters: {filter_error}")
        
        # Apply POS Profile filtering
        if pos_profile:
            try:
                # Handle both POS Profile name and JSON data
                if isinstance(pos_profile, str) and not pos_profile.startswith('{'):
                    # It's a POS Profile name - get the document
                    profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
                    if hasattr(profile_doc, 'customer_group') and profile_doc.customer_group:
                        query_filters["customer_group"] = profile_doc.customer_group
                        frappe.logger().debug(f"Filtering by customer_group: {profile_doc.customer_group}")
                else:
                    # It's JSON data - parse customer groups
                    pos_profile_data = frappe.parse_json(pos_profile)
                    if pos_profile_data.get("customer_groups"):
                        customer_groups = []
                        for cg_data in pos_profile_data.get("customer_groups", []):
                            if cg_data.get("customer_group"):
                                customer_groups.append(cg_data.get("customer_group"))
                        
                        if customer_groups:
                            query_filters["customer_group"] = ["in", customer_groups]
                            frappe.logger().debug(f"Filtering by customer_groups: {customer_groups}")
            except Exception as profile_error:
                frappe.logger().warning(f"Could not process pos_profile: {profile_error}")
        
        # Add search term filtering (server-side)
        if search_term and search_term.strip():
            search_term = search_term.strip()
            # Search in multiple fields with OR condition
            query_filters.update({
                "or": [
                    {"customer_name": ["like", f"%{search_term}%"]},
                    {"mobile_no": ["like", f"%{search_term}%"]},
                    {"email_id": ["like", f"%{search_term}%"]},
                    {"name": ["like", f"%{search_term}%"]},
                    {"tax_id": ["like", f"%{search_term}%"]}
                ]
            })
            frappe.logger().debug(f"Server-side search for: '{search_term}'")
        
        # Execute the query with ORM for safety
        customers = frappe.get_all(
            "Customer",
            filters=query_filters,
            fields=[
                "name",
                "customer_name", 
                "mobile_no",
                "email_id",
                "tax_id",
                "customer_group",
                "territory",
                "customer_type",
                "default_price_list",
                "image",
                "disabled",
                "creation",
                "modified"
            ],
            limit_page_length=limit,
            limit_start=offset,
            order_by="customer_name asc"
        )
        
        frappe.logger().debug(f"get_many_customers returned {len(customers)} customers")
        return customers
        
    except Exception as e:
        frappe.logger().error(f"Error in get_many_customers: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error searching customers: {0}").format(str(e)))


@frappe.whitelist() 
def get_customers_count(search_term="", pos_profile=None, filters=None):
    """
    Get total count of customers matching the search criteria (for pagination).
    
    Args:
        search_term (str): Search query
        pos_profile (str): POS Profile for filtering
        filters (str): Additional JSON filters
        
    Returns:
        int: Total number of matching customers
    """
    try:
        # Use same filtering logic as get_many_customers but only count
        query_filters = {"disabled": 0}
        
        # Parse additional filters
        if filters:
            try:
                additional_filters = frappe.parse_json(filters)
                query_filters.update(additional_filters)
            except:
                pass
        
        # Apply POS Profile filtering
        if pos_profile:
            try:
                if isinstance(pos_profile, str) and not pos_profile.startswith('{'):
                    profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
                    if hasattr(profile_doc, 'customer_group') and profile_doc.customer_group:
                        query_filters["customer_group"] = profile_doc.customer_group
                else:
                    pos_profile_data = frappe.parse_json(pos_profile)
                    if pos_profile_data.get("customer_groups"):
                        customer_groups = [cg.get("customer_group") for cg in pos_profile_data.get("customer_groups", [])]
                        if customer_groups:
                            query_filters["customer_group"] = ["in", customer_groups]
            except:
                pass
        
        # Add search filtering
        if search_term and search_term.strip():
            search_term = search_term.strip()
            query_filters.update({
                "or": [
                    {"customer_name": ["like", f"%{search_term}%"]},
                    {"mobile_no": ["like", f"%{search_term}%"]},
                    {"email_id": ["like", f"%{search_term}%"]},
                    {"name": ["like", f"%{search_term}%"]},
                    {"tax_id": ["like", f"%{search_term}%"]}
                ]
            })
        
        count = frappe.db.count("Customer", filters=query_filters)
        return count
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customers_count: {str(e)}")
        return 0