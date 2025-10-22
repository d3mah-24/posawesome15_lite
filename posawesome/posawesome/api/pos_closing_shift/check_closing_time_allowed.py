# -*- coding: utf-8 -*-
# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, time as dtime, timedelta


@frappe.whitelist()
def check_closing_time_allowed(pos_profile):
    """
    Check if closing shift is allowed at current time
    Returns: {"allowed": True/False, "message": "reason"}
    """
    try:
        if not pos_profile:
            return {"allowed": True, "message": "No profile specified"}
            
        profile = frappe.get_doc("POS Profile", pos_profile)
        
        # Check if closing time control is enabled
        if not profile.get("posa_closing_time_control"):
            return {"allowed": True, "message": "Time control disabled"}

        closing_start_time = profile.get("posa_closing_time_start")
        closing_end_time = profile.get("posa_closing_time_end")

        if not closing_start_time or not closing_end_time:
            return {"allowed": True, "message": "Time not configured"}

        # Parse times
        start_time = _parse_time(closing_start_time)
        end_time = _parse_time(closing_end_time)

        if not start_time or not end_time:
            return {"allowed": True, "message": "Invalid time format"}

        # Get current datetime
        current_dt = frappe.utils.now_datetime()

        # Create datetime objects for comparison
        start_dt = current_dt.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second, microsecond=start_time.microsecond)
        end_dt = current_dt.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second, microsecond=end_time.microsecond)

        # If start_time > end_time, assume end_time is next day
        if start_time > end_time:
            end_dt = end_dt + timedelta(days=1)

        # Check if current time is within [start_dt, end_dt]
        allowed = start_dt <= current_dt <= end_dt

        if allowed:
            return {"allowed": True, "message": "Closing allowed"}
        else:
            start_str = start_time.strftime("%H:%M")
            end_str = end_time.strftime("%H:%M")
            if start_time > end_time:
                end_str += " (next day)"
            return {
                "allowed": False, 
                "message": f"{start_str} : {end_str}"
            }
            
    except Exception as e:
        frappe.log_error(f"[check_closing_time_allowed.py][check_closing_time_allowed] Error: {str(e)}")
        return {"allowed": False, "message": f"Error: {str(e)}"}


def _parse_time(time_value):
    """Helper function to parse time value to datetime.time object"""
    if not time_value:
        return None
    if isinstance(time_value, dtime):
        return time_value
    for fmt in ("%H:%M:%S.%f", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(str(time_value), fmt).time()
        except Exception:
            continue
    return None
