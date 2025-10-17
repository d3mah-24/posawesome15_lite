# -*- coding: utf-8 -*-
"""
Delete Customer API
Handles customer deletion with proper validation and cleanup
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def delete_customer(customer_id, force=False):
    """
    Delete a customer with proper validation and dependency checks.
    
    Args:
        customer_id (str): Customer ID/name to delete (required)
        force (bool): Force deletion even if there are linked documents (default: False)
        
    Returns:
        dict: Deletion status and information
    """
    try:
        # Validate required parameters
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        # Check if customer exists
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer not found: {0}").format(customer_id))
        
        # Check permissions
        if not frappe.has_permission("Customer", "delete", customer_id):
            frappe.throw(_("You don't have permission to delete this customer"), frappe.PermissionError)
        
        customer_doc = frappe.get_doc("Customer", customer_id)
        customer_name = customer_doc.customer_name
        
        # Check for linked documents before deletion (unless force=True)
        if not force:
            linked_docs = _check_customer_dependencies(customer_id)
            if linked_docs:
                linked_info = []
                for doctype, count in linked_docs.items():
                    if count > 0:
                        linked_info.append(f"{doctype}: {count}")
                
                if linked_info:
                    frappe.throw(_(
                        "Cannot delete customer '{0}' because it has linked documents: {1}. "
                        "Use force=True to delete anyway."
                    ).format(customer_name, ", ".join(linked_info)))
        
        # Perform the deletion
        try:
            customer_doc.delete()
            
            frappe.logger().info(f"Successfully deleted customer: {customer_id} - {customer_name}")
            
            return {
                "success": True,
                "message": _("Customer '{0}' deleted successfully").format(customer_name),
                "deleted_customer": {
                    "id": customer_id,
                    "name": customer_name
                }
            }
            
        except frappe.LinkExistsError as link_error:
            # Handle case where ERPNext prevents deletion due to links
            frappe.throw(_(
                "Cannot delete customer '{0}' because it is referenced in other documents. "
                "Details: {1}"
            ).format(customer_name, str(link_error)))
        
    except Exception as e:
        frappe.logger().error(f"Error in delete_customer: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        
        # Re-raise permission and validation errors as-is
        if "permission" in str(e).lower() or "not found" in str(e).lower() or "Cannot delete" in str(e):
            raise
        else:
            frappe.throw(_("Error deleting customer: {0}").format(str(e)))


@frappe.whitelist()
def soft_delete_customer(customer_id, reason=""):
    """
    Soft delete a customer by disabling it instead of permanent deletion.
    
    Args:
        customer_id (str): Customer ID/name to disable
        reason (str): Reason for disabling the customer
        
    Returns:
        dict: Status of the soft deletion
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer not found: {0}").format(customer_id))
        
        # Check permissions
        if not frappe.has_permission("Customer", "write", customer_id):
            frappe.throw(_("You don't have permission to disable this customer"), frappe.PermissionError)
        
        customer_doc = frappe.get_doc("Customer", customer_id)
        customer_name = customer_doc.customer_name
        
        # Disable the customer
        customer_doc.disabled = 1
        
        # Add reason to a custom field if it exists
        if reason and hasattr(customer_doc, 'posa_disable_reason'):
            customer_doc.posa_disable_reason = reason
        
        customer_doc.save()
        
        frappe.logger().info(f"Soft deleted (disabled) customer: {customer_id} - {customer_name}")
        
        return {
            "success": True,
            "message": _("Customer '{0}' disabled successfully").format(customer_name),
            "disabled_customer": {
                "id": customer_id,
                "name": customer_name,
                "reason": reason
            }
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in soft_delete_customer: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        
        if "permission" in str(e).lower() or "not found" in str(e).lower():
            raise
        else:
            frappe.throw(_("Error disabling customer: {0}").format(str(e)))


def _check_customer_dependencies(customer_id):
    """
    Check for documents linked to this customer.
    
    Args:
        customer_id (str): Customer ID to check
        
    Returns:
        dict: Dictionary with doctype as key and count as value
    """
    dependencies = {}
    
    # List of doctypes that commonly link to Customer
    linked_doctypes = [
        "Sales Invoice",
        "Sales Order", 
        "Quotation",
        "Payment Entry",
        "Delivery Note",
        "Customer Group",
        "Address",
        "Contact",
        "Loyalty Point Entry"
    ]
    
    for doctype in linked_doctypes:
        try:
            if frappe.db.exists("DocType", doctype):
                # Check if this doctype has a customer field
                if frappe.db.exists("DocField", {"parent": doctype, "fieldname": "customer"}):
                    count = frappe.db.count(doctype, {"customer": customer_id})
                    dependencies[doctype] = count
                    
                # Special case for Address and Contact (they use link_doctype/link_name)
                elif doctype in ["Address", "Contact"]:
                    count = frappe.db.count(doctype, {
                        "link_doctype": "Customer",
                        "link_name": customer_id
                    })
                    dependencies[doctype] = count
                    
        except Exception as e:
            frappe.logger().warning(f"Could not check {doctype} for customer dependencies: {e}")
            dependencies[doctype] = 0
    
    return dependencies