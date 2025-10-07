# -*- coding: utf-8 -*-
"""
Process Item Offer API
"""

from __future__ import unicode_literals

import json

import frappe
from frappe import _
from frappe.utils import flt


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
