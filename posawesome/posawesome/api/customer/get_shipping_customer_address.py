# -*- coding: utf-8 -*-
"""
Get Shipping Customer Address API
Handles retrieving customer's shipping address
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_shipping_customer_address(customer):
    """
    Get shipping address for a customer.
    
    Args:
        customer (str): Customer name/ID
        
    Returns:
        dict: Shipping address document or None
    """
    try:
        if not customer:
            frappe.throw(_("Customer is required"))
            
        # Get customer document to check for shipping address
        customer_doc = frappe.get_doc("Customer", customer)
        
        if customer_doc.customer_primary_contact:
            address = frappe.get_doc("Address", customer_doc.customer_primary_contact)
            return address.as_dict()
            
        # Look for shipping type address
        shipping_addresses = frappe.get_all(
            "Address",
            filters={
                "address_type": "Shipping"
            },
            fields=["name"]
        )
        
        for addr in shipping_addresses:
            # Check if this address is linked to our customer
            links = frappe.get_all(
                "Dynamic Link",
                filters={
                    "parent": addr.name,
                    "link_doctype": "Customer", 
                    "link_name": customer
                }
            )
            if links:
                address = frappe.get_doc("Address", addr.name)
                return address.as_dict()
                
        return None
        
    except Exception as e:
        frappe.logger().error(f"Error in get_shipping_customer_address: {str(e)}")
        frappe.throw(_("Error retrieving shipping address: {0}").format(str(e)))