# -*- coding: utf-8 -*-
"""
Updated to use ERPNext Sales Invoice native methods only.
Uses ERPNext's standard document creation with is_pos=1.
"""
from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt,nowdate
from ..pos_offer.offers import get_applicable_offers, is_offer_applicable, apply_offer_to_invoice
from .update import _calculate_item_discount_total


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

        # Check if auto offers are already applied to this invoice (shouldn't happen during creation, but check anyway)
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
        total_qty = sum(flt(item.qty) for item in doc.items)
        total_amount = sum(flt(item.qty) * flt(item.rate) for item in doc.items)
        # Get all auto offers for this POS Profile
        offers = frappe.get_all(
            "POS Offer",
            filters={
                "disable": 0,
                "auto": 1,
                "discount_type": "Discount Percentage",
                "company": doc.company,
                "pos_profile": ["in", [profile, ""]],
                "valid_from": ["<=", doc.posting_date or nowdate()],
                "valid_upto": [">=", doc.posting_date or nowdate()],
                "min_qty": ["<=", total_qty],
                "max_qty": [">=", total_qty],
                "max_amt": [">=", total_amount]
            },
            fields=["name", "discount_percentage", "min_qty", "max_qty", "min_amt", "max_amt", "offer_type"],
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
def create_invoice(data):
    """
    Create new Sales Invoice using ERPNext native methods only.
    Uses frappe.new_doc('Sales Invoice') with is_pos=1.
    """
    try:
        # Parse JSON data
        if isinstance(data, str):
            data = json.loads(data)
    except (json.JSONDecodeError, ValueError) as e:
        frappe.log_error(f"[ERROR] Invalid JSON data: {str(e)}", "POS Invoice Error")
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        # Validate that we're creating new (not updating existing)
        if data.get("name"):
            frappe.throw(_("Cannot specify name when creating new invoice"))

        # Create new Sales Invoice document using ERPNext
        doc = frappe.new_doc("Sales Invoice")


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
        # Ensure POS settings are set
        doc.is_pos = 1
        doc.update_stock = 1

        # Use ERPNext native methods
        doc.set_missing_values()

        if apply_auto_transaction_discount(doc):
             # Rerun calculation to adopt the discount injected by the custom function above
             doc.calculate_taxes_and_totals()
        else:
             pass

        # Calculate taxes and totals using ERPNext native methods
        doc.calculate_taxes_and_totals()

        # Calculate total item discounts (for live display in POS)
        _calculate_item_discount_total(doc)

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

        # Calculate total item discounts (for live display in POS)
        _calculate_item_discount_total(doc)

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

        # Calculate total item discounts (for live display in POS)
        _calculate_item_discount_total(doc)

        doc.save()

        return doc.as_dict()

    except Exception as e:
        frappe.logger().error(f"Error creating new invoice with item: {str(e)}")
        frappe.throw(_("Error creating invoice with item: {0}").format(str(e)))

