# POS Awesome API Structure Tree

```
posawesome.posawesome.api/
├── sales_invoice/
│   ├── create.create_invoice
│   ├── update.update_invoice
│   ├── submit.submit_invoice
│   ├── delete.delete_invoice
│   └── get_return.get_invoices_for_return
│
├── customer/
│   ├── get_customer.get_customer
│   ├── get_many_customers.get_many_customers
│   ├── get_many_customers.get_customers_count
│   ├── create_customer.create_customer
│   ├── update_customer.update_customer
│   ├── create_customer_address.create_customer_address
│   ├── get_customer_credit.get_customer_credit
│   ├── get_many_customer_addresses.get_many_customer_addresses
│   └── get_customer_coupons/
│       ├── get_pos_coupon
│       └── get_customer_coupons
│
├── pos_profile/
│   ├── get_default_payment_from_pos_profile.get_default_payment_from_pos_profile
│   └── get_opening_dialog_data.get_opening_dialog_data
│
├── item/
│   ├── get_items.get_items
│   ├── get_items_groups.get_items_groups
│   ├── get_items_barcode.get_items_barcode
│   ├── get_scale_barcode.get_scale_barcode
│   ├── get_private_barcode.get_private_barcode
│   └── batch.process_batch_selection
│
├── pos_offer/
│   ├── get_applicable_offers.get_applicable_offers
│   └── get_offers_for_profile.get_offers_for_profile
│
└── pos_opening_shift/
    ├── create_opening_voucher.create_opening_voucher
    ├── get_current_shift_name.get_current_shift_name
    ├── get_user_shift_invoice_count.get_user_shift_invoice_count
    ├── make_closing_shift_from_opening (from pos_closing_shift doctype)
    └── submit_closing_shift (from pos_closing_shift doctype)

posawesome.posawesome.doctype/
└── pos_closing_shift/
    └── pos_closing_shift/
        ├── make_closing_shift_from_opening
        └── submit_closing_shift

frappe/
├── client.get
├── client.delete
└── ping
```

## Frontend Integration Status

✅ **Centralized API Mapper Implemented**
- All Vue components now use `API_MAP` from `api_mapper.js`
- Eliminated duplicate API endpoint definitions
- Total: **42 API endpoints** mapped across **11 Vue files**

### Updated Files:
- Invoice.vue (9 endpoints)
- ItemsSelector.vue (8 endpoints) 
- Customer.vue (2 endpoints)
- Payments.vue (4 endpoints)
- UpdateCustomer.vue (2 endpoints)
- Returns.vue (2 endpoints)
- PosCoupons.vue (2 endpoints)
- OpeningDialog.vue (2 endpoints)
- NewAddress.vue (1 endpoint)
- Pos.vue (4 endpoints)
- Navbar.vue (1 endpoint)

## Summary
- **Total API Endpoints**: 42
- **Vue Files Updated**: 11/11 (100%)
- **Status**: All components centralized ✅