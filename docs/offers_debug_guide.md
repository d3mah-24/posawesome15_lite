# 🔍 Offers & Coupons Debug Guide

## Overview
This document explains how to use the debug logging added to track why offers are not being applied in POS Awesome Lite.

## Debug Logging Added

### 🔧 Backend Debug Logging (frappe.log_error)

All backend debug logs are written with `frappe.log_error()` and can be viewed in:
- **ERPNext UI**: Go to **Error Log** doctype
- **Search/Filter**: Use "Offers Debug" in the error title field

#### 1. **get_offers.py** - Offer Retrieval
```python
Location: posawesome/posawesome/api/pos_offer/get_offers.py
```

**Debug Points**:
- `[DEBUG] get_offers called with profile: {profile}` - Function entry
- `[DEBUG] POS Profile details - Company: {company}, Warehouse: {warehouse}, Date: {date}` - Profile info
- `[DEBUG] Query returned {count} offers. Offer names: {names}` - Database query results
- `[ERROR] get_offers exception: {error}` - Error handling

**What to Check**:
- Is the POS Profile correct?
- Are there any offers in the database for this company/warehouse?
- Are date ranges valid?

#### 2. **get_applicable_offers.py** - Offer Application Check
```python
Location: posawesome/posawesome/api/pos_offer/get_applicable_offers.py
```

**Debug Points**:
- `[DEBUG] get_applicable_offers called with invoice: {invoice_name}` - Function entry
- `[DEBUG] No POS Profile found for invoice: {invoice_name}` - Missing profile
- `[DEBUG] POS Profile: {profile}, Customer: {customer}, Grand Total: {total}, Items count: {count}` - Invoice data
- `[DEBUG] Total offers from get_offers: {count}` - All available offers
- `[DEBUG] Offer '{name}' applicable: {True/False} | Type: {type} | Apply On: {apply_on}` - Each offer check
- `[DEBUG] Total applicable offers: {count}` - Final result
- `[ERROR] get_applicable_offers exception: {error}` - Error handling

**What to Check**:
- Are offers being retrieved from `get_offers()`?
- Why is each offer being accepted or rejected?
- How many offers passed all checks?

#### 3. **offer_utils.py** - Detailed Validation Logic
```python
Location: posawesome/posawesome/api/pos_offer/offer_utils.py
Function: is_offer_applicable()
```

**Debug Points**:
- `[DEBUG] Offer '{name}' rejected: Company mismatch` - Wrong company
- `[DEBUG] Offer '{name}' rejected: Not yet valid / Expired` - Date issues
- `[DEBUG] Offer '{name}' rejected: Min/Max amount not met` - Amount conditions
- `[DEBUG] Offer '{name}' rejected: Min/Max qty not met` - Quantity conditions
- `[DEBUG] Offer '{name}' checking Item Code: {item} in invoice items: {items}` - Item code check
- `[DEBUG] Offer '{name}' ACCEPTED: Item Code matched` - Success
- `[DEBUG] Offer '{name}' rejected: Item Code not found in invoice` - Failed item check
- Similar logs for Item Group and Brand checks
- `[DEBUG] Offer '{name}' ACCEPTED: Transaction-level offer` - Transaction offers
- `[DEBUG] Offer '{name}' ACCEPTED: Default acceptance` - No specific conditions

**What to Check**:
- Which validation rule is rejecting the offer?
- Are item codes/groups/brands matching correctly?
- Are min/max amounts and quantities configured correctly?

### 💻 Frontend Debug Logging (console.log)

All frontend debug logs appear in **Browser Console** (F12 → Console tab).

#### 1. **Invoice.vue** - Offer Fetching
```javascript
Location: posawesome/public/js/posapp/components/pos/Invoice.vue
Method: get_applicable_pos_offers()
```

**Debug Points**:
- `[DEBUG] get_applicable_pos_offers - Already processing, skipping` - Duplicate call prevention
- `[DEBUG] get_applicable_pos_offers - Starting API call for invoice: {name}` - API call start
- `[DEBUG] get_applicable_pos_offers - API response: {data}` - Raw response
- `[DEBUG] get_applicable_pos_offers - Offers count: {count}` - How many offers returned
- `[DEBUG] get_applicable_pos_offers - Calling updatePosOffers with: {offers}` - Passing to update
- `[ERROR] get_applicable_pos_offers - API error: {error}` - API failure

**What to Check**:
- Is the API being called?
- Are offers being returned from backend?
- Is `updatePosOffers()` being called?

#### 2. **Invoice.vue** - Offer Updates
```javascript
Method: updatePosOffers(), updateInvoiceOffers()
```

