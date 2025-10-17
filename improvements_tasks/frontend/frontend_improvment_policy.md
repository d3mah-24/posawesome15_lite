# Frontend Improvement Policy

## Code Structure Policy

### Component Organization Rules
- Each Vue component must be under 500 lines
- Separate business logic from UI logic
- Use composition API for complex state management
- Implement proper component lifecycle cleanup

### Queue System Policy (MANDATORY)

#### Operation Type Grouping:
```
├── item_operations      → Same DocType (Item)
├── payment_operations   → Same DocType (Payment)  
├── discount_operations  → Same DocType (Pricing Rule)
├── offers_operations    → Same DocType (Promotional Scheme)
└── customer_operations  → Same DocType (Customer)
```

#### Queue Implementation Requirements:
- Single queue per DocType operation group
- Collect operations in temp cache frontend
- Wait 1 second idle time
- Send ONE batch API call: `update_[doctype]`
- Proper timer cleanup in `beforeDestroy`

### Memory Management Policy

#### Mandatory Cleanup:
- Remove all event listeners in `beforeDestroy`
- Clear all timers and intervals
- Unsubscribe from event bus
- Release DOM references

#### Simple Policy Rules:
- **NO caching** (only temp operations batches allowed)
- **NO animations** or visual effects
- **NO heavy CSS** or complex styling
- **NO complex JavaScript logic**
- Keep components simple and lightweight

### Queue Management Policy

#### Batch Queue System (MANDATORY):
- **ONLY 3 API calls total for entire invoice process:**
  1. **1 API to CREATE invoice** (with first item)
  2. **1 API to UPDATE invoice** (if idle 1sec after operations)
  3. **1 API to SUBMIT & PRINT invoice** (when click print)
- **All other operations cached temporarily**

#### 3-API Invoice Process:
```
API 1: CREATE invoice (first item)
   ↓
API 2: UPDATE invoice (all changes batched)
   ├── Items changes
   ├── Payment changes  
   ├── Discount changes
   ├── Offers changes
   └── Customer changes
   ↓
API 3: SUBMIT & PRINT invoice (final step)
```

#### Batch Implementation Rules:
- **Collect operations during user activity**
- **Wait 1 second after last operation**
- **Send batch API call with all changes**
- **Clear temporary cache after successful API call**

#### Complete Invoice Flow (3 APIs Only):
```
Step 1: First Item Added → API 1: CREATE invoice
Step 2: All Operations   → Temp Cache → Idle 1s → API 2: UPDATE invoice
Step 3: Click Print      → API 3: SUBMIT & PRINT invoice

Example:
Add First Item     → API 1: create_invoice
Add Payment        → Temp Cache
Add Discount       → Temp Cache  
Modify Quantity    → Temp Cache
Wait 1 second      → API 2: update_invoice (ALL changes)
Click Print        → API 3: submit_and_print_invoice
```

#### Queue Timeout Rules:
- Maximum batch wait: 1 second
- Maximum batch size: 50 operations
- Force send if batch full
- Queue timeout: Maximum 5 seconds per API call

### Performance Requirements

#### Resource Optimization:
- Virtual scrolling for lists > 50 items
- Load all components immediately
- Simple component structure only

### API Call Policy

#### Request Optimization:
- Maximum 2 API calls on page load
- Batch multiple operations when possible
- Use specific field selection only
- Implement request deduplication


### Bundle Optimization Policy

#### Import Standards:
- Use named imports only
- Import specific Vuetify components
- No global library imports
- Minimize external dependencies

#### Code Standards:
- Use functional components where possible
- Remove unused code and dependencies
- Optimize images and assets

## Implementation Priority

### Phase 1: Critical Issues
1. Implement batch queue system (1s wait + batch API)
2. Fix memory leaks in queue system
3. Add component lifecycle cleanup
4. Optimize bundle size

### Phase 2: Performance & Validation
1. Optimize queue management
2. Add virtual scrolling
3. Optimize API calls
4. Add error boundaries
5. Final performance optimization
6. Testing and validation

## Compliance Requirements

### Code Review Checklist:
- [ ] Memory cleanup implemented
- [ ] Batch queue system implemented (1s wait)
- [ ] Error boundaries added
- [ ] Bundle size within limits
- [ ] Performance targets met
- [ ] No caching implemented (batch queue only)

### Testing Requirements:
- Memory usage testing
- Performance benchmarking
- Error scenario testing
- Bundle size validation
- Cross-browser compatibility

---

**Policy Enforcement**: Mandatory for all frontend code  
**Review Required**: Before merging any frontend changes  
**Performance Target**: 75% resource reduction  
**Compliance Level**: Critical