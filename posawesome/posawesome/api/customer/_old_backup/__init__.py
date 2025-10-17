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

# Import legacy functions for backward compatibility (marked as deprecated)
from .customer_names import get_customer_names, get_customers  # Modern replacement available
from .customer_info import get_customer_info  # Use get_customer instead
from .available_credit import get_available_credit  # Use get_customer_credit instead
from .customer_addresses import get_customer_addresses as legacy_get_customer_addresses  # Use get_customer_addresses instead
from .create_customer import create_customer as legacy_create_customer  # Use post_customer instead


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
        "GET /api/customer/{id}/coupons": "posawesome.posawesome.api.customer.get_customer_coupons"
    },
    
    # Legacy APIs (Deprecated but maintained for compatibility)
    "legacy": {
        "get_customer_names": "posawesome.posawesome.api.customer.customer_names.get_customer_names",
        "get_customers": "posawesome.posawesome.api.customer.customer_names.get_customers",
        "get_customer_info": "posawesome.posawesome.api.customer.customer_info.get_customer_info", 
        "get_available_credit": "posawesome.posawesome.api.customer.available_credit.get_available_credit",
        "create_customer": "posawesome.posawesome.api.customer.create_customer.create_customer",
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
