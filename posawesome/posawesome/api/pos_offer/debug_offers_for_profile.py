# -*- coding: utf-8 -*-
"""
Debug Offers for Profile Function
Handles debugging offers for profile
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import nowdate


@frappe.whitelist()
def debug_offers_for_profile(profile):
    """
    دالة تشخيص لجلب العروض - بدون فلاتر معقدة
    """
    try:
        # جلب جميع العروض بدون فلاتر
        all_offers = frappe.get_all(
            "POS Offer",
            fields=["name", "title", "company", "pos_profile", "warehouse", "valid_from", "valid_upto", "disable"]
        )
        
        # جلب العروض النشطة فقط
        active_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0},
            fields=["name", "title", "company", "pos_profile", "warehouse", "valid_from", "valid_upto"]
        )
        
        # جلب ملف POS
        pos_profile = frappe.get_doc("POS Profile", profile)
        company = pos_profile.company
        warehouse = pos_profile.warehouse
        date = nowdate()
        
        # جلب العروض الخاصة بالشركة
        company_offers = frappe.get_all(
            "POS Offer",
            filters={"disable": 0, "company": company},
            fields=["name", "title", "company", "pos_profile", "warehouse", "valid_from", "valid_upto"]
        )
        
        return {
            "total_offers": len(all_offers),
            "active_offers": len(active_offers),
            "company_offers": len(company_offers),
            "profile_info": {
                "name": profile,
                "company": company,
                "warehouse": warehouse,
                "current_date": date
            },
            "all_offers": all_offers,
            "active_offers": active_offers,
            "company_offers": company_offers
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        pass
