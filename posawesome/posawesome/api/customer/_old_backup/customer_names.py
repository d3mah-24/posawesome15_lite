# -*- coding: utf-8 -*-
"""
Customer Names Functions (POSNext Style)
Handles customer search, creation, and management for POS operations
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _


@frappe.whitelist()
def get_customer_names(pos_profile, search_term="", limit=50):
    """
    Search customers for inline customer selection in POS (POSNext Style).

    Args:
        pos_profile (str): JSON string of POS Profile configuration
        search_term (str): Search query (name, mobile, or customer ID)
        limit (int): Maximum number of results to return

    Returns:
        list: List of customer dictionaries with name, customer_name, mobile_no, email_id
    """
    try:
        frappe.logger().debug(f"get_customer_names called with search_term={search_term}, limit={limit}")
        
        # Parse pos_profile safely
        pos_profile_data = frappe.parse_json(pos_profile) if isinstance(pos_profile, str) else pos_profile
        
        filters = {"disabled": 0}
        
        # Filter by POS Profile customer groups if specified
        if pos_profile_data and pos_profile_data.get("customer_groups"):
            customer_groups = []
            for cg_data in pos_profile_data.get("customer_groups", []):
                if cg_data.get("customer_group"):
                    customer_groups.append(cg_data.get("customer_group"))
            
            if customer_groups:
                filters["customer_group"] = ["in", customer_groups]
                frappe.logger().debug(f"Filtering by customer_groups: {customer_groups}")
        
        # Add server-side search filtering if search_term provided
        if search_term and search_term.strip():
            search_term = search_term.strip()
            filters.update({
                "or": [
                    {"customer_name": ["like", f"%{search_term}%"]},
                    {"mobile_no": ["like", f"%{search_term}%"]},
                    {"name": ["like", f"%{search_term}%"]}
                ]
            })
            frappe.logger().debug(f"Server-side search for: {search_term}")
        
        # Use secure ORM instead of raw SQL
        customers = frappe.get_all(
            "Customer",
            filters=filters,
            fields=["name", "customer_name", "mobile_no", "email_id"],
            limit=limit,
            order_by="customer_name asc"
        )
        
        frappe.logger().debug(f"get_customer_names returned {len(customers)} customers")
        return customers
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_names: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error fetching customers: {0}").format(str(e)))


@frappe.whitelist()
def get_customers(search_term="", pos_profile=None, limit=50):
    """
    Modern POSNext-style customer search API.
    
    Args:
        search_term (str): Search query (name, mobile, or customer ID)
        pos_profile (str): POS Profile name or JSON string
        limit (int): Maximum number of results to return

    Returns:
        list: List of customer dictionaries with name, customer_name, mobile_no, email_id
    """
    try:
        frappe.logger().debug(f"get_customers called with search_term={search_term}, pos_profile={pos_profile}, limit={limit}")

        filters = {"disabled": 0}

        # Filter by POS Profile customer group if specified
        if pos_profile:
            try:
                # Handle both POS Profile name and JSON data
                if isinstance(pos_profile, str) and not pos_profile.startswith('{'):
                    # It's a POS Profile name
                    profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
                    if hasattr(profile_doc, 'customer_group') and profile_doc.customer_group:
                        filters["customer_group"] = profile_doc.customer_group
                        frappe.logger().debug(f"Filtering by customer_group: {profile_doc.customer_group}")
                else:
                    # It's JSON data, parse it
                    pos_profile_data = frappe.parse_json(pos_profile)
                    if pos_profile_data.get("customer_groups"):
                        customer_groups = [cg.get("customer_group") for cg in pos_profile_data.get("customer_groups", [])]
                        if customer_groups:
                            filters["customer_group"] = ["in", customer_groups]
                            frappe.logger().debug(f"Filtering by customer_groups: {customer_groups}")
            except Exception as profile_error:
                frappe.logger().warning(f"Could not process pos_profile: {profile_error}")

        # Add server-side search filtering
        if search_term and search_term.strip():
            search_term = search_term.strip()
            filters.update({
                "or": [
                    {"customer_name": ["like", f"%{search_term}%"]},
                    {"mobile_no": ["like", f"%{search_term}%"]},
                    {"name": ["like", f"%{search_term}%"]}
                ]
            })
            frappe.logger().debug(f"Server-side search for: {search_term}")

        # Use secure ORM query
        result = frappe.get_all(
            "Customer",
            filters=filters,
            fields=["name", "customer_name", "mobile_no", "email_id"],
            limit=limit,
            order_by="customer_name asc"
        )
        
        frappe.logger().debug(f"get_customers returned {len(result)} customers")
        return result
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customers: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error fetching customers: {0}").format(str(e)))


@frappe.whitelist()
def create_customer(customer_name, mobile_no=None, email_id=None, customer_group="Individual", territory="All Territories"):
    """
    Create a new customer from POS (POSNext Style).

    Args:
        customer_name (str): Customer name (required)
        mobile_no (str): Mobile number (optional)
        email_id (str): Email address (optional)
        customer_group (str): Customer group (default: Individual)
        territory (str): Territory (default: All Territories)

    Returns:
        dict: Created customer document
    """
    # Check if user has permission to create customers
    if not frappe.has_permission("Customer", "create"):
        frappe.throw(_("You don't have permission to create customers"), frappe.PermissionError)

    if not customer_name:
        frappe.throw(_("Customer name is required"))

    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": customer_name,
        "customer_type": "Individual",
        "customer_group": customer_group or "Individual",
        "territory": territory or "All Territories",
        "mobile_no": mobile_no or "",
        "email_id": email_id or "",
    })

    customer.insert()
    return customer.as_dict()


@frappe.whitelist()
def get_customer_details(customer):
    """
    Get detailed customer information (POSNext Style).

    Args:
        customer (str): Customer ID

    Returns:
        dict: Customer details
    """
    if not customer:
        frappe.throw(_("Customer is required"))

    return frappe.get_cached_doc("Customer", customer).as_dict()
