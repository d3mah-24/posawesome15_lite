# -*- coding: utf-8 -*-
"""
Update Customer API
Handles updating existing customer information with validation
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def update_customer(
    customer_id,
    customer_name=None,
    mobile_no=None,
    email_id=None,
    tax_id=None,
    birthday=None,
    gender=None,
    customer_group=None,
    territory=None,
    customer_type=None,
    discount_percentage=None,
    disabled=None,
    **kwargs
):
    """
    Update existing customer information with validation.
    
    Args:
        customer_id (str): Customer ID/name (required)
        customer_name (str): New customer name
        mobile_no (str): New mobile number
        email_id (str): New email address  
        tax_id (str): New tax ID
        birthday (str): New birthday
        gender (str): New gender
        customer_group (str): New customer group
        territory (str): New territory
        customer_type (str): New customer type
        discount_percentage (float): New discount percentage
        disabled (int): Disable/enable customer (0/1)
        **kwargs: Additional fields to update
        
    Returns:
        dict: Updated customer document
    """
    try:
        # Validate required parameters
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        # Check if customer exists
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer not found: {0}").format(customer_id))
        
        # Check permissions
        if not frappe.has_permission("Customer", "write", customer_id):
            frappe.throw(_("You don't have permission to update this customer"), frappe.PermissionError)
        
        # Get the customer document
        customer_doc = frappe.get_doc("Customer", customer_id)
        
        # Track what fields are being updated
        updated_fields = []
        
        # Update basic fields if provided
        if customer_name is not None and customer_name.strip():
            new_name = customer_name.strip()
            # Check for duplicate customer name (excluding current customer)
            existing = frappe.db.get_value("Customer", {"customer_name": new_name, "name": ["!=", customer_id]}, "name")
            if existing:
                frappe.throw(_("Customer with name '{0}' already exists: {1}").format(new_name, existing))
            customer_doc.customer_name = new_name
            updated_fields.append("customer_name")
        
        if mobile_no is not None:
            mobile_no = mobile_no.strip() if mobile_no else ""
            # Check for duplicate mobile (excluding current customer)
            if mobile_no:
                existing = frappe.db.get_value("Customer", {"mobile_no": mobile_no, "name": ["!=", customer_id]}, "name")
                if existing:
                    frappe.throw(_("Customer with mobile number '{0}' already exists: {1}").format(mobile_no, existing))
            customer_doc.mobile_no = mobile_no
            updated_fields.append("mobile_no")
        
        if email_id is not None:
            customer_doc.email_id = email_id.strip() if email_id else ""
            updated_fields.append("email_id")
        
        if tax_id is not None:
            customer_doc.tax_id = tax_id.strip() if tax_id else ""
            updated_fields.append("tax_id")
        
        if gender is not None and gender in ["Male", "Female", "Other", ""]:
            customer_doc.gender = gender
            updated_fields.append("gender")
        
        if customer_group is not None:
            # Validate customer group exists
            if customer_group and not frappe.db.exists("Customer Group", customer_group):
                frappe.throw(_("Customer Group '{0}' does not exist").format(customer_group))
            customer_doc.customer_group = customer_group
            updated_fields.append("customer_group")
        
        if territory is not None:
            # Validate territory exists
            if territory and not frappe.db.exists("Territory", territory):
                frappe.throw(_("Territory '{0}' does not exist").format(territory))
            customer_doc.territory = territory
            updated_fields.append("territory")
        
        if customer_type is not None:
            customer_doc.customer_type = customer_type
            updated_fields.append("customer_type")
        
        if disabled is not None:
            customer_doc.disabled = int(disabled) if disabled else 0
            updated_fields.append("disabled")
        
        # Handle POS-specific fields if they exist
        if birthday is not None and hasattr(customer_doc, 'posa_birthday'):
            from .create_customer import _parse_birthday
            formatted_birthday = _parse_birthday(birthday) if birthday else None
            customer_doc.posa_birthday = formatted_birthday
            updated_fields.append("posa_birthday")
        
        if discount_percentage is not None and hasattr(customer_doc, 'posa_discount'):
            try:
                customer_doc.posa_discount = float(discount_percentage) if discount_percentage else 0
                updated_fields.append("posa_discount")
            except (ValueError, TypeError):
                frappe.throw(_("Invalid discount percentage: {0}").format(discount_percentage))
        
        # Update any additional fields from kwargs
        for field_name, field_value in kwargs.items():
            if hasattr(customer_doc, field_name) and field_name not in ['name', 'doctype']:
                setattr(customer_doc, field_name, field_value)
                updated_fields.append(field_name)
        
        # Save the document if any fields were updated
        if updated_fields:
            customer_doc.save()
            frappe.logger().info(f"Updated customer {customer_id} - fields: {', '.join(updated_fields)}")
        else:
            frappe.logger().info(f"No fields updated for customer {customer_id}")
        
        # Return the updated customer document
        return customer_doc.as_dict()
        
    except Exception as e:
        frappe.logger().error(f"Error in update_customer: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        
        # Re-raise validation errors as-is
        if "already exists" in str(e) or "does not exist" in str(e) or "permission" in str(e).lower():
            raise
        else:
            frappe.throw(_("Error updating customer: {0}").format(str(e)))


@frappe.whitelist()
def patch_customer(customer_id, **kwargs):
    """
    Partial update of customer (PATCH method equivalent).
    Only updates the fields that are explicitly provided.
    
    Args:
        customer_id (str): Customer ID/name (required) 
        **kwargs: Fields to update
        
    Returns:
        dict: Updated customer document
    """
    try:
        # Filter out None values and empty strings for true partial update
        update_data = {k: v for k, v in kwargs.items() if v is not None and v != ""}
        
        if not update_data:
            frappe.throw(_("No fields provided to update"))
        
        return update_customer(customer_id, **update_data)
        
    except Exception as e:
        frappe.logger().error(f"Error in patch_customer: {str(e)}")
        raise