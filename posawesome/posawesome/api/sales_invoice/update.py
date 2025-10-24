# -*- coding: utf-8 -*-
"""
Updated to use ERPNext Sales Invoice native methods only.
No custom calculations - everything handled by ERPNext core.
"""
from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt
from ..pos_offer.offers import get_applicable_offers, is_offer_applicable


def apply_auto_transaction_discount(doc):
    """Finds auto transaction discount and applies it to the Sales Invoice doc."""

    try:
        # Get all offers for the profile
        profile = doc.pos_profile
        if not profile:
            return False

        # Get all auto offers for this POS Profile
        offers = frappe.get_all(
            "POS Offer",
            filters={
                "disable": 0,
                "auto": 1,
                "discount_type": "Discount Percentage",
                "pos_profile": ["in", [profile, ""]],
            },
            fields=["name", "discount_percentage", "min_amt", "max_amt", "offer_type"],
            order_by="discount_percentage desc"
        )

        # Check each offer for applicability
        for offer in offers:
            if is_offer_applicable(offer, doc):
                discount_percentage = flt(offer.get("discount_percentage"))

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
def update_invoice(data):
    """
    Update Sales Invoice using ERPNext native methods only.
    Uses Sales Invoice + is_pos=1 + update_stock=1 approach.
    """
    try:
        # Parse JSON data
        if isinstance(data, str):
            data = json.loads(data)
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        if not data.get("name"):
            frappe.throw(_("Invoice name is required for update operations"))

        # Get existing Sales Invoice document
        doc = frappe.get_doc("Sales Invoice", data.get("name"))

        # Verify it's still a draft
        if doc.docstatus != 0:
            frappe.throw(_("Cannot update submitted Sales Invoice"))

        # Handle empty items (deletion case)
        if data.get("items") is not None and not data.get("items"):
            frappe.delete_doc("Sales Invoice", doc.name, ignore_permissions=True, force=True)
            frappe.db.commit()
            return {"message": "Invoice deleted successfully"}

        # Update document with new data (client now sends all required fields including price_list_rate)
        doc.update(data)

        # Ensure POS settings are maintained
        doc.is_pos = 1
        doc.update_stock = 1

        # Apply auto transaction discount if applicable
        if apply_auto_transaction_discount(doc):
            # Rerun calculation to adopt the discount injected by the custom function above
            doc.calculate_taxes_and_totals()

        # Let ERPNext handle all calculations using native methods
        doc.calculate_taxes_and_totals()

        # Calculate total item discounts (for live display in POS)
        _calculate_item_discount_total(doc)

        # Save using ERPNext native save
        doc.save()
        frappe.db.commit()

        # Return updated document
        return doc.as_dict()

    except frappe.exceptions.ValidationError as ve:
        # Handle validation errors gracefully
        frappe.logger().error(f"Validation error in update_invoice: {str(ve)}")
        frappe.throw(_("Validation error: {0}").format(str(ve)))

    except Exception as e:
        # Log and re-raise any other errors
        frappe.logger().error(f"Error in update_invoice: {str(e)}")
        frappe.throw(_("Error updating invoice: {0}").format(str(e)))


def _calculate_item_discount_total(doc):
    """
    Calculate total item-level discounts and store in posa_item_discount_total.

    Simply sum the discount_amount field from each item.
    ERPNext already calculates this per item in Sales Invoice Item table.

    Only calculates when:
    - Invoice is POS (is_pos = 1)
    """
    # Check if this is a POS invoice
    if not getattr(doc, 'is_pos', False):
        return

    # Simply sum discount_amount from all items
    total_item_discount = sum(flt(item.discount_amount) for item in doc.items)

    # Store in custom field
    doc.posa_item_discount_total = flt(total_item_discount, doc.precision("posa_item_discount_total"))
