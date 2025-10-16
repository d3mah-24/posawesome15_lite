# -*- coding: utf-8 -*-
"""
Cleanup Duplicate Offers Function
Handles cleaning up duplicate offers in invoice
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def cleanup_duplicate_offers(invoice_name):
    """
    تنظيف العروض المكررة في الفاتورة
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        if not doc.posa_offers:
            return {"message": "لا توجد عروض في هذه الفاتورة"}
        
        # تجميع العروض حسب الاسم
        offers_by_name = {}
        for row in doc.posa_offers:
            if row.offer_name not in offers_by_name:
                offers_by_name[row.offer_name] = []
            offers_by_name[row.offer_name].append(row)
        
        # إزالة العروض المكررة
        removed_count = 0
        for offer_name, rows in offers_by_name.items():
            if len(rows) > 1:
                # الاحتفاظ بالصف الأول فقط
                for row in rows[1:]:
                    doc.remove(row)
                    removed_count += 1
        
        if removed_count > 0:
            doc.save()
            result = {
                "success": True,
                "message": f"تم إزالة {removed_count} عرض مكرر من الفاتورة {invoice_name}",
                "removed_count": removed_count
            }
            return result
        else:
            result = {
                "success": True,
                "message": "لا توجد عروض مكررة في هذه الفاتورة",
                "removed_count": 0
            }
            return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطأ في تنظيف العروض المكررة: {str(e)}"
        }
