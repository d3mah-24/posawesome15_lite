# -*- coding: utf-8 -*-
"""
Get Offers by Type Handler Function
Handles routing to specific offer type functions
"""

from __future__ import unicode_literals

import frappe
from .get_offer_fields_mapping import get_offer_fields_mapping
from .get_offer_filters_mapping import get_offer_filters_mapping
from .offer_utils import is_offer_applicable


def get_offers_by_type_handler(offer_type, invoice_name, coupon_code=None):
    """
    Handler function to route to specific offer type functions
    """
    try:
        # Get field mapping for each offer type
        field_mapping = get_offer_fields_mapping()
        fields = field_mapping.get(offer_type, ["*"])
        
        # Get filter mapping for each offer type
        filter_mapping = get_offer_filters_mapping()
        filters = filter_mapping.get(offer_type, {"disable": 0})
        
        # Add coupon filter if needed
        if offer_type == "coupon" and coupon_code:
            filters["title"] = ["like", f"%{coupon_code}%"]
        
        # Get offers from database
        offers = frappe.get_all(
            "POS Offer",
            filters=filters,
            fields=fields
        )
        
        # Check applicability
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        applicable_offers = []
        
        for offer in offers:
            if is_offer_applicable(offer, doc):
                applicable_offers.append(offer)
        
        return {
            "success": True,
            "offers": applicable_offers,
            "count": len(applicable_offers),
            "message": f"تم العثور على {len(applicable_offers)} عرض {offer_type} مناسب"
        }
        
    except Exception as e:
        return {
            "success": False,
            "offers": [],
            "count": 0,
            "error": str(e),
            "message": f"خطأ في معالج نوع العرض: {str(e)}"
        }
    finally:
        pass
