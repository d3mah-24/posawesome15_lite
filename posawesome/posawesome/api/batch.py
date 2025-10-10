# -*- coding: utf-8 -*-
"""
Batch API
Handles all Batch related operations
"""

from __future__ import unicode_literals

import frappe
from frappe import _

# متغير عام لتجميع التشخيصات
debug_log = []

def log_debug(message):
    """إضافة رسالة للتشخيص العام"""
    debug_log.append(str(message))

def clear_debug_log():
    """مسح التشخيص العام"""
    global debug_log
    debug_log = []

def save_debug_log():
    """حفظ التشخيص العام في سجل واحد"""
    global debug_log
    if debug_log:
        # حفظ في سجل الأخطاء فقط (بدون مسح)
        frappe.log_error(message="\n".join(debug_log), title="Batch API - تشخيص شامل")
        # لا نمسح debug_log هنا - نتركه للتجميع


@frappe.whitelist()
def process_batch_selection(item_code, current_item_row_id, existing_items_data, batch_no_data, preferred_batch_no=None):
    """
    Process batch selection for items
    """
    try:
        # Implementation for batch selection processing
        # This is a placeholder - you may need to implement the actual logic
        return {
            "success": True,
            "message": "Batch selection processed",
            "data": {}
        }
    except Exception as e:
        frappe.log_error(f"Error processing batch selection: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


# دالة لحفظ جميع التشخيصات في Error Log
def show_all_debug_logs():
    """حفظ جميع التشخيصات المجمعة في Error Log"""
    global debug_log
    if debug_log:
        # حفظ في سجل الأخطاء فقط
        frappe.log_error(message="\n".join(debug_log), title="Batch API - جميع التشخيصات المجمعة")
        
        # مسح التشخيصات بعد الحفظ
        debug_log = []
