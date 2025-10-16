# -*- coding: utf-8 -*-
"""
Get Applicable Offers Function
Handles getting all applicable offers for invoice
"""

from __future__ import unicode_literals

import frappe
from .get_offers import get_offers
from .is_offer_applicable import is_offer_applicable


@frappe.whitelist()
def get_applicable_offers(invoice_name):
    """
    GET - Get all applicable offers for invoice (مطابق للنسخة القديمة مع تحسينات)
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # الحصول على معلومات الملف الشخصي من الفاتورة
        pos_profile = doc.pos_profile if hasattr(doc, 'pos_profile') else None
        if not pos_profile:
            return []
        
        # استخدام دالة get_offers للحصول على العروض المناسبة للملف الشخصي
        all_offers = get_offers(pos_profile)
        
        applicable_offers = []
        
        for offer in all_offers:
            # Check if offer is applicable to this invoice
            if is_offer_applicable(offer, doc):
                applicable_offers.append(offer)
        
        return applicable_offers
        
    except Exception as e:
        return []
