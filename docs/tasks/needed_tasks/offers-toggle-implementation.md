# 🎁 Task: Offers Toggle Implementation

**💰 Budget**: TBD

**👨‍💻 Developer**: TBD

**💳 Payment**: TBD

**🎯 Priority**: 🔥 High

**📊 Status**: ⏳ Pending

**🔧 Feature**: POS Profile Offers Toggle

**📖 Description**:

- Implement POS Profile checkbox to enable/disable offers functionality
- When disabled (posa_auto_fetch_offers=0), no offers are fetched, applied, or displayed
- When enabled (posa_auto_fetch_offers=1), offers work normally

**🛠️ Technical Requirements**:

- **📊 Analysis and Discussion Required** (Before any implementation)
- **📋 Respect Existing Code Policy** (Must follow current code policies)
- **🏗️ Respect Existing File Structure** (Both frontend and backend files)
- **🚫 No Project Policy Violations** (Must comply with all project policies)
- Follow ERPNext original patterns
- Use existing ERPNext methods
- Maintain system compatibility
- Ensure performance optimization

**🎯 Implementation Details**:

**✅ Custom Field** (Already exists):
- Field: `posa_auto_fetch_offers` in POS Profile
- Type: Check (checkbox)
- Default: 1 (enabled)
- Location: After offer-related fields

**✅ Frontend Logic** (Implemented):
- **Pos.vue**: Added check in `get_offers()` method
- **Invoice.vue**: Added check in `_processOffers()` method
- **PosOffers.vue**: Added conditional rendering with `offersEnabled` computed property

**🎯 Behavior**:

**When posa_auto_fetch_offers = 1 (Enabled)**:
- Offers fetch normally from API
- Offer cards display in frontend
- Offers can be applied to invoices
- All offer functionality works as expected

**When posa_auto_fetch_offers = 0 (Disabled)**:
- No offers API calls made
- No offer cards displayed
- No offers applied to invoices
- Existing applied offers are cleared
- Shows "Offers Disabled" message

**📋 Deliverables**:

- **📊 Analysis and Presentation** (Required before implementation)
- Custom field in POS Profile (already exists)
- Frontend conditional logic (implemented)
- Disabled state UI (implemented)
- Testing documentation

**🎯 Success Criteria**:

- ✅ POS Profile checkbox controls offers functionality
- ✅ When disabled, no offers are fetched or displayed
- ✅ When enabled, offers work normally
- ✅ Clean UI for disabled state
- ✅ No performance impact
- ✅ Code follows project policies
- ✅ Proper error handling

**🧪 Testing Requirements**:

1. **Test with posa_auto_fetch_offers = 1 (enabled)**:
   - Offers should fetch normally
   - Offers cards should display
   - Offers should apply to invoices

2. **Test with posa_auto_fetch_offers = 0 (disabled)**:
   - No offers API calls
   - No offers cards displayed
   - No offers applied to invoices
   - Existing applied offers removed
   - Shows disabled message

3. **Test profile switching**:
   - Switch between profiles with different settings
   - Ensure offers enable/disable correctly

**📁 Files Modified**:

1. ✅ `posawesome/fixtures/custom_field.json` - Custom field (already exists)
2. ✅ `posawesome/public/js/posapp/components/pos/Pos.vue` - Added enable/disable logic
3. ✅ `posawesome/public/js/posapp/components/pos/Invoice.vue` - Added check in _processOffers
4. ✅ `posawesome/public/js/posapp/components/pos/PosOffers.vue` - Added conditional rendering
5. ✅ `docs/tasks/needed_tasks/offers-toggle-implementation.md` - Task documentation

**📝 Notes**:

- Implementation is complete and ready for testing
- All code follows existing patterns and policies
- No breaking changes to existing functionality
- Clean separation between enabled/disabled states
