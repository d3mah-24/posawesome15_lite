# -*- coding: utf-8 -*-
"""
POS Invoice Offers and Coupons Management API

This module handles all offer and coupon-related operations for POS invoices:
- Apply/remove offers
- Coupon validation
- Offer calculations
- Discount management
"""

from __future__ import unicode_literals

import json

import frappe
from frappe import _
from frappe.utils import flt

from posawesome.posawesome.doctype.pos_coupon.pos_coupon import (
    update_coupon_code_count,
)


@frappe.whitelist()  # type: ignore
def apply_offers_to_invoice(invoice_name, offer_names):
    """
    POST - Apply specific offers to an invoice
    """
    try:
        if not invoice_name or not offer_names:
            return None

        # Handle both string and list inputs
        if isinstance(offer_names, str):
            try:
                offer_names = json.loads(offer_names)
            except (json.JSONDecodeError, ValueError):
                offer_names = [offer_names]

        if not isinstance(offer_names, list):
            offer_names = [offer_names]

        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore

        # Apply each offer
        for offer_name in offer_names:
            try:
                _apply_single_offer(doc, offer_name)
            except Exception as e:
                frappe.log_error(
                    f"Error applying offer {offer_name}: {str(e)}"
                )
                continue

        # Let ERPNext handle all calculations
        doc.set_missing_values()
        doc.calculate_taxes_and_totals()
        doc.save()

        return doc.as_dict()
    except Exception as e:
        frappe.log_error(
            f"Error in apply_offers_to_invoice: {str(e)}"
        )
        raise


@frappe.whitelist()  # type: ignore
def remove_offers_from_invoice(invoice_name, offer_names):
    """
    DELETE - Remove specific offers from an invoice
    """
    try:
        if not invoice_name or not offer_names:
            return None

        # Handle both string and list inputs
        if isinstance(offer_names, str):
            try:
                offer_names = json.loads(offer_names)
            except (json.JSONDecodeError, ValueError):
                offer_names = [offer_names]

        if not isinstance(offer_names, list):
            offer_names = [offer_names]

        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore

        # Remove each offer
        for offer_name in offer_names:
            try:
                _remove_single_offer(doc, offer_name)
            except Exception as e:
                frappe.log_error(
                    f"Error removing offer {offer_name}: {str(e)}"
                )
                continue

        # Let ERPNext handle all calculations
        doc.set_missing_values()
        doc.calculate_taxes_and_totals()
        doc.save()

        return doc.as_dict()
    except Exception as e:
        frappe.log_error(
            f"Error in remove_offers_from_invoice: {str(e)}"
        )
        raise


@frappe.whitelist()  # type: ignore
def get_applicable_offers(invoice_name):
    """
    GET - Get all applicable offers for an invoice
    """
    try:
        if not invoice_name:
            return []

        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        
        # Get all active offers
        offers = frappe.get_all(
            "POS Offer",
            filters={"disabled": 0},
            fields=["name", "offer_name", "offer_type", "discount_percentage", "discount_amount"]
        )
        
        applicable_offers = []
        
        for offer in offers:
            # Check if offer is applicable
            if _is_offer_applicable(doc, offer):
                applicable_offers.append(offer)
        
        return applicable_offers
        
    except Exception as e:
        frappe.log_error(f"Error getting applicable offers: {str(e)}")
        return []


@frappe.whitelist()  # type: ignore
def validate_offer_coupon(offer_data):
    """
    Validate offer coupon code
    """
    try:
        if isinstance(offer_data, str):
            offer_data = json.loads(offer_data)
        
        coupon_code = offer_data.get("coupon_code")
        if not coupon_code:
            return {"valid": False, "message": "Coupon code is required"}
        
        # Check if coupon exists and is valid
        coupon = frappe.get_doc("POS Coupon", coupon_code)
        
        if coupon.disabled:
            return {"valid": False, "message": "Coupon is disabled"}
        
        if coupon.maximum_use > 0 and coupon.used >= coupon.maximum_use:
            return {"valid": False, "message": "Coupon usage limit exceeded"}
        
        return {
            "valid": True,
            "coupon": coupon.as_dict(),
            "message": "Coupon is valid"
        }
        
    except frappe.DoesNotExistError:
        return {"valid": False, "message": "Invalid coupon code"}
    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}


