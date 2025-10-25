# -*- coding: utf-8 -*-
"""
Sales Invoice API - Consolidated
All sales invoice operations using ERPNext native methods only.
"""
from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt, nowdate
from ..pos_offer.offers import get_applicable_offers, is_offer_applicable, apply_offer_to_invoice


# ===== DELETE OPERATIONS =====

@frappe.whitelist()
def delete_invoice(invoice_name):
    """
    Delete Sales Invoice using ERPNext native methods only.
    Uses ERPNext's standard deletion workflow.
    """
    try:
        if not invoice_name:
            frappe.throw(_("Invoice name is required"))

        # Get document using ERPNext
        doc = frappe.get_doc("Sales Invoice", invoice_name)

        # Check permissions using ERPNext
        if not doc.has_permission("delete"):
            frappe.throw(_("Not permitted to delete this invoice"))

        # Only allow deletion of draft documents
        if doc.docstatus != 0:
            frappe.throw(_("Cannot delete submitted invoice. Use cancel instead."))

        # Use ERPNext native delete method
        doc.delete()

        return {
            "success": True,
            "message": "Invoice deleted successfully"
        }

    except frappe.exceptions.DoesNotExistError:
        frappe.throw(_("Invoice {0} does not exist").format(invoice_name))

    except frappe.exceptions.PermissionError as pe:
        frappe.throw(_("Permission denied: {0}").format(str(pe)))

    except frappe.exceptions.ValidationError as ve:
        frappe.throw(_("Validation error: {0}").format(str(ve)))

    except Exception as e:
        frappe.logger().error(f"Error in delete_invoice: {str(e)}")
        frappe.throw(_("Error deleting invoice: {0}").format(str(e)))


# ===== CREATE OPERATIONS =====

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


# ===== GET RETURN OPERATIONS =====

@frappe.whitelist()
def get_invoices_for_return(invoice_name, company):
    """
    Search invoices for return operations
    """
    try:
        # Search for invoices that can be returned
        filters = {
            "company": company,
            "docstatus": 1,  # Only submitted invoices
            "is_return": 0,  # Not already a return
        }

        if invoice_name:
            filters["name"] = ["like", f"%{invoice_name}%"]

        invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=["name", "customer", "grand_total", "outstanding_amount", "posting_date", "currency"],
            order_by="posting_date desc",
            limit=50  # Increased limit
        )

        # Get items data for each invoice with essential fields
        for invoice in invoices:
            items = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": invoice["name"]},
                fields=[
                    "name", "item_code", "item_name", "qty", "rate", "amount", "stock_qty",
                    "discount_percentage", "discount_amount", "uom", "warehouse",
                    "price_list_rate", "conversion_factor"
                ]
            )
            invoice["items"] = items

        return invoices

    except Exception as e:
        frappe.logger().error(f"Error in get_invoices_for_return: {str(e)}")
        return []


# ===== INVOICE RESPONSE HELPERS =====

def get_minimal_invoice_response(invoice_doc):
    """
    Return only essential data needed by POS frontend to minimize response size
    This dramatically reduces the response size from ~50KB to ~5KB
    """
    try:
        # Essential invoice fields only
        minimal_response = {
            "name": invoice_doc.name,
            "is_return": invoice_doc.is_return or 0,
            "docstatus": invoice_doc.docstatus,

            # Financial totals (required for POS display)
            "total": invoice_doc.total or 0,
            "net_total": invoice_doc.net_total or 0,
            "grand_total": invoice_doc.grand_total or 0,
            "total_taxes_and_charges": invoice_doc.total_taxes_and_charges or 0,
            "discount_amount": invoice_doc.discount_amount or 0,
            "additional_discount_percentage": invoice_doc.additional_discount_percentage or 0,

            # Items with only essential fields
            "items": []
        }

        # Add minimal item data
        for item in invoice_doc.items:
            minimal_item = {
                "name": item.name,
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty or 0,
                "rate": item.rate or 0,
                "price_list_rate": item.price_list_rate or 0,
                "base_rate": getattr(item, 'base_rate', item.price_list_rate or item.rate or 0),
                "amount": item.amount or 0,
                "discount_percentage": item.discount_percentage or 0,
                "discount_amount": item.discount_amount or 0,
                "uom": item.uom,

                # POS specific fields
                "posa_row_id": getattr(item, 'posa_row_id', ''),
                "posa_offers": getattr(item, 'posa_offers', '[]'),
                "posa_offer_applied": getattr(item, 'posa_offer_applied', 0),
                "posa_is_offer": getattr(item, 'posa_is_offer', 0),
                "posa_is_replace": getattr(item, 'posa_is_replace', 0),
                "is_free_item": getattr(item, 'is_free_item', 0),

                # Batch/Serial if exists
                "batch_no": getattr(item, 'batch_no', ''),
                "serial_no": getattr(item, 'serial_no', ''),
            }

            minimal_response["items"].append(minimal_item)

        # Add payments if any
        minimal_response["payments"] = []
        if invoice_doc.payments:
            for payment in invoice_doc.payments:
                minimal_payment = {
                    "mode_of_payment": payment.mode_of_payment,
                    "amount": payment.amount or 0,
                    "account": getattr(payment, 'account', ''),
                }
                minimal_response["payments"].append(minimal_payment)

        # Add posa_offers if any
        minimal_response["posa_offers"] = []
        if hasattr(invoice_doc, 'posa_offers') and invoice_doc.posa_offers:
            for offer in invoice_doc.posa_offers:
                minimal_offer = {
                    "name": offer.name,
                    "offer_name": getattr(offer, 'offer_name', ''),
                    "apply_on": getattr(offer, 'apply_on', ''),
                    "offer": getattr(offer, 'offer', ''),
                    "offer_applied": getattr(offer, 'offer_applied', 0),
                    "row_id": getattr(offer, 'row_id', ''),
                }
                minimal_response["posa_offers"].append(minimal_offer)

        return minimal_response

    except Exception as e:
        raise


