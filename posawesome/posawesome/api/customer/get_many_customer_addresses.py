# -*- coding: utf-8 -*-
"""
Get Many Customer Addresses API
Handles retrieving multiple customer addresses
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_many_customer_addresses(customer):
    """
    Get all addresses for a customer.
    
    Args:
        customer (str): Customer name/ID
        
    Returns:
        list: List of address documents
    """
    try:
        if not customer:
            frappe.throw(_("Customer is required"))
            
        # Get all address links for this customer
        address_links = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": customer,
                "parenttype": "Address"
            },
            fields=["parent"]
        )
        
        if not address_links:
            return []
            
        addresses = []
        for link in address_links:
            try:
                address = frappe.get_doc("Address", link.parent)
                addresses.append(address.as_dict())
            except Exception:
                continue  # Skip if address doesn't exist
                
        return addresses
        
    except Exception as e:
        frappe.logger().error(f"Error in get_many_customer_addresses: {str(e)}")
        frappe.throw(_("Error retrieving addresses: {0}").format(str(e)))