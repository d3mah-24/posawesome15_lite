# -*- coding: utf-8 -*-
"""
Get Applicable Offers Function
Handles getting all applicable offers for invoice
"""

from __future__ import unicode_literals

import frappe
from .get_offers import get_offers
from .offer_utils import is_offer_applicable


@frappe.whitelist()
def get_applicable_offers(invoice_name):
    """
    GET - Get all applicable offers for invoice (مطابق للنسخة القديمة مع تحسينات)
    """
    try:
        frappe.log_error(f"[DEBUG] get_applicable_offers called with invoice: {invoice_name}", "Offers Debug - Start")
        
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # الحصول على معلومات الملف الشخصي من الفاتورة
        pos_profile = doc.pos_profile if hasattr(doc, 'pos_profile') else None
        if not pos_profile:
            frappe.log_error(f"[DEBUG] No POS Profile found for invoice: {invoice_name}", "Offers Debug - No Profile")
            return []
        
        frappe.log_error(f"[DEBUG] POS Profile: {pos_profile}, Customer: {doc.customer}, Grand Total: {doc.grand_total}, Items count: {len(doc.items)}", "Offers Debug - Invoice Data")
        
        # استخدام دالة get_offers للحصول على العروض المناسبة للملف الشخصي
        all_offers = get_offers(pos_profile)
        
        frappe.log_error(f"[DEBUG] Total offers from get_offers: {len(all_offers)}", "Offers Debug - All Offers Count")
        
        applicable_offers = []
        
        for offer in all_offers:
            # Check if offer is applicable to this invoice
            is_applicable = is_offer_applicable(offer, doc)
            frappe.log_error(f"[DEBUG] Offer '{offer.get('name')}' applicable: {is_applicable} | Type: {offer.get('offer')} | Apply On: {offer.get('apply_on')}", "Offers Debug - Offer Check")
            
            if is_applicable:
                applicable_offers.append(offer)
        
        frappe.log_error(f"[DEBUG] Total applicable offers: {len(applicable_offers)}", "Offers Debug - Applicable Count")
        
        return applicable_offers
        
    except Exception as e:
        frappe.log_error(f"[ERROR] get_applicable_offers exception: {str(e)}\nInvoice: {invoice_name}", "Offers Debug - Exception")
        return []
