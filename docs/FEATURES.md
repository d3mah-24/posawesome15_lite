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

## 💸 Easy Item Discount Control

- Control show/hide discount price and discount percentage columns in POS interface
- Insert discounted price (limited to allowed max percentage)
- Insert discount percentage (limited to allowed max percentage)  
- Sales invoice shows total items discount amount (simplified for invoice print format)

---

## 💰 Easy Invoice Discount Control

- Control show/hide Invoice discount percentage
- Insert discount percentage (limited to allowed max percentage)
- Sales invoice shows total Invoice discount amount & Percentage (simplified for invoice print format)

---

## 🎯 Offers & Coupons

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

## 📱 Barcode Scanner Compatibility

- **Auto-Focus Free Scanning:** Scan barcodes anywhere in POS interface without focusing search field
- **Instant Item Addition:** Scanned items automatically added to invoice cart
- **Multiple Barcode Support:** EAN-13, Code 128, UPC-A, and custom barcodes
- **Hardware Scanner Compatible:** Works with USB and Bluetooth barcode scanners
- **Speed Optimized:** Handles 30+ scans per second for high-volume operations
- **Error Handling:** Clear feedback for invalid or unrecognized barcodes
- **OnScan.js Integration:** Advanced barcode detection with configurable timing
- **No Manual Input Required:** Seamless scanning workflow without keyboard interaction

---

## 🎨 User Interface

- **Frontend:** Vue 3.4.21 + Vuetify 3.6.9
- Responsive and modern design
- Split view (items selector + invoice)
- Compact table layouts
- Real-time calculations
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
