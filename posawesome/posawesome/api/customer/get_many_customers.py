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
def get_many_customers(pos_profile=None, search_term=None, limit=50, offset=0):
    """
    Get multiple customers with advanced filtering and server-side search.
    Optimized replacement for legacy get_customer_names function.
    Implements Backend Improvement Policy: ORM-only, field optimization, Redis caching.
    
    Args:
        pos_profile (str): POS Profile name for filtering (optional)
        search_term (str): Search query for customer_name, mobile, email, etc. (optional)
        limit (int): Maximum number of results (default: 50)
        offset (int): Number of records to skip for pagination (default: 0)
        
    Returns:
        list: List of customer dictionaries with optimized fields
    """
    try:
        # Log incoming request
        frappe.log_error(f"[get_many_customers.py][get_many_customers] START - pos_profile: {pos_profile}, search_term: '{search_term}', limit: {limit}")
        
        # Convert limit and offset to integers for safety
        limit = min(int(limit or 50), 200)  # Cap at 200 for performance
        offset = int(offset or 0)
        
        frappe.log_error(f"[get_many_customers.py][get_many_customers] Processed params - limit: {limit}, offset: {offset}")
        
        # Redis caching for POS Profile data (Backend Improvement Policy)
        cache_key = None
        if pos_profile and not search_term:
            cache_key = f"pos_customers_{pos_profile}_{limit}_{offset}"
            cached_result = frappe.cache().get_value(cache_key)
            if cached_result:
                return cached_result
        
        # Base query filters
        query_filters = {
            "disabled": 0  # Only active customers
        }
        
        frappe.log_error(f"[get_many_customers.py][get_many_customers] Base filters: {query_filters}")
        
        # Additional filters can be added here if needed in future
        # For now, we only use the base filters and pos_profile filtering
        
        # Apply POS Profile filtering
        if pos_profile:
            try:
                frappe.log_error(f"[get_many_customers.py][get_many_customers] Applying POS profile filter: {pos_profile}")
                # Handle both POS Profile name and JSON data
                if isinstance(pos_profile, str) and not pos_profile.startswith('{'):
                    # It's a POS Profile name - get the document
                    profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
                    if hasattr(profile_doc, 'customer_group') and profile_doc.customer_group:
                        query_filters["customer_group"] = profile_doc.customer_group
                        frappe.log_error(f"[get_many_customers.py][get_many_customers] Added customer_group filter: {profile_doc.customer_group}")
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
                            frappe.log_error(f"[get_many_customers.py][get_many_customers] Added customer_groups filter: {customer_groups}")
            except Exception as profile_error:
                # Silent fallback for POS profile processing
                frappe.log_error(f"[get_many_customers.py][get_many_customers] POS profile filter error: {str(profile_error)}")
                pass
        
        frappe.log_error(f"[get_many_customers.py][get_many_customers] Final query filters: {query_filters}")
        
        # Add search term filtering (POSNext ORM-only approach)
        search_filters = []
        if search_term and search_term.strip():
            search_term = search_term.strip()
            frappe.log_error(f"[get_many_customers.py][get_many_customers] Search term provided: '{search_term}'")
            # Priority-based search fields (most important first)
            search_filters = [
                ["customer_name", "like", f"%{search_term}%"],   # Primary search field
                ["name", "like", f"%{search_term}%"],           # Customer ID search  
                ["mobile_no", "like", f"%{search_term}%"],      # Mobile number search
                ["email_id", "like", f"%{search_term}%"],       # Email search
                ["tax_id", "like", f"%{search_term}%"]          # Tax ID search
            ]
            frappe.log_error(f"[get_many_customers.py][get_many_customers] Search filters: {search_filters}")
        else:
            frappe.log_error(f"[get_many_customers.py][get_many_customers] No search term, loading all customers")
        
        # Use Frappe ORM with optimized field selection (Backend Policy Compliance)
        fields_to_fetch = [
            "name", "customer_name", "mobile_no", "email_id", "tax_id",
            "customer_group", "territory", "disabled"
        ]
        
        frappe.log_error(f"[get_many_customers.py][get_many_customers] Fields to fetch: {fields_to_fetch}")
        
        # Handle search term with ORM-only approach (POSNext style)
        if search_filters:
            # Use proper OR filters for efficient search across multiple fields
            frappe.log_error(f"[get_many_customers.py][get_many_customers] Building OR filters for search")
            
            # Convert search filters to proper OR format
            or_filters = []
            for field_name, operator, value in search_filters:
                or_filters.append([field_name, operator.lower(), value])
            
            # Add OR filters to base query
            search_query_filters = {
                **query_filters,
                "or": or_filters
            }
            
            frappe.log_error(f"[get_many_customers.py][get_many_customers] Final search query: {search_query_filters}")
            
            customers = frappe.get_all(
                "Customer",
                filters=search_query_filters,
                fields=fields_to_fetch,
                limit=limit,
                start=offset,
                order_by="customer_name asc"
            )
            
            frappe.log_error(f"[get_many_customers.py][get_many_customers] OR search returned {len(customers)} customers")
        else:
            # Simple query without search terms
            frappe.log_error(f"[get_many_customers.py][get_many_customers] Executing simple query with filters: {query_filters}")
            customers = frappe.get_all(
                "Customer",
                filters=query_filters,
                fields=fields_to_fetch,
                limit=limit,
                start=offset,
                order_by="customer_name asc"
            )
            frappe.log_error(f"[get_many_customers.py][get_many_customers] Simple query returned {len(customers)} customers")
        
        # Cache results for better performance (Backend Improvement Policy)
        if cache_key and customers:
            frappe.cache().set_value(cache_key, customers, expires_in_sec=300)  # 5-minute cache
            frappe.log_error(f"[get_many_customers.py][get_many_customers] Cached {len(customers)} customers")
        
        frappe.log_error(f"[get_many_customers.py][get_many_customers] SUCCESS - Returning {len(customers)} customers")
        if customers:
            frappe.log_error(f"[get_many_customers.py][get_many_customers] Sample customer: {customers[0]}")
        
        return customers
        
    except Exception as e:
        frappe.log_error(f"[get_many_customers.py][get_many_customers] ERROR: {str(e)}")
        frappe.log_error(frappe.get_traceback())
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
        frappe.log_error(f"[get_many_customers.py][get_customers_count] Error: {str(e)}")
        return 0