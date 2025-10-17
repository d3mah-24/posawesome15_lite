# -*- coding: utf-8 -*-
"""
Customer API Module
Consolidated API endpoints for customer management following RESTful conventions

This module provides a clean, organized API structure:
- get_customer: Retrieve single customer details
- get_many_customers: Search and retrieve multiple customers  
- post_customer: Create new customer
- update_customer: Update existing customer
- delete_customer: Delete customer (hard delete)
- soft_delete_customer: Disable customer (soft delete)
- get_customer_credit: Get customer credit information
- get_customer_addresses: Get customer address information
- get_customer_coupons: Get customer coupons and gift cards

Legacy API endpoints are maintained for backward compatibility but marked as deprecated.
"""

from __future__ import unicode_literals

# Import all modern API functions
from .get_customer import get_customer
from .get_many_customers import get_many_customers, get_customers_count
from .post_customer import post_customer
from .update_customer import update_customer, patch_customer
from .delete_customer import delete_customer, soft_delete_customer
from .get_customer_credit import get_customer_credit, get_customer_credit_summary
from .get_customer_addresses import (
    get_customer_addresses, 
    get_customer_primary_address,
    get_customer_shipping_addresses
)
from .get_customer_coupons import get_customer_coupons, get_active_gift_coupons
from .get_customer_balance import get_customer_balance, get_customer_outstanding_invoices

# Backward compatibility functions - wrapper functions for legacy API calls
def get_customer_names(*args, **kwargs):
    """Legacy wrapper for get_many_customers"""
    return get_many_customers(*args, **kwargs)

def get_customers(*args, **kwargs):
    """Legacy wrapper for get_many_customers"""
    return get_many_customers(*args, **kwargs)

def get_customer_info(*args, **kwargs):
    """Legacy wrapper for get_customer"""
    return get_customer(*args, **kwargs)

def get_available_credit(*args, **kwargs):
    """Legacy wrapper for get_customer_credit"""
    return get_customer_credit(*args, **kwargs)

def create_customer(*args, **kwargs):
    """Legacy wrapper for post_customer"""
    return post_customer(*args, **kwargs)

# get_customer_balance is already imported above, no wrapper needed


# API Mapping for documentation and reference
API_ENDPOINTS = {
    # Modern RESTful APIs (Recommended)
    "modern": {
        "GET /api/customer/{id}": "posawesome.posawesome.api.customer.get_customer",
        "GET /api/customers": "posawesome.posawesome.api.customer.get_many_customers", 
        "POST /api/customer": "posawesome.posawesome.api.customer.post_customer",
        "PUT /api/customer/{id}": "posawesome.posawesome.api.customer.update_customer",
        "PATCH /api/customer/{id}": "posawesome.posawesome.api.customer.patch_customer",
        "DELETE /api/customer/{id}": "posawesome.posawesome.api.customer.delete_customer",
        "POST /api/customer/{id}/disable": "posawesome.posawesome.api.customer.soft_delete_customer",
        "GET /api/customer/{id}/credit": "posawesome.posawesome.api.customer.get_customer_credit",
        "GET /api/customer/{id}/addresses": "posawesome.posawesome.api.customer.get_customer_addresses",
        "GET /api/customer/{id}/coupons": "posawesome.posawesome.api.customer.get_customer_coupons",
        "GET /api/customer/{id}/balance": "posawesome.posawesome.api.customer.get_customer_balance"
    },
    
    # Legacy APIs replaced by modern equivalents - backward compatibility maintained through function aliases
    "legacy_replaced_by": {
        "get_customer_names": "get_many_customers",
        "get_customers": "get_many_customers", 
        "get_customer_info": "get_customer",
        "get_available_credit": "get_customer_credit",
        "create_customer": "post_customer",
    }
}

# Quick reference for function usage
FUNCTION_MAPPING = {
    # Customer CRUD Operations
    "get_single_customer": get_customer,
    "search_customers": get_many_customers,
    "create_new_customer": post_customer,
    "modify_customer": update_customer,
    "partial_update_customer": patch_customer,
    "remove_customer": delete_customer,
    "disable_customer": soft_delete_customer,
    
    # Customer Related Data
    "customer_credit_info": get_customer_credit,
    "customer_addresses_list": get_customer_addresses,
    "customer_coupons_list": get_customer_coupons,
    "customer_balance_info": get_customer_balance,
    
    # Utility Functions
    "count_customers": get_customers_count,
    "customer_credit_summary": get_customer_credit_summary,
    "primary_address": get_customer_primary_address,
    "shipping_addresses": get_customer_shipping_addresses,
    "active_gift_coupons": get_active_gift_coupons,
}


def get_api_info():
    """
    Get information about available customer APIs.
    
    Returns:
        dict: API endpoints and function mappings
    """
    return {
        "endpoints": API_ENDPOINTS,
        "functions": list(FUNCTION_MAPPING.keys()),
        "version": "2.0",
        "description": "Modern RESTful Customer API with backward compatibility"
    }
