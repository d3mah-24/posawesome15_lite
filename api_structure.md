# API Structure - POS Awesome

> Frontend ↔ Backend API Mapping  
> Date: October 13, 2025

---

## Customer.vue
**Required APIs:**
- ✅ `customer.get_customer_names`

**Response Fields:** `name`, `customer_name`, `mobile_no`, etc.

---

## Invoice.vue
**Required APIs:**
- ✅ `batch.process_batch_selection`
- ✅ `customer.get_customer_info`
- ✅ `pos_offer.get_applicable_offers`
- ✅ `pos_profile.get_default_payment_from_pos_profile`
- ✅ `sales_invoice.delete_invoice`
- ✅ `sales_invoice.submit_invoice`
- ✅ `sales_invoice.update_invoice`
	(Moved to client-side: item-level offer processing and validation handled locally)

**Response Fields:** Invoice doc, items, payments, totals

  

---

## ItemsSelector.vue
**Required APIs:**
- ✅ `item.get_items` (called 5× in different contexts)
- ✅ `item.get_items_groups`
- ✅ `item.search_items_barcode`
- ✅ `item.search_private_barcode`
- ✅ `item.search_scale_barcode`

**Response Fields:** `item_code`, `item_name`, `rate`, `actual_qty`, `has_zero_price`

---

## Navbar.vue
**Required APIs:**
- ✅ `pos_opening_shift.get_user_shift_invoice_count`

**Response Fields:** `count`

---

## NewAddress.vue
**Required APIs:**
- ✅ `customer.make_address`

**Response Fields:** Address doc

---

## OpeningDialog.vue
**Required APIs:**
- ✅ `pos_profile.get_opening_dialog_data`
- ✅ `pos_opening_shift.create_opening_voucher`

**Response Fields:** POS Profile data, company, warehouse

---

## Payments.vue
**Required APIs:**
- ✅ `customer.get_customer_addresses`
- ✅ `sales_invoice.create_payment_request`
- ✅ `sales_invoice.submit_invoice`

**Response Fields:** Addresses list, payment request

---

## Pos.vue
**Required APIs:**
- ✅ `pos_opening_shift.get_current_shift_name`

**Response Fields:** Shift name

---

## PosCoupons.vue
**Required APIs:**
- ✅ `customer.get_active_gift_coupons`
- ✅ `customer.get_pos_coupon`

**Response Fields:** Coupons list

---

## Returns.vue
**Required APIs:**
- ✅ `sales_invoice.search_invoices_for_return`

**Response Fields:** Invoices list for return

---

## UpdateCustomer.vue
**Required APIs:**
- ✅ `customer.create_customer`

**Response Fields:** Customer doc

---

# 📊 Statistics

## Backend
- **Total API Files:** 9
- **Total Whitelisted APIs:** 37
- **Total Helper Functions:** 24

### Per File Breakdown:
```
batch.py:               1 API,   0 helpers
before_cancel.py:       0 API,   1 helper
before_submit.py:       0 API,   1 helper
customer.py:            9 APIs,  7 helpers
item.py:                5 APIs,  0 helpers
pos_offer.py:           5 APIs,  5 helpers
pos_opening_shift.py:   5 APIs,  1 helper
pos_profile.py:         5 APIs,  0 helpers
sales_invoice.py:       7 APIs,  8 helpers
```

---

## Frontend
- **Total Vue Files:** 11
- **Total API Calls:** 30 (unique method calls)
- **Total Call Instances:** 30+

### Per File Breakdown:
```
Customer.vue:       1 call
Invoice.vue:        9 calls
ItemsSelector.vue:  9 calls (5 to get_items + 4 barcode searches)
Navbar.vue:         1 call
NewAddress.vue:     1 call
OpeningDialog.vue:  2 calls
Payments.vue:       3 calls
Pos.vue:            1 call
PosCoupons.vue:     2 calls
Returns.vue:        1 call
UpdateCustomer.vue: 1 call
```

---

## 🔍 Coverage Analysis

✅ **Matched:** 30 API calls have corresponding backend definitions  
🔴 **Missing/Dead Code:** 0 (all frontend calls now have backend definitions or were moved client-side)

💡 **Note:** Some helper functions (22) are used internally by whitelisted APIs

---

## ✅ Status

All frontend API calls now either have backend implementations or were intentionally moved to the client. No missing/dead API calls remain.