**Debug Points**:
- `[DEBUG] updatePosOffers called in Invoice.vue with: {offers}` - Event emission
- `[DEBUG] updateInvoiceOffers called with: {offers}` - Invoice offer update
- `[DEBUG] posa_offers updated to: {offers}` - Local state update

**What to Check**:
- Are offers being passed to the event bus?
- Is the local invoice state being updated?

#### 3. **PosOffers.vue** - Offer Display & Selection
```javascript
Location: posawesome/public/js/posapp/components/pos/PosOffers.vue
```

**Debug Points**:
- `[DEBUG] SET_OFFERS event received: {data}` - Initial offer loading
- `[DEBUG] pos_offers set to: {offers}` - Offers with applied status
- `[DEBUG] updatePosOffers called with: {appliedOffers}` - External update
- `[DEBUG] Current pos_offers before update: {offers}` - State before
- `[DEBUG] Offer '{name}' status changed: {old} -> {new}` - Status changes
- `[DEBUG] pos_offers after update: {offers}` - State after
- `[DEBUG] handleManualOfferChange - Current offers: {offers}` - Manual toggle
- `[DEBUG] Applied Grand Total Offers count: {count}` - Grand total offers
- `[DEBUG] Multiple Grand Total offers detected` - Conflict resolution
- `[DEBUG] Single Grand Total offer applied: {name}` - Active offer
- `[DEBUG] Disabling other Grand Total offer: {name}` - Disabling others
- `[DEBUG] No Grand Total offers applied` - None active
- `[ERROR] handleManualOfferChange exception: {error}` - Error handling

**What to Check**:
- Are offers being received in PosOffers component?
- Are offer statuses (applied/not applied) correct?
- Are Grand Total offer conflicts being resolved?

#### 4. **PosCoupons.vue** - Coupon Management
```javascript
Location: posawesome/public/js/posapp/components/pos/PosCoupons.vue
```

**Debug Points**:
- `[DEBUG] add_coupon called with: {code}` - Coupon entry
- `[DEBUG] Current customer: {customer}, pos_profile: {profile}` - Context
- `[WARN] add_coupon - Missing customer or coupon code` - Validation failure
- `[WARN] add_coupon - Coupon already used: {code}` - Duplicate coupon
- `[DEBUG] add_coupon - Calling API to validate coupon` - API call
- `[DEBUG] add_coupon - API response: {response}` - Server response
- `[WARN] add_coupon - Coupon validation failed: {msg}` - Invalid coupon
- `[DEBUG] add_coupon - Coupon validated successfully: {coupon}` - Valid coupon
- `[DEBUG] add_coupon - Updated posa_coupons: {coupons}` - State update
- `[ERROR] add_coupon - API call failed: {error}` - API error
- `[DEBUG] updatePosCoupons called with offers: {offers}` - Offer sync
- `[DEBUG] Current posa_coupons before update: {coupons}` - State before
- `[DEBUG] Coupon '{code}' status changed: {old} -> {new}` - Status change
- `[DEBUG] posa_coupons after update: {coupons}` - State after

**What to Check**:
- Are coupons being validated correctly?
- Are coupon-based offers being linked?
- Is coupon status syncing with offers?

## How to Debug Offer Issues

### Step 1: Check Backend Logs (Error Log)

1. Go to **ERPNext** → **Error Log**
2. Filter by: `error LIKE '%Offers Debug%'`
3. Sort by: `Creation` (newest first)
4. Look for the debug flow:
   ```
   Offers Debug - Get Offers Start
   Offers Debug - Profile Details
   Offers Debug - Query Results
   Offers Debug - Start
   Offers Debug - Invoice Data
   Offers Debug - All Offers Count
   Offers Debug - Offer Check (for each offer)
   Offers Debug - [Various validation checks]
   Offers Debug - Applicable Count
   ```

**Common Issues**:
- **No offers found**: Check if offers exist in database with correct company/warehouse/dates
- **All offers rejected**: Check validation logs to see which rules are failing
- **Offers not applicable**: Check Item Code/Group/Brand matching, amounts, quantities

### Step 2: Check Frontend Logs (Browser Console)

1. Open **Browser Console** (F12 → Console)
2. Filter by: `[DEBUG]`
3. Look for the debug flow:
   ```
   [DEBUG] get_applicable_pos_offers - Starting API call
   [DEBUG] get_applicable_pos_offers - API response
   [DEBUG] get_applicable_pos_offers - Offers count
   [DEBUG] updatePosOffers called
   [DEBUG] SET_OFFERS event received
   [DEBUG] pos_offers set to
   ```

