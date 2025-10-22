# -*- coding: utf-8 -*-
"""
Get Single Customer API
Handles retrieving detailed information for a single customer
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_customer(customer_id):
    """
    Get detailed customer information by ID.
    
    Args:
        customer_id (str): Customer ID or name
        
    Returns:
        dict: Customer details including loyalty points, addresses, etc.
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
            
        # Check if customer exists
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer not found"))
            
        customer_doc = frappe.get_cached_doc("Customer", customer_id)
        
        result = {
            # Basic customer info
            "name": customer_doc.name,
            "customer_name": customer_doc.customer_name,
            "customer_type": customer_doc.customer_type,
            "customer_group": customer_doc.customer_group,
            "territory": customer_doc.territory,
            
            # Contact details
            "email_id": customer_doc.email_id,
            "mobile_no": customer_doc.mobile_no,
            "tax_id": customer_doc.tax_id,
            
            # POS specific fields
            "image": customer_doc.image,
            "gender": customer_doc.gender,
            "birthday": getattr(customer_doc, 'posa_birthday', None),
            "posa_discount": getattr(customer_doc, 'posa_discount', 0),
            
            # Business fields - maintaining backward compatibility
            "default_price_list": customer_doc.default_price_list,
            "customer_price_list": customer_doc.default_price_list,  # Legacy compatibility
            "loyalty_program": customer_doc.loyalty_program,
            "disabled": customer_doc.disabled,
            
            # Calculated fields
            "loyalty_points": None,
            "customer_group_price_list": None,
        }
        
        # Get customer group price list
        if customer_doc.customer_group:
            result["customer_group_price_list"] = frappe.get_cached_value(
                "Customer Group", 
                customer_doc.customer_group, 
                "default_price_list"
            )
        
        # Get loyalty program details
        if customer_doc.loyalty_program:
            try:
                from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
                    get_loyalty_program_details_with_points
                )
                lp_details = get_loyalty_program_details_with_points(
                    customer_doc.name,
                    customer_doc.loyalty_program,
                    silent=True,
                    include_expired_entry=False,
                )
                result["loyalty_points"] = lp_details.get("loyalty_points", 0)
            except Exception as loyalty_error:
                # Silent fallback for loyalty details
                result["loyalty_points"] = 0
        
        return result
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error retrieving customer information: {0}").format(str(e)))