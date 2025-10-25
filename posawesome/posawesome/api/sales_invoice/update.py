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
from ..pos_offer.offers import get_applicable_offers, is_offer_applicable, apply_offer_to_invoice


def apply_auto_transaction_discount(doc):
    """Finds auto transaction discount and applies it to the Sales Invoice doc."""

    try:
        # Get all offers for the profile
        profile = doc.pos_profile
        if not profile:
            return False

        # Check if offers are enabled in POS Profile
        pos_profile_doc = frappe.get_doc("POS Profile", profile)
        if not pos_profile_doc.get("posa_auto_fetch_offers"):
            return False

        # Check if auto offers are already applied to this invoice
        existing_auto_offers = []
        if hasattr(doc, 'posa_offers') and doc.posa_offers:
            # Get the offer documents to check if they're auto offers
            for posa_offer in doc.posa_offers:
                try:
                    offer_doc = frappe.get_doc("POS Offer", posa_offer.offer_name)
                    if offer_doc.get("auto") == 1:
                        existing_auto_offers.append(posa_offer.offer_name)
                except:
                    continue

        # If auto offers are already applied, don't apply again
        if existing_auto_offers:
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
                # Apply offer using the new function
                if apply_offer_to_invoice(doc, offer):
                    return True

    except Exception as e:
        # Silent fail - don't break invoice creation
        frappe.log_error(f"Auto discount error: {str(e)}", "Auto Discount Error")

    return False

@frappe.whitelist()
def update_invoice(data):
    """
    Update Sales Invoice using ERPNext native methods only.
    - Accepts posa_offers from UI, resolves to real POS Offer names.
    - Clears/sets Sales Invoice.offer_name safely.
    - Never looks up a "None" offer.
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        name = (data or {}).get("name")
        if not name:
            frappe.throw(_("Invoice name is required for update operations"))

        doc = frappe.get_doc("Sales Invoice", name)

        if doc.docstatus != 0:
            frappe.throw(_("Cannot update submitted Sales Invoice"))

        # Deletion case (empty items sent explicitly)
        if data.get("items") is not None and not data.get("items"):
            frappe.delete_doc("Sales Invoice", doc.name, ignore_permissions=True, force=True)
            frappe.db.commit()
            return {"message": "Invoice deleted successfully"}

        # Extract incoming offers (list of dicts) and remove from payload
        selected_offers = data.get("posa_offers") or []
        if "posa_offers" in data:
            del data["posa_offers"]

        # Reset child table on the doc before applying new offers
        doc.set("posa_offers", [])

        # Update other fields first
        doc.update(data)

        # Resolve offer names and apply
        resolved_offers = []
        for sel in selected_offers:
            if not isinstance(sel, dict):
                continue

            offer_name = (sel.get("offer_name") or sel.get("name") or "") and str(
                sel.get("offer_name") or sel.get("name")
            ).strip()

            # Fallback: resolve by title if provided
            if not offer_name:
                title = (sel.get("title") or "").strip()
                if title:
                    found = frappe.get_all(
                        "POS Offer",
                        filters={"title": title},
                        fields=["name"],
                        limit=1,
                    )
                    if found:
                        offer_name = found[0]["name"]

            if not offer_name:
                continue

            # Verify the POS Offer exists
            exists = frappe.get_all(
                "POS Offer",
                filters={"name": offer_name},
                fields=["name"],
                limit=1,
            )
            if not exists:
                # skip silently; do not break invoice updates
                continue

            # Keep track and append child row for UI/submit visibility
            resolved_offers.append(offer_name)
            doc.append("posa_offers", {"offer_name": offer_name})

            # Apply offer effects to the doc (uses server-side logic only)
            try:
                offer_doc = frappe.get_doc("POS Offer", offer_name)
                apply_offer_to_invoice(doc, offer_doc)
            except Exception as e:
                frappe.log_error(f"Error applying offer {offer_name}: {str(e)}", "POS Offers")

        # Maintain POS flags
        doc.is_pos = 1
        doc.update_stock = 1

        # Sync legacy single link field if it exists
        primary_offer = resolved_offers[0] if resolved_offers else None
        if getattr(doc, "meta", None) and doc.meta.has_field("offer_name"):
            if primary_offer:
                doc.offer_name = primary_offer
            else:
                # Allow draft updates without an offer; submit can re-validate
                doc.offer_name = None
                doc.flags.ignore_mandatory = True

        # Auto transaction discount (server-side check only)
        if apply_auto_transaction_discount(doc):
            doc.calculate_taxes_and_totals()

        # Native calculations
        doc.calculate_taxes_and_totals()

        # POS live-display helper
        _calculate_item_discount_total(doc)

        # Fast save; allow draft updates even when offer_name is empty
        doc.save(ignore_version=True)
        frappe.db.commit()

        return doc.as_dict()

    except frappe.exceptions.ValidationError as ve:
        frappe.logger().error(f"Validation error in update_invoice: {str(ve)}")
        frappe.throw(_("Validation error: {0}").format(str(ve)))
    except Exception as e:
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