**Common Issues**:
- **API not called**: Check if invoice is created and has items
- **API returns empty**: Check backend logs
- **Offers received but not displayed**: Check PosOffers component logs
- **Offers displayed but not applying**: Check handleManualOfferChange logs

### Step 3: Cross-Reference Backend + Frontend

**Scenario**: Offer appears in POS but doesn't apply

1. **Backend Check**:
   - Look for `[DEBUG] Offer '{name}' applicable: True` in backend logs
   - Confirm offer was marked as applicable

2. **Frontend Check**:
   - Look for `[DEBUG] get_applicable_pos_offers - Offers count: X` (X > 0)
   - Check if `[DEBUG] SET_OFFERS event received` shows your offer
   - Check if `offer_applied: true` for auto-apply offers

3. **Manual Toggle Check**:
   - Look for `[DEBUG] handleManualOfferChange` logs when toggling
   - Check for Grand Total conflicts

## Common Debugging Scenarios

### Scenario 1: No Offers Showing Up

**Backend**:
```
[DEBUG] get_offers called with profile: XYZ
[DEBUG] Query returned 0 offers
```
**Solution**: No offers configured for this POS Profile/Company/Warehouse

**Backend**:
```
[DEBUG] Total offers from get_offers: 5
[DEBUG] Offer 'ABC' applicable: False | Type: Item Code
[DEBUG] Total applicable offers: 0
```
**Solution**: All offers failed validation - check offer_utils logs for reasons

**Frontend**:
```
[DEBUG] get_applicable_pos_offers - API response: []
[DEBUG] get_applicable_pos_offers - Offers count: 0
```
**Solution**: Backend returned no offers - check backend logs

### Scenario 2: Offers Show But Don't Apply

**Frontend**:
```
[DEBUG] SET_OFFERS event received: [{name: 'ABC', offer_applied: false}]
```
**Solution**: `auto` field not set on offer - offers need manual toggle OR auto=1

**Frontend**:
```
[DEBUG] Applied Grand Total Offers count: 2
[DEBUG] Multiple Grand Total offers detected, applying best one
```
**Solution**: Multiple Grand Total offers - system selects best discount

**Frontend**:
```
[DEBUG] Offer 'ABC' status changed: true -> false
[DEBUG] Disabling other Grand Total offer: ABC
```
**Solution**: Another Grand Total offer was selected (higher discount)

### Scenario 3: Coupon Not Working

**Frontend**:
```
[WARN] add_coupon - Coupon validation failed: Coupon expired
```
**Solution**: Coupon validity dates are wrong

**Frontend**:
```
[DEBUG] add_coupon - Coupon validated successfully
[DEBUG] Coupon 'XYZ' status changed: 0 -> 1
```
**Solution**: Coupon works but linked offer might not be applicable - check offer logs

## How to Remove Debug Logs (After Debugging)

Once debugging is complete, you can remove logs:

### Backend (Optional - keep for production monitoring)
```bash
# Comment out frappe.log_error() calls in:
# - posawesome/api/pos_offer/get_offers.py
# - posawesome/api/pos_offer/get_applicable_offers.py
# - posawesome/api/pos_offer/offer_utils.py
```

### Frontend (Remove for production)
```bash
# Remove console.log() calls in:
# - public/js/posapp/components/pos/Invoice.vue
# - public/js/posapp/components/pos/PosOffers.vue
# - public/js/posapp/components/pos/PosCoupons.vue
```

Then rebuild:
```bash
cd ~/frappe-bench-15
bench build --app posawesome
bench restart
```

## Summary

**Backend Logs** (Error Log in ERPNext):
- Offer retrieval from database
- Offer validation rules (company, dates, amounts, quantities)
- Item/Group/Brand matching
- Final applicable offers count

**Frontend Logs** (Browser Console):
- API call initiation and response
- Offer display and status updates
- Manual toggle handling
- Grand Total conflict resolution
- Coupon validation and application

**Debug Flow**:
1. Backend: `get_offers()` → retrieve all offers for POS Profile
2. Backend: `get_applicable_offers()` → filter offers for this invoice
3. Backend: `is_offer_applicable()` → validate each offer's rules
4. Frontend: `get_applicable_pos_offers()` → API call to backend
5. Frontend: `updatePosOffers()` → emit event to PosOffers component
6. Frontend: `SET_OFFERS` event → display offers with correct status
7. Frontend: `handleManualOfferChange()` → handle user toggles

**Key Insight**: The debug logs now show the complete journey of an offer from database query → validation → frontend display → user interaction!
