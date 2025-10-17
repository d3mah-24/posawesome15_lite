# -*- coding: utf-8 -*-
"""
Get Customer Balance API
Handles retrieving customer balance information
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_customer_balance(customer_id, company=None):
    """
    Get customer balance information.
    
    Args:
        customer_id (str): Customer ID/name (required)
        company (str): Company to filter by (optional)
        
    Returns:
        dict: Balance information including outstanding amount
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
            
        # Check if customer exists
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer not found"))
        
        # Get customer balance from Customer doctype
        customer = frappe.get_doc("Customer", customer_id)
        
        # Get outstanding amount using ORM (Backend Improvement Policy)
        invoice_filters = {
            "customer": customer_id,
            "docstatus": 1
        }
        
        if company:
            invoice_filters["company"] = company
        
        # Get invoice data using ORM with specific fields only
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=invoice_filters,
            fields=["outstanding_amount", "grand_total"],
            order_by="posting_date desc"
        )
        
        # Calculate totals using Python (ORM approach)
        outstanding_amount = sum(inv.get("outstanding_amount", 0) for inv in invoices)
        total_invoiced = sum(inv.get("grand_total", 0) for inv in invoices)
        invoice_count = len(invoices)
        
        result = [{
            "outstanding_amount": outstanding_amount,
            "total_invoiced": total_invoiced,
            "invoice_count": invoice_count
        }]
        
        # Get credit limit from child table
        credit_limit = 0
        if hasattr(customer, 'credit_limits') and customer.credit_limits:
            # Get the first credit limit entry or filter by company
            credit_entry = customer.credit_limits[0]
            if company:
                for cl in customer.credit_limits:
                    if cl.company == company:
                        credit_entry = cl
                        break
            credit_limit = credit_entry.credit_limit if credit_entry else 0

        balance_info = {
            "customer_id": customer_id,
            "customer_name": customer.customer_name,
            "outstanding_amount": result[0].get("outstanding_amount", 0) if result else 0,
            "total_invoiced": result[0].get("total_invoiced", 0) if result else 0,
            "invoice_count": result[0].get("invoice_count", 0) if result else 0,
            "credit_limit": credit_limit,
            "payment_terms": getattr(customer, 'payment_terms', None),
            "customer_group": customer.customer_group,
            "territory": customer.territory
        }
        
        # Calculate available credit
        balance_info["available_credit"] = max(0, balance_info["credit_limit"] - balance_info["outstanding_amount"])
        
        return balance_info
        
    except frappe.DoesNotExistError:
        frappe.throw(_("Customer {0} not found").format(customer_id))
    except Exception as e:
        frappe.log_error(
            message=f"Error getting customer balance: {str(e)}",
            title="Customer Balance API Error"
        )
        frappe.throw(_("Failed to get customer balance: {0}").format(str(e)))


@frappe.whitelist()
def get_customer_outstanding_invoices(customer_id, company=None, limit=None):
    """
    Get list of outstanding invoices for a customer.
    
    Args:
        customer_id (str): Customer ID/name (required)
        company (str): Company to filter by (optional)
        limit (int): Limit number of results (optional)
        
    Returns:
        list: Outstanding invoices with details
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        # Build filters using ORM (Backend Improvement Policy)    
        invoice_filters = {
            "customer": customer_id,
            "docstatus": 1,
            "outstanding_amount": [">", 0]
        }
        
        if company:
            invoice_filters["company"] = company
        
        # Get outstanding invoices using ORM with specific fields
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=invoice_filters,
            fields=[
                "name", "posting_date", "due_date", "grand_total",
                "outstanding_amount", "currency", "status"
            ],
            order_by="posting_date desc",
            limit=int(limit) if limit else None
        )
        
        # Calculate days overdue using Python (avoid SQL functions)
        from datetime import date
        today = date.today()
        
        for invoice in invoices:
            if invoice.get("due_date"):
                due_date = invoice["due_date"]
                if isinstance(due_date, str):
                    from dateutil.parser import parse
                    due_date = parse(due_date).date()
                invoice["days_overdue"] = (today - due_date).days
            else:
                invoice["days_overdue"] = 0
        
        return invoices
        
    except Exception as e:
        frappe.log_error(
            message=f"Error getting customer outstanding invoices: {str(e)}",
            title="Customer Outstanding Invoices API Error"
        )
        frappe.throw(_("Failed to get outstanding invoices: {0}").format(str(e)))