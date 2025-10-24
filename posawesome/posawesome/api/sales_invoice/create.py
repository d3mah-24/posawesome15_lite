# -*- coding: utf-8 -*-
"""
Updated to use ERPNext Sales Invoice native methods only.
Uses ERPNext's standard document creation with is_pos=1.
"""
from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt
from ..pos_offer.get_applicable_offers import get_applicable_offers
from ..pos_offer.get_offers_by_type_handler import get_offers_by_type_handler


def apply_auto_transaction_discount(doc):
    """Finds auto transaction discount and applies it to the Sales Invoice doc."""

    try:
        # Get all offers for the profile
        profile = doc.pos_profile
        if not profile:
            return False

        # Get offers for this POS Profile directly from database
        # We can't use get_offers_by_type_handler because doc.name is None (not saved yet)
        offers = frappe.get_all(
            "POS Offer",
            filters={
                "disable": 0,
                "auto": 1,
                "offer_type": "grand_total",
                "discount_type": "Discount Percentage",
                "pos_profile": ["in", [profile, ""]],
            },
            fields=["name", "discount_percentage", "min_amt", "max_amt"],
            order_by="discount_percentage desc",
            limit=1
        )

        if offers and len(offers) > 0:
            auto_disc_offer = offers[0]
            discount_percentage = flt(auto_disc_offer.get("discount_percentage"))

            # Check min/max amount conditions if set
            # Use flt() to safely handle None values (converts None to 0)
            grand_total = flt(doc.grand_total)
            min_amt = flt(auto_disc_offer.get("min_amt"))
            max_amt = flt(auto_disc_offer.get("max_amt"))

            if min_amt > 0 and grand_total < min_amt:
                return False
            if max_amt > 0 and grand_total > max_amt:
                return False

            if discount_percentage > 0:
                # Apply the discount percentage directly to the Sales Invoice doc
                doc.additional_discount_percentage = discount_percentage

                # Return True to indicate success
                return True

    except Exception as e:
        # Silent fail - don't break invoice creation
        frappe.log_error(f"Auto discount error: {str(e)}", "Auto Discount Error")

    return False

@frappe.whitelist()
def create_invoice(data):
    """
    Create new Sales Invoice using ERPNext native methods only.
    Uses frappe.new_doc('Sales Invoice') with is_pos=1.
    """
    # print("coming in create_invoice ", data)
    try:
        # Parse JSON data
        if isinstance(data, str):
            data = json.loads(data)
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        # Validate that we're creating new (not updating existing)
        if data.get("name"):
            frappe.throw(_("Cannot specify name when creating new invoice"))

        # Create new Sales Invoice document using ERPNext
        doc = frappe.new_doc("Sales Invoice")

        # Update with provided data
        doc.update(data)

        # Ensure POS settings are set
        doc.is_pos = 1
        doc.update_stock = 1

        # Use ERPNext native methods
        doc.set_missing_values()


        if apply_auto_transaction_discount(doc):
             # Rerun calculation to adopt the discount injected by the custom function above
             doc.calculate_taxes_and_totals()

        # Calculate taxes and totals using ERPNext native methods
        doc.calculate_taxes_and_totals()

        # Save the document to get a proper name
        doc.save()

        # Return created document
        return doc.as_dict()

    except frappe.exceptions.ValidationError as ve:
        frappe.logger().error(f"Validation error in create_invoice: {str(ve)}")
        frappe.throw(_("Validation error: {0}").format(str(ve)))

    except Exception as e:
        frappe.logger().error(f"Error in create_invoice: {str(e)}")
        frappe.throw(_("Error creating invoice: {0}").format(str(e)))


@frappe.whitelist()
def add_item_to_invoice(item_code, qty=1, customer=None, pos_profile=None):
    """
    Add item to existing draft invoice or create new one if none exists.
    Uses ERPNext native methods only.
    """
    try:
        if not item_code:
            frappe.throw(_("Item code is required"))

        qty = float(qty) if qty else 1.0

        # Find existing draft invoice for current user
        existing_draft = _find_existing_draft(customer, pos_profile)

        if existing_draft:
            return _add_item_to_existing_invoice(existing_draft, item_code, qty)
        else:
            return _create_new_invoice_with_item(item_code, qty, customer, pos_profile)

    except Exception as e:
        frappe.logger().error(f"Error in add_item_to_invoice: {str(e)}")
        frappe.throw(_("Error adding item: {0}").format(str(e)))


def _find_existing_draft(customer=None, pos_profile=None):
    """
    Find existing draft invoice for current user.
    """
    try:
        filters = {
            "docstatus": 0,  # Draft only
            "owner": frappe.session.user,
        }

        if customer:
            filters["customer"] = customer
        if pos_profile:
            filters["pos_profile"] = pos_profile

        draft_invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=["name"],
            order_by="creation desc",
            limit=1
        )

        return draft_invoices[0].name if draft_invoices else None

    except Exception:
        return None


def _add_item_to_existing_invoice(invoice_name, item_code, qty):
    """
    Add item to existing invoice using ERPNext native methods.
    """
    try:
        # Get existing document
        doc = frappe.get_doc("Sales Invoice", invoice_name)

        # Check if item already exists
        existing_item = None
        for item in doc.items:
            if item.item_code == item_code:
                existing_item = item
                break

        if existing_item:
            # Item exists - increment quantity
            existing_item.qty += qty
        else:
            # Item doesn't exist - add new item row
            item_doc = frappe.get_doc("Item", item_code)

            doc.append("items", {
                "item_code": item_code,
                "item_name": item_doc.item_name,
                "qty": qty,
                "uom": item_doc.stock_uom,
                "rate": item_doc.standard_rate or 0,
            })

        # Use ERPNext native methods
        doc.calculate_taxes_and_totals()
        doc.save()

        return doc.as_dict()

    except Exception as e:
        frappe.logger().error(f"Error adding item to existing invoice: {str(e)}")
        frappe.throw(_("Error adding item to invoice: {0}").format(str(e)))


def _create_new_invoice_with_item(item_code, qty, customer=None, pos_profile=None):
    """
    Create new invoice with specified item using ERPNext native methods.
    """
    try:
        item_doc = frappe.get_doc("Item", item_code)

        # Create new Sales Invoice
        doc = frappe.new_doc("Sales Invoice")

        # Set basic fields
        if customer:
            doc.customer = customer
        if pos_profile:
            doc.pos_profile = pos_profile

        # Set POS settings
        doc.is_pos = 1
        doc.update_stock = 1

        # Add item
        doc.append("items", {
            "item_code": item_code,
            "item_name": item_doc.item_name,
            "qty": qty,
            "uom": item_doc.stock_uom,
            "rate": item_doc.standard_rate or 0,
        })

        # Use ERPNext native methods
        doc.set_missing_values()
        doc.calculate_taxes_and_totals()
        doc.save()

        return doc.as_dict()

    except Exception as e:
        frappe.logger().error(f"Error creating new invoice with item: {str(e)}")
        frappe.throw(_("Error creating invoice with item: {0}").format(str(e)))

