# -*- coding: utf-8 -*-
"""
Get Minimal Invoice Response Function
Handles creating minimal response for POS frontend
"""

from __future__ import unicode_literals

import frappe


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
