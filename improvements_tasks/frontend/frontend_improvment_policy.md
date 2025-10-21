# Frontend Improvement Policy

## Memory Management Rules
- ✅ **Event listeners cleanup**: All Vue components properly remove event listeners in `beforeDestroy`/`onBeforeUnmount`
- ✅ **Timer cleanup**: All timers and intervals are properly cleared
- ✅ **Event bus cleanup**: All components properly unsubscribe from event bus
- ✅ **DOM references**: All DOM references are properly released


## UI/UX Rules
### **ONLY Vue.js + HTML + CSS**
- Use named imports only
- Minimize external dependencies
- Use Vue.js + HTML + CSS only
- NO caching (only temp operations batches allowed)
- NO animations
- NO heavy CSS
- NO Vuetify components
- NO complex JavaScript logic
- No global library imports
- Virtual scrolling for lists > 50 items
- Simple component structure only
- ERPNext-standard layouts only
- No custom animations or visual effects


## (MANDATORY) Sequence Operations are queued as batches
### API Call Rules
- Use `posawesome/public/js/posapp/api_mapper.js` for all API calls
- Maximum 2 API calls on page load
- Use **Composition API** for complex state management (Vue 3 style)
- Use `posawesome/public/js/posapp/api_mapper.js` for all API calls
- Batch multiple operations when possible
- Use specific field selection only
- Implement request deduplication
- Maximum 5 seconds per API call timeout
- Single queue per DocType operation group
- Collect operations in temp cache
- Wait 1 second idle time
- Send ONE batch API call: `update_[doctype]`
- Only 3 API calls per invoice: CREATE → UPDATE → SUBMIT
- Maximum batch wait: 1 second
- Maximum batch size: 50 operations
- Clear temporary cache after successful API call