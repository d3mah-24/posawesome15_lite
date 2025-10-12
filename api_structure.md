# API Structure - POS Awesome

> **Frontend to Backend API Mapping**  
> **Date:** October 12, 2025

---

## Navbar.vue
- `posawesome.posawesome.api.pos_opening_shift.get_user_shift_invoice_count`

---

## Customer.vue
- `posawesome.posawesome.api.customer.get_customer_names`

---

## Invoice.vue
- `posawesome.posawesome.api.sales_invoice_item.calculate_item_discount_amount`
- `posawesome.posawesome.api.sales_invoice.delete_invoice`
- `posawesome.posawesome.api.sales_invoice.update_invoice`
- `posawesome.posawesome.api.sales_invoice.update_invoice`
- `posawesome.posawesome.api.pos_profile.get_default_payment_from_pos_profile`
- `posawesome.posawesome.api.sales_invoice_item.validate_invoice_items`
- `posawesome.posawesome.api.sales_invoice.get_draft_invoices`
- `posawesome.posawesome.api.customer.get_customer_info`
- `posawesome.posawesome.api.batch.process_batch_selection`
- `posawesome.posawesome.api.pos_offer.get_applicable_offers`
- `posawesome.posawesome.api.pos_offer.process_item_offer`
- `posawesome.posawesome.api.sales_invoice.submit_invoice`

---

## ItemsSelector.vue
- `posawesome.posawesome.api.item.search_scale_barcode`
- `posawesome.posawesome.api.item.search_private_barcode`
- `posawesome.posawesome.api.item.search_items_barcode`
- `posawesome.posawesome.api.item.get_items`
- `posawesome.posawesome.api.item.get_items`
- `posawesome.posawesome.api.item.get_items`
- `posawesome.posawesome.api.item.get_items`
- `posawesome.posawesome.api.item.get_items`
- `posawesome.posawesome.api.item.get_items_groups`

---

## NewAddress.vue
- `posawesome.posawesome.api.customer.make_address`

---

## OpeningDialog.vue
- `posawesome.posawesome.api.pos_profile.get_opening_dialog_data`
- `posawesome.posawesome.api.pos_opening_shift.create_opening_voucher`

---

## Payments.vue
- `posawesome.posawesome.api.sales_invoice.submit_invoice`
- `posawesome.posawesome.api.customer.get_available_credit`
- `posawesome.posawesome.api.customer.get_customer_addresses`
- `posawesome.posawesome.api.sales_invoice.create_payment_request`

---

## Pos.vue
- `posawesome.posawesome.api.pos_opening_shift.get_current_shift_name`
- `posawesome.posawesome.api.pos_opening_shift.get_current_shift_name`
- `posawesome.posawesome.api.pos_offer.get_offers_for_profile`

---

## PosCoupons.vue
- `posawesome.posawesome.api.customer.get_pos_coupon`
- `posawesome.posawesome.api.customer.get_active_gift_coupons`

---

## Returns.vue
- `posawesome.posawesome.api.sales_invoice.search_invoices_for_return`

---

## UpdateCustomer.vue
- `posawesome.posawesome.api.customer.create_customer`

---

**Total APIs:** 37  
**Total Files:** 11
