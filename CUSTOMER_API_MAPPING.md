# 🗂️ Customer API Mapping - Vue.js to Python Functions

**Analysis Date:** October 17, 2025  
**Format:** Vue Component → Python Functions Called

---

## 📋 Active Mappings (Used Functions)

### Customer.vue
- `get_many_customers.get_many_customers()`
- `get_many_customers.get_customers_count()`

### UpdateCustomer.vue  
- `create_customer.create_customer()`
- `update_customer.update_customer()`

### Invoice.vue
- `get_customer.get_customer()`

### Payments.vue
- `get_customer_credit.get_customer_credit()`
- ✅ `get_many_customer_addresses.get_many_customer_addresses()` **(Fixed)**

### NewAddress.vue
- ✅ `create_customer_address.create_customer_address()` **(Fixed)**

### PosCoupons.vue
- `get_customer_coupons.get_customer_coupons()`
- `get_customer_coupons.get_pos_coupon()`

---

## ✅ All Files Now Used (Cleanup Complete)

**All unused files have been deleted:**
- ❌ ~~get_customer_address.py~~ (Deleted)
- ❌ ~~get_primary_customer_address.py~~ (Deleted) 
- ❌ ~~get_shipping_customer_address.py~~ (Deleted)
- ❌ ~~update_customer_address.py~~ (Deleted)
- ❌ ~~delete_customer_address.py~~ (Deleted)
- ❌ ~~get_customer_balance.py~~ (Deleted)
- ❌ ~~get_customer_groups.py~~ (Deleted)

---

## 🔧 Helper Functions (No Direct Vue Calls)

### create_customer.py
- `_parse_birthday()`
- `_create_gift_coupon()`

### update_customer.py
- `patch_customer()`

### get_customer_credit.py
- `get_customer_credit_summary()`
- `_get_invoice_credits()`
- `_get_advance_credits()`

### get_customer_coupons.py
- `get_active_gift_coupons()`
- `_get_gift_coupons()`
- `_get_loyalty_coupons()`
- `_validate_coupon_code()`

---

## ✅ Issues Fixed

### Fixed Paths ✅

**NewAddress.vue** - Line 119: **FIXED**
```javascript
// ✅ Updated to correct path
method: 'posawesome.posawesome.api.customer.create_customer_address.create_customer_address'
```

**Payments.vue** - Line 870: **FIXED**
```javascript
// ✅ Updated to correct path
method: "posawesome.posawesome.api.customer.get_many_customer_addresses.get_many_customer_addresses"
```

---

## 📊 Updated Summary Statistics

| Category | Count |
|----------|-------|
| **Vue Components Using APIs** | 6 |
| **Active Python Functions** | 13 |
| **Unused Python Functions** | 0 ✅ |
| **Helper Functions** | 7 |
| **Files with Wrong Paths** | 0 ✅ |
| **Python Files Remaining** | 8 |

---

**Created:** October 17, 2025  
**Updated:** October 17, 2025  
**Status:** ✅ OPTIMIZED AND CLEAN �