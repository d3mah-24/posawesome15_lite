# -*- coding: utf-8 -*-
"""
Validate Hook Function - Enhanced ERPNext Natural Operations
Handles comprehensive Sales Invoice validation using ERPNext patterns
"""

from __future__ import unicode_literals

import frappe
from frappe import _


def validate(doc, method):
    """
    Enhanced Sales Invoice validation using ERPNext natural patterns
    
    ERPNext Natural Approach:
    - Use frappe.throw() for validation errors (ERPNext stops processing)
    - Let ERPNext handle most validations automatically
    - Focus on POS-specific business rules only
    - Clean, focused validation logic
    """
    if not doc.is_pos:
        return
        
    # POS-specific validations
    validate_required_pos_fields(doc)
    validate_pos_items(doc)
    validate_zero_rated_items(doc)


def validate_required_pos_fields(doc):
    """
    Validate required fields for POS invoices
    ERPNext Natural: Use frappe.throw() to stop processing
    """
    required_fields = {
        "pos_profile": "POS Profile",
        "customer": "Customer", 
        "company": "Company",
        "currency": "Currency",
        "posa_pos_opening_shift": "POS Opening Shift"
    }
    
    for field, label in required_fields.items():
        if not doc.get(field):
            frappe.throw(_("{0} is required for POS Invoice").format(label))


def validate_pos_items(doc):
    """
    Validate POS invoice items
    ERPNext Natural: Let ERPNext handle most item validations
    """
    if not doc.items:
        frappe.throw(_("At least one item is required"))
    
    # Validate item quantities and rates
    for item in doc.items:
        if item.qty <= 0:
            frappe.throw(_("Item quantity must be greater than zero for {0}").format(item.item_code))


def validate_zero_rated_items(doc):
    """
    Validate zero-rated items based on POS Profile settings
    ERPNext Natural: Check settings and apply business rules
    """
    if not doc.pos_profile:
        return
        
    allow_zero_rated = frappe.get_cached_value(
        "POS Profile",
        doc.pos_profile, 
        "posa_allow_zero_rated_items"
    )
    
    for item in doc.items:
        if not item.rate or item.rate == 0:
            if allow_zero_rated:
                item.is_free_item = 1
            else:
                frappe.throw(_("Rate cannot be zero for item {0}").format(item.item_code))
        else:
            item.is_free_item = 0
