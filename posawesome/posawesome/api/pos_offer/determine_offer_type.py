# -*- coding: utf-8 -*-
"""
Determine Offer Type Function
Handles determining offer type based on invoice data
"""

from __future__ import unicode_literals

import frappe


def determine_offer_type(invoice_doc):
    """
    Determine the most appropriate offer type based on invoice data
    """
    try:
        # Check if invoice has items
        if not invoice_doc.items:
            return "unconditional"
        
        # Check for auto offers first
        auto_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "auto": 1},
            fields=["name"]
        )
        
        if auto_offers:
            return "auto"
        
        # Check for manual offers
        manual_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "auto": 0},
            fields=["name"]
        )
        
        if manual_offers:
            return "manual"
        
        # Check for coupon offers
        coupon_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "coupon_based": 1},
            fields=["name"]
        )
        
        if coupon_offers:
            return "coupon"
        
        # Check for give product offers
        give_product_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "offer": "Give Product"},
            fields=["name"]
        )
        
        if give_product_offers:
            return "give_product"
        
        # Check for loyalty offers
        loyalty_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "offer": "Loyalty Point"},
            fields=["name"]
        )
        
        if loyalty_offers:
            return "loyalty"
        
        # Check for percentage offers
        percentage_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "discount_type": "Discount Percentage"},
            fields=["name"]
        )
        
        if percentage_offers:
            return "percentage"
        
        # Check for conditional offers
        conditional_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "min_qty": [">", 0]},
            fields=["name"]
        )
        
        if conditional_offers:
            return "conditional"
        
        return "unconditional"
        
    except Exception as e:
        return "unconditional"
    finally:
        pass
