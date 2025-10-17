# -*- coding: utf-8 -*-
"""
Get Primary Customer Address API
Handles retrieving customer's primary address
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_primary_customer_address(customer):
    """
    Get primary address for a customer.
    
    Args:
        customer (str): Customer name/ID
        
    Returns:
        dict: Primary address document or None
    """
    try:
        if not customer:
            frappe.throw(_("Customer is required"))
            
        # Get customer document to check for primary address
        customer_doc = frappe.get_doc("Customer", customer)
        
        if customer_doc.customer_primary_address:
            address = frappe.get_doc("Address", customer_doc.customer_primary_address)
            return address.as_dict()
            
        # If no primary address set, get first available address
        address_links = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": customer,
                "parenttype": "Address"
            },
            fields=["parent"],
            limit=1
        )
        
        if address_links:
            address = frappe.get_doc("Address", address_links[0].parent)
            return address.as_dict()
            
        return None
        
    except Exception as e:
        frappe.logger().error(f"Error in get_primary_customer_address: {str(e)}")
        frappe.throw(_("Error retrieving primary address: {0}").format(str(e)))