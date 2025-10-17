# -*- coding: utf-8 -*-
"""
Get Customer Credit API
Handles retrieving customer credit information including available credit and advances
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_customer_credit(customer_id, company=None):
    """
    Get available credit information for a customer.
    
    Args:
        customer_id (str): Customer ID/name (required)
        company (str): Company to filter by (optional)
        
    Returns:
        dict: Credit information including invoices and advances
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer not found: {0}").format(customer_id))
        
        # Initialize result structure
        result = {
            "customer": customer_id,
            "company": company,
            "total_available_credit": 0,
            "credit_sources": [],
            "summary": {
                "invoice_credits": 0,
                "advance_credits": 0,
                "total_credits": 0
            }
        }
        
        # Get credit from outstanding return invoices (negative outstanding amount)
        invoice_credits = _get_invoice_credits(customer_id, company)
        result["credit_sources"].extend(invoice_credits)
        
        # Get credit from unallocated advances  
        advance_credits = _get_advance_credits(customer_id, company)
        result["credit_sources"].extend(advance_credits)
        
        # Calculate totals
        invoice_total = sum(credit["available_amount"] for credit in invoice_credits)
        advance_total = sum(credit["available_amount"] for credit in advance_credits)
        
        result["summary"]["invoice_credits"] = invoice_total
        result["summary"]["advance_credits"] = advance_total  
        result["summary"]["total_credits"] = invoice_total + advance_total
        result["total_available_credit"] = invoice_total + advance_total
        
        frappe.logger().debug(f"Customer {customer_id} has total credit: {result['total_available_credit']}")
        
        return result
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_credit: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error retrieving customer credit: {0}").format(str(e)))


@frappe.whitelist()
def get_customer_credit_summary(customer_id, company=None):
    """
    Get a simplified summary of customer credit (faster than full details).
    
    Args:
        customer_id (str): Customer ID/name (required)
        company (str): Company to filter by (optional)
        
    Returns:
        dict: Simplified credit summary
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        # Build filters for both queries
        invoice_filters = {
            "outstanding_amount": ["<", 0],
            "docstatus": 1,
            "is_return": 0,
            "customer": customer_id,
        }
        
        advance_filters = {
            "unallocated_amount": [">", 0],
            "party_type": "Customer", 
            "party": customer_id,
            "docstatus": 1,
        }
        
        if company:
            invoice_filters["company"] = company
            advance_filters["company"] = company
        
        # Get invoice credits using ORM (Backend Improvement Policy)
        invoice_credit_filters = {
            "customer": customer_id,
            "docstatus": 1,
            "is_return": 0,
            "outstanding_amount": ["<", 0]
        }
        
        if company:
            invoice_credit_filters["company"] = company
        
        invoice_credits = frappe.get_all(
            "Sales Invoice",
            filters=invoice_credit_filters,
            fields=["outstanding_amount"],
            order_by="posting_date desc"
        )
        
        invoice_credit = sum(abs(inv.get("outstanding_amount", 0)) for inv in invoice_credits)
        
        # Get advance credits using ORM (Backend Improvement Policy)
        advance_credit_filters = {
            "party_type": "Customer",
            "party": customer_id,
            "docstatus": 1,
            "unallocated_amount": [">", 0]
        }
        
        if company:
            advance_credit_filters["company"] = company
        
        advance_credits = frappe.get_all(
            "Payment Entry",
            filters=advance_credit_filters,
            fields=["unallocated_amount"],
            order_by="posting_date desc"
        )
        
        advance_credit = sum(payment.get("unallocated_amount", 0) for payment in advance_credits)
        
        total_credit = invoice_credit + advance_credit
        
        return {
            "customer": customer_id,
            "company": company,
            "invoice_credits": invoice_credit,
            "advance_credits": advance_credit,
            "total_available_credit": total_credit
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_credit_summary: {str(e)}")
        frappe.throw(_("Error retrieving customer credit summary: {0}").format(str(e)))


def _get_invoice_credits(customer_id, company=None):
    """
    Get credit available from return invoices with negative outstanding amounts.
    
    Returns:
        list: List of invoice credit entries
    """
    filters = {
        "outstanding_amount": ["<", 0],
        "docstatus": 1,
        "is_return": 0,
        "customer": customer_id,
    }
    
    if company:
        filters["company"] = company
    
    outstanding_invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "outstanding_amount", "posting_date", "grand_total", "company"],
        order_by="posting_date desc"
    )
    
    invoice_credits = []
    for invoice in outstanding_invoices:
        credit_amount = abs(invoice.outstanding_amount)
        invoice_credits.append({
            "type": "Invoice Credit",
            "reference_doctype": "Sales Invoice",
            "reference_name": invoice.name,
            "posting_date": invoice.posting_date,
            "available_amount": credit_amount,
            "original_amount": invoice.grand_total,
            "company": invoice.company,
            "description": f"Credit from Sales Invoice {invoice.name}"
        })
    
    return invoice_credits


def _get_advance_credits(customer_id, company=None):
    """
    Get credit available from unallocated advance payments.
    
    Returns:
        list: List of advance credit entries
    """
    filters = {
        "unallocated_amount": [">", 0],
        "party_type": "Customer",
        "party": customer_id,
        "docstatus": 1,
    }
    
    if company:
        filters["company"] = company
    
    advances = frappe.get_all(
        "Payment Entry",
        filters=filters,
        fields=["name", "unallocated_amount", "posting_date", "paid_amount", "company", "mode_of_payment"],
        order_by="posting_date desc"
    )
    
    advance_credits = []
    for advance in advances:
        advance_credits.append({
            "type": "Advance Payment",
            "reference_doctype": "Payment Entry", 
            "reference_name": advance.name,
            "posting_date": advance.posting_date,
            "available_amount": advance.unallocated_amount,
            "original_amount": advance.paid_amount,
            "company": advance.company,
            "mode_of_payment": advance.mode_of_payment,
            "description": f"Advance payment {advance.name} via {advance.mode_of_payment}"
        })
    
    return advance_credits