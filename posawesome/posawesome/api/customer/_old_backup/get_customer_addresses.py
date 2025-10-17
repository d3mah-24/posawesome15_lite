# -*- coding: utf-8 -*-
"""
Get Customer Addresses API
Handles retrieving customer address information
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_customer_addresses(customer_id, address_type=None):
    """
    Get all addresses linked to a customer.
    
    Args:
        customer_id (str): Customer ID/name (required)
        address_type (str): Filter by specific address type (optional)
        
    Returns:
        list: List of address dictionaries
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer not found: {0}").format(customer_id))
        
        # Build filters
        filters = {
            "link_doctype": "Customer",
            "link_name": customer_id,
            "disabled": 0
        }
        
        if address_type:
            filters["address_type"] = address_type
        
        # Get addresses
        addresses = frappe.get_all(
            "Address",
            filters=filters,
            fields=[
                "name",
                "address_title",
                "address_type", 
                "address_line1",
                "address_line2",
                "city",
                "county",
                "state",
                "country",
                "pincode",
                "phone",
                "fax",
                "email_id",
                "is_primary_address",
                "is_shipping_address",
                "disabled"
            ],
            order_by="is_primary_address desc, creation desc"
        )
        
        # Format addresses for better presentation
        formatted_addresses = []
        for addr in addresses:
            # Build formatted address string
            address_parts = [addr.address_line1]
            if addr.address_line2:
                address_parts.append(addr.address_line2)
            if addr.city:
                address_parts.append(addr.city)
            if addr.state:
                address_parts.append(addr.state)
            if addr.country:
                address_parts.append(addr.country)
            if addr.pincode:
                address_parts.append(addr.pincode)
            
            formatted_address = ", ".join(filter(None, address_parts))
            
            formatted_addresses.append({
                "name": addr.name,
                "title": addr.address_title,
                "type": addr.address_type,
                "address_line1": addr.address_line1,
                "address_line2": addr.address_line2,
                "city": addr.city,
                "county": addr.county,
                "state": addr.state,
                "country": addr.country,
                "pincode": addr.pincode,
                "phone": addr.phone,
                "fax": addr.fax,
                "email_id": addr.email_id,
                "is_primary": addr.is_primary_address,
                "is_shipping": addr.is_shipping_address,
                "formatted_address": formatted_address,
                "disabled": addr.disabled
            })
        
        frappe.logger().debug(f"Found {len(formatted_addresses)} addresses for customer {customer_id}")
        
        return formatted_addresses
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_addresses: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error retrieving customer addresses: {0}").format(str(e)))


@frappe.whitelist()
def get_customer_primary_address(customer_id):
    """
    Get the primary address for a customer.
    
    Args:
        customer_id (str): Customer ID/name (required)
        
    Returns:
        dict: Primary address details or None if not found
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        addresses = get_customer_addresses(customer_id)
        
        # Find primary address
        primary_address = None
        for addr in addresses:
            if addr["is_primary"]:
                primary_address = addr
                break
        
        # If no primary address, return the first address
        if not primary_address and addresses:
            primary_address = addresses[0]
        
        return primary_address
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_primary_address: {str(e)}")
        frappe.throw(_("Error retrieving primary address: {0}").format(str(e)))


@frappe.whitelist()
def get_customer_shipping_addresses(customer_id):
    """
    Get all shipping addresses for a customer.
    
    Args:
        customer_id (str): Customer ID/name (required)
        
    Returns:
        list: List of shipping addresses
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        addresses = get_customer_addresses(customer_id)
        
        # Filter for shipping addresses
        shipping_addresses = [addr for addr in addresses if addr["is_shipping"] or addr["type"] == "Shipping"]
        
        return shipping_addresses
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_shipping_addresses: {str(e)}")
        frappe.throw(_("Error retrieving shipping addresses: {0}").format(str(e)))