@frappe.whitelist()  # type: ignore
def check_offer_conditions(offer_data, qty, amount):
    """
    Check if offer conditions are met
    """
    try:
        if isinstance(offer_data, str):
            offer_data = json.loads(offer_data)
        
        min_qty = flt(offer_data.get("min_qty", 0))
        min_amount = flt(offer_data.get("min_amount", 0))
        
        if min_qty > 0 and flt(qty) < min_qty:
            return {
                "valid": False,
                "message": f"Minimum quantity required: {min_qty}"
            }
        
        if min_amount > 0 and flt(amount) < min_amount:
            return {
                "valid": False,
                "message": f"Minimum amount required: {min_amount}"
            }
        
        return {
            "valid": True,
            "message": "Offer conditions met"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error checking conditions: {str(e)}"
        }


@frappe.whitelist()  # type: ignore
def process_item_offer(offer_data, items_data):
    """
    Process item-level offer
    """
    try:
        if isinstance(offer_data, str):
            offer_data = json.loads(offer_data)
        if isinstance(items_data, str):
            items_data = json.loads(items_data)
        
        offer_type = offer_data.get("offer_type")
        discount_percentage = flt(offer_data.get("discount_percentage", 0))
        discount_amount = flt(offer_data.get("discount_amount", 0))
        
        processed_items = []
        
        for item in items_data:
            if offer_type == "Percentage":
                item["discount_percentage"] = discount_percentage
            elif offer_type == "Amount":
                item["discount_amount"] = discount_amount
            
            processed_items.append(item)
        
        return processed_items
        
    except Exception as e:
        frappe.throw(_("Error processing item offer: {0}").format(str(e)))


def _apply_single_offer(doc, offer_name):
    """Apply a single offer to the invoice"""
    try:
        offer = frappe.get_doc("POS Offer", offer_name)
        
        if offer.offer_type == "Item Discount":
            # Apply item-level discount
            for item in doc.items:
                if offer.discount_percentage > 0:
                    item.discount_percentage = offer.discount_percentage
                elif offer.discount_amount > 0:
                    item.discount_amount = offer.discount_amount
        
        elif offer.offer_type == "Invoice Discount":
            # Apply invoice-level discount
            if offer.discount_percentage > 0:
                doc.additional_discount_percentage = offer.discount_percentage
            elif offer.discount_amount > 0:
                doc.discount_amount = offer.discount_amount
        
    except Exception as e:
        frappe.log_error(f"Error applying offer {offer_name}: {str(e)}")


def _remove_single_offer(doc, offer_name):
    """Remove a single offer from the invoice"""
    try:
        offer = frappe.get_doc("POS Offer", offer_name)
        
        if offer.offer_type == "Item Discount":
            # Remove item-level discount
            for item in doc.items:
                item.discount_percentage = 0
                item.discount_amount = 0
        
        elif offer.offer_type == "Invoice Discount":
            # Remove invoice-level discount
            doc.additional_discount_percentage = 0
            doc.discount_amount = 0
        
    except Exception as e:
        frappe.log_error(f"Error removing offer {offer_name}: {str(e)}")


def _is_offer_applicable(doc, offer):
    """Check if an offer is applicable to the invoice"""
    try:
        # Check minimum quantity
        total_qty = sum(flt(item.qty) for item in doc.items)
        if offer.get("min_qty", 0) > 0 and total_qty < offer.min_qty:
            return False
        
        # Check minimum amount
        if offer.get("min_amount", 0) > 0 and flt(doc.grand_total) < offer.min_amount:
            return False
        
        return True
        
    except Exception:
        return False

