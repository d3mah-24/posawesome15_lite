# Frontend Improvement Policy

## Code Structure Policy

### Component Organization Rules
- Each Vue component must be under 500 lines
- Separate business logic from UI logic
- Use composition API for complex state management
- Implement proper component lifecycle cleanup

### Queue System Policy (MANDATORY)

#### Operation Type Grouping:
# Frontend Improvement Policy

## Component Organization Rules
- Each Vue component must be under 500 lines
- Separate business logic from UI logic
- Use composition API for complex state management
- Implement proper component lifecycle cleanup

## Memory Management Rules
- Remove all event listeners in `beforeDestroy`
- Clear all timers and intervals
- Unsubscribe from event bus
- Release DOM references
- NO caching (only temp operations batches allowed)
- NO animations
- NO heavy CSS
- NO Vuetify components
- NO complex JavaScript logic

## Batch Queue System Rules (MANDATORY)
- Single queue per DocType operation group
- Collect operations in temp cache
- Wait 1 second idle time
- Send ONE batch API call: `update_[doctype]`
- Only 3 API calls per invoice: CREATE → UPDATE → SUBMIT
- Maximum batch wait: 1 second
- Maximum batch size: 50 operations
- Clear temporary cache after successful API call

## API Call Rules
- Maximum 2 API calls on page load
- Batch multiple operations when possible
- Use specific field selection only
- Implement request deduplication
- Maximum 5 seconds per API call timeout

## Import Rules
- Use named imports only
- No global library imports
- Minimize external dependencies
- Use Vue.js + HTML + CSS only

## UI/UX Rules
- Virtual scrolling for lists > 50 items
- Simple component structure only
- ERPNext-standard layouts only
- No custom animations or visual effects

## Code Review Checklist
- [ ] Memory cleanup implemented
- [ ] Batch queue system implemented (1s wait)
- [ ] Components under 500 lines
- [ ] No Vuetify, no heavy CSS, no animations
- [ ] Only Vue.js + HTML + CSS
- [ ] Performance targets met
- [ ] No caching (batch queue only)