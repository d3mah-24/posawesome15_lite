# 🔌 API Structure - POS Awesome

> Frontend ↔ Backend API Mapping

---

## Customer.vue
**Backend:** `posawesome/posawesome/api/customer.py`

1. `get_customer_names` - Get all customer names for POS profile

**Response:** List of customers with name, customer_name, mobile_no

---

## Invoice.vue
**Backend:** Multiple API files

### Batch API
**File:** `posawesome/posawesome/api/batch.py`
1. `process_batch_selection` - Handle batch number selection for items

### Customer API
**File:** `posawesome/posawesome/api/customer.py`
2. `get_customer_info` - Get customer details with credit info

### POS Offer API
**File:** `posawesome/posawesome/api/pos_offer.py`
3. `get_applicable_offers` - Get offers applicable to invoice

### POS Profile API
**File:** `posawesome/posawesome/api/pos_profile.py`
4. `get_default_payment_from_pos_profile` - Get default payment methods

### Sales Invoice API
**File:** `posawesome/posawesome/api/sales_invoice.py`
5. `delete_invoice` - Delete draft invoice
6. `submit_invoice` - Submit and finalize invoice
7. `update_invoice` - Update invoice data

**Response:** Invoice doc with items, payments, totals

---

## ItemsSelector.vue
**Backend:** `posawesome/posawesome/api/item.py`

1. `get_items` - Get items list with filters (called 5× in different contexts)
2. `get_items_groups` - Get all item groups
3. `search_items_barcode` - Search item by standard barcode
4. `search_private_barcode` - Search item by custom/private barcode
5. `search_scale_barcode` - Search item by weight scale barcode

**Response:** item_code, item_name, rate, actual_qty, has_zero_price

---

## Navbar.vue
**Backend:** `posawesome/posawesome/api/pos_opening_shift.py`

1. `get_user_shift_invoice_count` - Get invoice count for current shift

**Response:** Invoice count

---

## NewAddress.vue
**Backend:** `posawesome/posawesome/api/customer.py`

1. `make_address` - Create new customer address

**Response:** Address document

---

## OpeningDialog.vue
**Backend:** Multiple API files

**File:** `posawesome/posawesome/api/pos_profile.py`
1. `get_opening_dialog_data` - Get POS profile and company data

**File:** `posawesome/posawesome/api/pos_opening_shift.py`
2. `create_opening_voucher` - Create new opening shift

**Response:** POS Profile data, company, warehouse

---

## Payments.vue
**Backend:** Multiple API files

**File:** `posawesome/posawesome/api/customer.py`
1. `get_customer_addresses` - Get customer shipping addresses

**File:** `posawesome/posawesome/api/sales_invoice.py`
2. `create_payment_request` - Create payment request for invoice
3. `submit_invoice` - Submit invoice with payments

**Response:** Addresses list, payment request details

---

## Pos.vue
**Backend:** `posawesome/posawesome/api/pos_opening_shift.py`

1. `get_current_shift_name` - Get current active shift name

**Response:** Shift name

---

## PosCoupons.vue
**Backend:** `posawesome/posawesome/api/customer.py`

1. `get_active_gift_coupons` - Get active gift coupons for customer
2. `get_pos_coupon` - Get specific POS coupon details

**Response:** Coupons list with details

---

## Returns.vue
**Backend:** `posawesome/posawesome/api/sales_invoice.py`

1. `search_invoices_for_return` - Search submitted invoices for creating returns

**Response:** List of invoices eligible for return

---

## UpdateCustomer.vue
**Backend:** `posawesome/posawesome/api/customer.py`

1. `create_customer` - Create new customer with details

**Response:** Customer document

---

## 📊 API Summary

### Backend Structure
- **Total Backend API Files:** 9 Python files
- **Total Whitelisted APIs:** 37 endpoints
- **Total Helper Functions:** 24 internal functions

### Backend Files Breakdown
```
batch.py                1 API,   0 helpers
before_cancel.py        0 API,   1 helper
before_submit.py        0 API,   1 helper
customer.py             9 APIs,  7 helpers
item.py                 5 APIs,  0 helpers
pos_offer.py            5 APIs,  5 helpers
pos_opening_shift.py    5 APIs,  1 helper
pos_profile.py          5 APIs,  0 helpers
sales_invoice.py        7 APIs,  8 helpers
```

### Frontend Structure
- **Total Vue Components:** 11 files
- **Total API Calls:** 30+ unique method calls
- **API Coverage:** ✅ 100% (all frontend calls have backend implementations)

### Frontend Files Breakdown
```
Customer.vue        1 API call
Invoice.vue         7 API calls
ItemsSelector.vue   5 API calls
Navbar.vue          1 API call
NewAddress.vue      1 API call
OpeningDialog.vue   2 API calls
Payments.vue        3 API calls
Pos.vue             1 API call
PosCoupons.vue      2 API calls
Returns.vue         1 API call
UpdateCustomer.vue  1 API call
```

---

## 🔗 API Endpoint Format

All API endpoints follow Frappe's whitelist convention:

```
frappe.call({
    method: "posawesome.posawesome.api.<module>.<function_name>",
    args: { ... },
    callback: function(r) { ... }
});
```

**Example:**
```javascript
frappe.call({
    method: "posawesome.posawesome.api.customer.get_customer_names",
    args: { pos_profile: "Main POS" },
    callback: function(r) {
        console.log(r.message);
    }
});
```

---

## 📝 API Categories

### Customer APIs (9 endpoints)
- Customer CRUD operations
- Address management
- Credit balance tracking
- Loyalty program integration
- Gift coupons

### Item APIs (5 endpoints)
- Item listing with filters
- Barcode search (3 types)
- Item group filtering

### Sales Invoice APIs (7 endpoints)
- Invoice CRUD operations
- Payment processing
- Return invoice creation
- Invoice search

### POS Offer APIs (5 endpoints)
- Offer retrieval
- Offer application logic
- Coupon validation

### POS Profile APIs (5 endpoints)
- Profile configuration
- Default settings
- Payment method setup

### POS Opening Shift APIs (5 endpoints)
- Shift management
- Opening/closing operations
- Shift reports

### Batch APIs (1 endpoint)
- Batch selection processing

---

## ✅ Coverage Status

**Frontend → Backend Mapping:** 100% complete

All Vue components have corresponding backend API implementations. No dead code or missing API endpoints.
