# -*- coding: utf-8 -*-
"""
Set Customer Info Functions
Handles setting customer information
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def set_customer_info(customer, fieldname, value=""):
    # Handle loyalty program separately (Customer only)
    if fieldname == "loyalty_program":
        frappe.db.set_value("Customer", customer, "loyalty_program", value)
        return

    # Get primary contact ID from Customer
    contact = (
        frappe.get_cached_value("Customer", customer, "customer_primary_contact") or ""
    )

    # Case 1: Contact exists - update existing contact
    if contact:
        contact_doc = frappe.get_doc("Contact", contact)
        
        # Update email in both Contact and Customer
        if fieldname == "email_id":
            contact_doc.set("email_ids", [{"email_id": value, "is_primary": 1}])
            frappe.db.set_value("Customer", customer, "email_id", value)
        
        # Update mobile in both Contact and Customer
        elif fieldname == "mobile_no":
            contact_doc.set("phone_nos", [{"phone": value, "is_primary_mobile_no": 1}])
            frappe.db.set_value("Customer", customer, "mobile_no", value)
        
        # Update gender in both Contact and Customer
        elif fieldname == "gender":
            contact_doc.gender = value
            frappe.db.set_value("Customer", customer, "gender", value)
        
        contact_doc.save()

    # Case 2: No contact exists - create new contact
    else:
        contact_doc = frappe.new_doc("Contact")
        contact_doc.first_name = customer
        contact_doc.is_primary_contact = 1
        contact_doc.is_billing_contact = 1
        
        # Add mobile number to new contact
        if fieldname == "mobile_no":
            contact_doc.add_phone(value, is_primary_mobile_no=1, is_primary_phone=1)

        # Add email to new contact
        if fieldname == "email_id":
            contact_doc.add_email(value, is_primary=1)
            
        # Add gender to new contact
        if fieldname == "gender":
            contact_doc.gender = value

        # Link contact to customer
        contact_doc.append("links", {"link_doctype": "Customer", "link_name": customer})

        # Save new contact and update customer reference
        contact_doc.flags.ignore_mandatory = True
        contact_doc.save()
        frappe.set_value(
            "Customer", customer, "customer_primary_contact", contact_doc.name
        )
