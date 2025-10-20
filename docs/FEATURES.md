# ✨ Features - POS Awesome Lite

> Complete feature list for POS Awesome

---

## 💰 Sales & Invoices

- Create, update, and submit sales invoices
- Multiple payment modes (Cash, Card, Bank Transfer, Phone/M-PESA)
- Split payments across multiple payment methods
- Payment request creation (M-PESA/Phone payments)
- Invoice returns with item selection
- Draft invoices (save and resume later)
- Item-level discount (percentage/amount)
- Write-off change amount
- Credit sales with customer credit tracking
- Change amount calculation (cashback)

---

## �️ Easy Item Discount Control

Complete discount management system with flexible UI controls and validation:

### Display Control Settings
- **`posa_display_discount_percentage`** - Show/hide discount % column in POS interface
- **`posa_display_discount_amount`** - Show/hide discount amount column in POS interface
- **`posa_item_discount_settings`** - Master toggle for all discount features

### User Permission Settings  
- **`posa_allow_user_to_edit_item_discount`** - Allow cashiers to modify item discounts
- **`posa_item_max_discount_allowed`** - Maximum discount percentage limit (prevents over-discounting)

### Key Features
- **Dual Input Methods:** Edit discount by percentage OR by discounted price
- **Smart Validation:** Both input methods respect the maximum discount limit
- **Real-time Calculation:** Automatic conversion between percentage and amount
- **Invoice Integration:** `posa_item_discount_total` field shows total discount amount
- **Print Format Ready:** Easily display total discounts in invoice templates

### How It Works
1. **Show/Hide Columns:** Control which discount columns appear in the POS interface
2. **Input Validation:** Whether editing discount % or price, system enforces max limit
3. **Automatic Sync:** Change discount % → price updates, change price → % updates  
4. **Total Tracking:** All item discounts sum to `posa_item_discount_total` for reporting

---

## �🎯 Offers & Coupons

- **POS Offers** - Apply on: Item, Item Group, Brand, Transaction
- **Offer Types:** Product/Give Product, Discount (%), Discount (Amount)
- Min/Max quantity and amount triggers
- Date-based offer validity (from/to)
- Auto-apply offers or manual selection
- Coupon-based offers
- Gift coupons from referral codes
- Replace item or replace cheapest item options

---

## 👥 Customer Management

- Customer search and quick selection
- Create new customers with full details
- Customer addresses (shipping/billing)
- Manage multiple addresses
- Customer referral codes and campaigns
- Customer credit balance tracking
- Loyalty program integration
- Loyalty points redemption
- Tax ID support
- Mobile number tracking

---

## 📦 Inventory

- Real-time stock availability display
- Batch number selection and tracking
- Serial number support
- Multi-barcode support:
  - Standard EAN/UPC barcodes
  - Weight scale barcodes (prefix-based)
  - Private/custom barcodes
- Item search (name/code/barcode)
- Item group filtering
- Price list integration
- Item images display

---

## 🔐 Shift Management

- **POS Opening Shift** - Opening balance entry
- **POS Closing Shift** - End-of-day reconciliation
- Cash denomination counting
- Payment mode-wise summary
- Shift-wise invoice tracking
- Invoice count per shift
- Shift reports and statistics

---

## 💳 Payment Features

- Payment mode configuration
- Phone payment request (M-PESA/Mobile Money)
- Loyalty points payment
- Customer credit redemption
- Change amount handling
- Write-off excess/shortage
- Payment reference tracking

---

## 🎨 User Interface

- **Frontend:** Vue 3.4.21 + Vuetify 3.6.9
- Responsive and modern design
- Split view (items selector + invoice)
- Compact table layouts
- Real-time calculations
- Hardware barcode scanner support (onScan.js)
- Keyboard shortcuts (Ctrl+S, Ctrl+X, Ctrl+D, ESC)
- Touch-friendly controls
- Dark/Light theme support

---

## 📋 Configuration Options

### POS Profile Settings
- Allow user to edit item discount
- Maximum item discount allowed
- Allow write-off change
- Allow credit sales
- Use customer credit
- Use cashback on returns

### Payment Settings
- Multiple payment modes configuration
- Default payment method
- Payment request integration
- Phone payment support

### Offer Settings
- Auto-apply offers
- Coupon-based offers
- Date-based validity
- Multi-level offer application
