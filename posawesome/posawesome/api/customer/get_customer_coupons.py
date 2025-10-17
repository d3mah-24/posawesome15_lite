# -*- coding: utf-8 -*-
"""
Get Customer Coupons API
Handles retrieving customer gift coupons and promotional codes
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from datetime import datetime, date


@frappe.whitelist() 
def get_customer_coupons(customer_id, coupon_type=None, active_only=True):
    """
    Get all coupons/gift cards associated with a customer.
    
    Args:
        customer_id (str): Customer ID/name (required)
        coupon_type (str): Filter by coupon type ('Gift Coupon', 'Loyalty', etc.)
        active_only (bool): Return only active/unused coupons (default: True)
        
    Returns:
        list: List of coupon dictionaries
    """
    try:
        if not customer_id:
            frappe.throw(_("Customer ID is required"))
        
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer not found: {0}").format(customer_id))
        
        # Get gift coupons
        gift_coupons = _get_gift_coupons(customer_id, active_only)
        
        # Get loyalty coupons if loyalty module is available
        loyalty_coupons = _get_loyalty_coupons(customer_id, active_only)
        
        # Combine all coupons
        all_coupons = gift_coupons + loyalty_coupons
        
        # Filter by coupon type if specified
        if coupon_type:
            all_coupons = [coupon for coupon in all_coupons if coupon["type"] == coupon_type]
        
        # Sort by creation date (newest first)
        all_coupons.sort(key=lambda x: x.get("creation_date", ""), reverse=True)
        
        frappe.logger().debug(f"Found {len(all_coupons)} coupons for customer {customer_id}")
        
        return all_coupons
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_coupons: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error retrieving customer coupons: {0}").format(str(e)))


@frappe.whitelist()
def get_active_gift_coupons(customer_id=None):
    """
    Get all active gift coupons, optionally filtered by customer.
    
    Args:
        customer_id (str): Customer ID/name (optional)
        
    Returns:
        list: List of active gift coupon dictionaries
    """
    try:
        filters = {
            "docstatus": 1,
            "used": 0,
        }
        
        if customer_id:
            filters["customer"] = customer_id
        
        # Check if Gift Coupon doctype exists
        if not frappe.db.exists("DocType", "POS Gift Coupon"):
            return []
        
        coupons = frappe.get_all(
            "POS Gift Coupon",
            filters=filters,
            fields=[
                "name",
                "coupon_code", 
                "customer",
                "balance",
                "used",
                "creation",
                "expiry_date",
                "company"
            ],
            order_by="creation desc"
        )
        
        active_coupons = []
        today = date.today()
        
        for coupon in coupons:
            # Check if coupon is not expired
            is_expired = False
            if coupon.expiry_date:
                if isinstance(coupon.expiry_date, str):
                    try:
                        expiry_date = datetime.strptime(coupon.expiry_date, '%Y-%m-%d').date()
                        is_expired = expiry_date < today
                    except ValueError:
                        is_expired = False
                else:
                    is_expired = coupon.expiry_date < today
            
            if not is_expired and coupon.balance > 0:
                active_coupons.append({
                    "type": "Gift Coupon",
                    "name": coupon.name,
                    "code": coupon.coupon_code,
                    "customer": coupon.customer,
                    "balance": coupon.balance,
                    "expiry_date": coupon.expiry_date,
                    "creation_date": coupon.creation,
                    "company": coupon.company,
                    "status": "Active"
                })
        
        return active_coupons
        
    except Exception as e:
        frappe.logger().error(f"Error in get_active_gift_coupons: {str(e)}")
        return []


def _get_gift_coupons(customer_id, active_only=True):
    """
    Internal function to get gift coupons for a customer.
    
    Returns:
        list: List of gift coupon dictionaries
    """
    try:
        # Check if Gift Coupon doctype exists
        if not frappe.db.exists("DocType", "POS Gift Coupon"):
            return []
        
        filters = {
            "customer": customer_id,
            "docstatus": 1
        }
        
        if active_only:
            filters["used"] = 0
        
        coupons = frappe.get_all(
            "POS Gift Coupon", 
            filters=filters,
            fields=[
                "name",
                "coupon_code",
                "balance", 
                "used",
                "creation",
                "expiry_date",
                "company"
            ],
            order_by="creation desc"
        )
        
        gift_coupons = []
        today = date.today()
        
        for coupon in coupons:
            # Determine status
            status = "Used" if coupon.used else "Active"
            
            # Check expiry
            is_expired = False
            if coupon.expiry_date:
                if isinstance(coupon.expiry_date, str):
                    try:
                        expiry_date = datetime.strptime(coupon.expiry_date, '%Y-%m-%d').date()
                        is_expired = expiry_date < today
                    except ValueError:
                        is_expired = False
                else:
                    is_expired = coupon.expiry_date < today
            
            if is_expired and not coupon.used:
                status = "Expired"
            
            # Skip expired/used coupons if active_only is True
            if active_only and status != "Active":
                continue
            
            gift_coupons.append({
                "type": "Gift Coupon", 
                "name": coupon.name,
                "code": coupon.coupon_code,
                "customer": customer_id,
                "balance": coupon.balance,
                "expiry_date": coupon.expiry_date,
                "creation_date": coupon.creation,
                "company": coupon.company,
                "status": status
            })
        
        return gift_coupons
        
    except Exception as e:
        frappe.logger().warning(f"Error getting gift coupons: {e}")
        return []


def _get_loyalty_coupons(customer_id, active_only=True):
    """
    Internal function to get loyalty coupons for a customer.
    
    Returns:
        list: List of loyalty coupon dictionaries  
    """
    try:
        # Check if Loyalty Program and related doctypes exist
        if not frappe.db.exists("DocType", "Loyalty Point Entry"):
            return []
        
        customer_doc = frappe.get_cached_doc("Customer", customer_id)
        if not customer_doc.loyalty_program:
            return []
        
        # Get loyalty point entries
        filters = {
            "customer": customer_id,
            "loyalty_program": customer_doc.loyalty_program,
            "docstatus": 1
        }
        
        if active_only:
            filters["expiry_date"] = [">=", date.today()]
        
        loyalty_entries = frappe.get_all(
            "Loyalty Point Entry",
            filters=filters,
            fields=[
                "name",
                "loyalty_points", 
                "expiry_date",
                "posting_date",
                "company"
            ],
            order_by="posting_date desc"
        )
        
        loyalty_coupons = []
        for entry in loyalty_entries:
            if entry.loyalty_points > 0:  # Only positive point entries
                status = "Active"
                if entry.expiry_date and entry.expiry_date < date.today():
                    status = "Expired"
                
                if active_only and status != "Active":
                    continue
                
                loyalty_coupons.append({
                    "type": "Loyalty Points",
                    "name": entry.name,
                    "code": f"LP-{entry.name}",
                    "customer": customer_id,
                    "balance": entry.loyalty_points,
                    "expiry_date": entry.expiry_date,
                    "creation_date": entry.posting_date,
                    "company": entry.company,
                    "status": status
                })
        
        return loyalty_coupons
        
    except Exception as e:
        frappe.logger().warning(f"Error getting loyalty coupons: {e}")
        return []


@frappe.whitelist()
def get_pos_coupon(coupon_code, customer_id=None, company=None):
    """
    Validate and get specific POS coupon details.
    
    Args:
        coupon_code (str): Coupon code to validate (required)
        customer_id (str): Customer ID for validation (optional)
        company (str): Company for validation (optional)
        
    Returns:
        dict: Coupon details if valid, error message if invalid
    """
    try:
        if not coupon_code:
            frappe.throw(_("Coupon code is required"))
            
        coupon_code = coupon_code.strip()
        
        # Check if coupon exists and is valid
        coupon_details = _validate_coupon_code(coupon_code, customer_id, company)
        
        return coupon_details
        
    except Exception as e:
        frappe.logger().error(f"Error in get_pos_coupon: {str(e)}")
        return {
            "valid": False,
            "message": str(e),
            "coupon_code": coupon_code
        }


def _validate_coupon_code(coupon_code, customer_id=None, company=None):
    """
    Validate coupon code and return details.
    
    Args:
        coupon_code (str): Coupon code to validate
        customer_id (str): Customer ID for validation
        company (str): Company for validation
        
    Returns:
        dict: Coupon validation result with details
    """
    try:
        # Check if POS Coupon doctype exists
        if not frappe.db.exists("DocType", "POS Coupon"):
            return {
                "valid": False,
                "message": _("POS Coupon module is not available"),
                "coupon_code": coupon_code
            }
        
        # Find coupon by code
        filters = {"coupon_code": coupon_code}
        if company:
            filters["company"] = company
            
        coupon = frappe.db.get_value(
            "POS Coupon", 
            filters,
            ["name", "customer", "coupon_type", "coupon_amount", "used", "expiry_date", "company"],
            as_dict=True
        )
        
        if not coupon:
            return {
                "valid": False,
                "message": _("Invalid coupon code: {0}").format(coupon_code),
                "coupon_code": coupon_code
            }
        
        # Check if already used
        if coupon.used:
            return {
                "valid": False,
                "message": _("Coupon has already been used"),
                "coupon_code": coupon_code
            }
        
        # Check expiry date
        if coupon.expiry_date and coupon.expiry_date < date.today():
            return {
                "valid": False,
                "message": _("Coupon has expired"),
                "coupon_code": coupon_code,
                "expiry_date": coupon.expiry_date
            }
        
        # Check customer match if specified
        if customer_id and coupon.customer != customer_id:
            return {
                "valid": False,
                "message": _("Coupon is not valid for this customer"),
                "coupon_code": coupon_code
            }
        
        # Valid coupon
        return {
            "valid": True,
            "message": _("Valid coupon"),
            "coupon_code": coupon_code,
            "coupon_name": coupon.name,
            "customer": coupon.customer,
            "coupon_type": coupon.coupon_type,
            "coupon_amount": coupon.coupon_amount,
            "company": coupon.company,
            "expiry_date": coupon.expiry_date
        }
        
    except Exception as e:
        frappe.logger().error(f"Error validating coupon: {e}")
        return {
            "valid": False,
            "message": _("Error validating coupon: {0}").format(str(e)),
            "coupon_code": coupon_code
        }