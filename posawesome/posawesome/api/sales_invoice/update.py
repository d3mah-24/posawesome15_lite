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
        doc.set("posa_offers", [])

        # 2) Extract and remove posa_offers from incoming data
        selected_offers = data.get("posa_offers") or []
        if "posa_offers" in data:
            del data["posa_offers"]

        # 3) Now update the document safely
        doc.update(data)

        # 3) resolve and apply offers safely
                # 3) resolve and apply offers safely
        try:
            for sel in selected_offers:
                if not isinstance(sel, dict):
                    continue

                # Try to get the actual document name
                offer_name = sel.get("offer_name") or sel.get("name")

                # If not found, try to look up by title
                if not offer_name or offer_name == "None" or str(offer_name).strip() == "":
                  title = sel.get("title")
                  if title:
                      try:
                          offer_docs = frappe.get_all("POS Offer", filters={"title": title}, fields=["name"])
                          if offer_docs:
                             offer_name = offer_docs[0].name
                          else:
                              # Skip if no offer found with this title
                             continue
                      except:
                          continue

                # Validate that the offer actually exists before applying
                if not offer_name or offer_name == "None" or str(offer_name).strip() == "":
                    continue

                try:
                    # Check if POS Offer document exists
                    if not frappe.db.exists("POS Offer", offer_name):
                        frappe.log_error(f"POS Offer not found: {offer_name}", "POS Offers")
                        continue

                    offer_doc = frappe.get_doc("POS Offer", offer_name)
                    apply_offer_to_invoice(doc, offer_doc)
                except Exception as e:
                    frappe.log_error(f"Error applying offer {offer_name}: {str(e)}", "POS Offers")

        except Exception as e:
            frappe.log_error(f"Error processing manual POS offers: {str(e)}", "POS Offers")
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