# ===== SUBMIT OPERATIONS =====

@frappe.whitelist()
def submit_invoice(data=None, name=None, invoice=None, invoice_data=None):
    """
    Submit Sales Invoice using ERPNext native methods only.
    Uses ERPNext's standard submission workflow.
    """
    try:
        # Determine invoice name from any parameter
        invoice_name = name or (
            (json.loads(data) if isinstance(data, str) else data or {}).get("name") if data else None
        ) or (
            (json.loads(invoice) if isinstance(invoice, str) else invoice or {}).get("name") if invoice else None
        ) or (
            (json.loads(invoice_data) if isinstance(invoice_data, str) else invoice_data or {}).get("name") if invoice_data else None
        )

        if not invoice_name:
            frappe.throw(_("Invoice name is required for submission"))

        # Get Sales Invoice document
        doc = frappe.get_doc("Sales Invoice", invoice_name)

        # Check if already submitted
        if doc.docstatus == 1:
            frappe.throw(_("Invoice is already submitted"))
        elif doc.docstatus == 2:
            frappe.throw(_("Cannot submit cancelled invoice"))

        # Update with any new data if provided
        if data:
            data_dict = json.loads(data) if isinstance(data, str) else data
            doc.update(data_dict)

        # Ensure POS settings are maintained
        doc.is_pos = 1
        doc.update_stock = 1

        # Use ERPNext native methods for calculation and submission
        doc.calculate_taxes_and_totals()
        doc.validate()
        doc.save()
        doc.submit()

        # Return submitted document
        return {
            "success": True,
            "message": "Invoice submitted successfully",
            "invoice": doc.as_dict()
        }

    except frappe.exceptions.ValidationError as ve:
        frappe.logger().error(f"Validation error in submit_invoice: {str(ve)}")
        frappe.throw(_("Validation error: {0}").format(str(ve)))

    except Exception as e:
        frappe.logger().error(f"Error in submit_invoice: {str(e)}")
        frappe.throw(_("Error submitting invoice: {0}").format(str(e)))


# ===== UPDATE OPERATIONS =====

@frappe.whitelist()
def update_invoice(data):
    """
    Update Sales Invoice using ERPNext native methods only.
    - Accepts posa_offers from UI and applies them server-side.
    - Keeps ignore_pricing_rule=1 while applying offers so item discounts stick.
    """
    import json
    import frappe

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

        # Delete draft when explicit empty items are sent
        if data.get("items") is not None and not data.get("items"):
            frappe.delete_doc("Sales Invoice", doc.name, ignore_permissions=True, force=True)
            frappe.db.commit()
            return {"message": "Invoice deleted successfully"}

        # Extract selected offers from payload and remove them from doc.update
        selected_offers = data.get("posa_offers") or []
        if "posa_offers" in data:
            del data["posa_offers"]

        # Clean offers (only keep those with a name or title)
        cleaned_offers = []
        for sel in (selected_offers if isinstance(selected_offers, list) else [selected_offers]):
            if not isinstance(sel, dict):
                continue
            nm = (sel.get("offer_name") or sel.get("name") or "").strip()
            title = (sel.get("title") or "").strip()
            if nm:
                cleaned_offers.append({"offer_name": nm})
            elif title:
                cleaned_offers.append({"title": title})

        # Refresh child table and update basic fields
        doc.set("posa_offers", [])
        doc.update(data)

        # POS flags and source
        doc.is_pos = 1
        doc.update_stock = 1
        doc.flags.from_pos_page = True

        # Force ignore_pricing_rule when we are applying manual offers
        if cleaned_offers:
            doc.ignore_pricing_rule = 1
        elif "ignore_pricing_rule" in data:
            # Honor explicit field even when no offers were sent
            doc.ignore_pricing_rule = 1 if data.get("ignore_pricing_rule") else 0

        # Resolve each offer and apply to the invoice
        resolved = []
        for sel in cleaned_offers:
            offer_name = sel.get("offer_name")
            if not offer_name and sel.get("title"):
                # Resolve by title
                found = frappe.get_all(
                    "POS Offer",
                    filters={"title": sel["title"]},
                    fields=["name"],
                    limit=1,
                )
                offer_name = found[0]["name"] if found else None

            if not offer_name:
                continue

            exists = frappe.get_all("POS Offer", filters={"name": offer_name}, fields=["name"], limit=1)
            if not exists:
                # Skip invalid offers silently (don't break updates)
                continue

            # Track and mirror into child table for UI
            resolved.append(offer_name)
            doc.append("posa_offers", {"offer_name": offer_name})

            # Apply server-side logic
            try:
                offer_doc = frappe.get_doc("POS Offer", offer_name)
                apply_offer_to_invoice(doc, offer_doc)
            except Exception as e:
                frappe.log_error(f"Error applying offer {offer_name}: {str(e)}", "POS Offers")

        # Legacy single link sync (optional)
        if getattr(doc, "meta", None) and doc.meta.has_field("offer_name"):
            doc.offer_name = resolved[0] if resolved else None
            if not resolved:
                # don't fail on missing offer at draft time
                doc.flags.ignore_mandatory = True

        # Totals
        doc.calculate_taxes_and_totals()
        _calculate_item_discount_total(doc)

        # Save fast
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
