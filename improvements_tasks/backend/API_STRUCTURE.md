# 📡 POS Awesome API Structure

**Generated:** October 20, 2025  
**Source:** `/posawesome/public/js/posapp/api_mapper.js`  
**Version:** 2.0

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| **Total APIs** | 27 |
| **API Categories** | 7 |
| **Backend Files** | ~25 |
| **Frontend Components Using APIs** | 12 |

### APIs by Category

| Category | Count | % |
|----------|-------|---|
| Customer APIs | 10 | 37% |
| POS Opening Shift APIs | 6 | 22% |
| Sales Invoice APIs | 5 | 19% |
| Item APIs | 4 | 15% |
| Frappe Standard | 3 | 11% |
| POS Offer APIs | 2 | 7% |
| POS Profile APIs | 1 | 4% |

---

## 🏗️ Backend Directory Structure

```
posawesome/
├── api/
│   ├── __init__.py
│   │
│   ├── sales_invoice/
│   │   ├── __init__.py
│   │   ├── create.py
│   │   ├── update.py
│   │   ├── submit.py
│   │   ├── delete.py
│   │   └── get_return.py
│   │
│   ├── customer/
│   │   ├── __init__.py
│   │   ├── get_customer.py
│   │   ├── get_many_customers.py
│   │   ├── create_customer.py
│   │   ├── update_customer.py
│   │   ├── create_customer_address.py
│   │   ├── get_customer_credit.py
│   │   ├── get_many_customer_addresses.py
│   │   └── get_customer_coupons.py
│   │
│   ├── pos_profile/
│   │   ├── __init__.py
│   │   ├── get_default_payment_from_pos_profile.py
│   │   └── get_opening_dialog_data.py
│   │
│   ├── item/
│   │   ├── __init__.py
│   │   ├── get_items.py
│   │   ├── get_items_groups.py
│   │   ├── get_barcode_item.py
│   │   └── batch.py
│   │
│   └── pos_offer/
│       ├── __init__.py
│       ├── get_applicable_offers.py
│       └── get_offers_for_profile.py
│
└── doctype/
    ├── pos_opening_shift/
    │   └── pos_opening_shift.py
    │
    └── pos_closing_shift/
        └── pos_closing_shift.py
```

---

## 📋 API Method Paths

### Sales Invoice APIs (5)
```
posawesome.posawesome.api.sales_invoice.create.create_invoice
posawesome.posawesome.api.sales_invoice.update.update_invoice
posawesome.posawesome.api.sales_invoice.submit.submit_invoice
posawesome.posawesome.api.sales_invoice.delete.delete_invoice
posawesome.posawesome.api.sales_invoice.get_return.get_invoices_for_return
```

### Customer APIs (10)
```
posawesome.posawesome.api.customer.get_customer.get_customer
posawesome.posawesome.api.customer.get_many_customers.get_many_customers
posawesome.posawesome.api.customer.get_many_customers.get_customers_count
posawesome.posawesome.api.customer.create_customer.create_customer
posawesome.posawesome.api.customer.update_customer.update_customer
posawesome.posawesome.api.customer.create_customer_address.create_customer_address
posawesome.posawesome.api.customer.get_customer_credit.get_customer_credit
posawesome.posawesome.api.customer.get_many_customer_addresses.get_many_customer_addresses
posawesome.posawesome.api.customer.get_customer_coupons.get_customer_coupons
posawesome.posawesome.api.customer.get_customer_coupons.get_pos_coupon
```

### POS Profile APIs (1)
```
posawesome.posawesome.api.pos_profile.get_default_payment_from_pos_profile.get_default_payment_from_pos_profile
```

### Item APIs (4)
```
posawesome.posawesome.api.item.get_items.get_items
posawesome.posawesome.api.item.get_items_groups.get_items_groups
posawesome.posawesome.api.item.get_barcode_item.get_barcode_item
posawesome.posawesome.api.item.batch.process_batch_selection
```

### POS Offer APIs (2)
```
posawesome.posawesome.api.pos_offer.get_applicable_offers.get_applicable_offers
posawesome.posawesome.api.pos_offer.get_offers_for_profile.get_offers_for_profile
```

### POS Opening Shift APIs (6)
```
posawesome.posawesome.api.pos_profile.get_opening_dialog_data.get_opening_dialog_data
posawesome.posawesome.doctype.pos_opening_shift.pos_opening_shift.create_opening_voucher
posawesome.posawesome.doctype.pos_opening_shift.pos_opening_shift.get_current_shift_name
posawesome.posawesome.doctype.pos_opening_shift.pos_opening_shift.get_user_shift_invoice_count
posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening
posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift
```

### Frappe Standard APIs (3)
```
frappe.client.get
frappe.client.delete
frappe.ping
```

---

## 📌 Notes

- **Source of Truth:** `/posawesome/public/js/posapp/api_mapper.js`
- **Unified Barcode:** `get_barcode_item.py` handles all barcode types (standard, scale, private)
- **Frappe APIs:** Built-in framework APIs, no custom code needed

---

*Last Updated: October 20, 2025*
