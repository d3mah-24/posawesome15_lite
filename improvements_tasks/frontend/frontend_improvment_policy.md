# Frontend Improvement Policy

## 1. Memory Management Rules
**Purpose**: Prevent memory leaks and ensure proper cleanup

1.1. ✅ **Event listeners cleanup**: Remove listeners in `beforeDestroy`/`onBeforeUnmount`
1.2. ✅ **Timer cleanup**: Clear all timers and intervals
1.3. ✅ **Event bus cleanup**: Unsubscribe from event bus
1.4. ✅ **DOM references**: Release all DOM references

## 2. UI/UX Rules
**Purpose**: Maintain simple, consistent interface

### 2.1 Core Framework
2.1.1. Use Vue.js + HTML + CSS only
2.1.2. NO caching (only temp operations batches allowed)
2.1.3. NO animations
2.1.4. NO heavy CSS
2.1.5. NO Vuetify components
2.1.6. NO complex JavaScript logic

### 2.2 Component Structure
2.2.1. Virtual scrolling for lists > 50 items
2.2.2. Simple component structure only
2.2.3. ERPNext-standard layouts only
2.2.4. No custom animations or visual effects

## 3. Asset Management Rules
**Purpose**: Ensure local-only dependencies and fast loading

3.1. ✅ **Local CDN Only**: Download all external CDN dependencies locally
3.2. ✅ **Local Fonts Only**: Serve fonts from local assets only
3.3. ✅ **Material Design Icons**: Use local implementation from `node_modules/@mdi/font/`
3.4. ✅ **Font Files**: Copy all font files to `posawesome/public/css/`
3.5. ✅ **CSS Paths**: Update CSS font paths to local files only
3.6. ✅ **No External Requests**: Zero external CDN requests for fonts/icons
3.7. ✅ **Minimize Dependencies**: Use named imports only
3.8. ✅ **No Global Imports**: No global library imports allowed

## 4. API Call Rules (MANDATORY)
**Purpose**: Optimize API performance with batched operations

### 4.1 API Configuration
4.1.1. Use `posawesome/public/js/posapp/api_mapper.js` for all API calls
4.1.2. Maximum 2 API calls on page load
4.1.3. Use **Composition API** for complex state management (Vue 3 style)
4.1.4. Maximum 5 seconds per API call timeout

### 4.2 Batching Rules
4.2.1. Batch multiple operations when possible
4.2.2. Use specific field selection only
4.2.3. Implement request deduplication
4.2.4. Single queue per DocType operation group
4.2.5. Collect operations in temp cache
4.2.6. Wait 1 second idle time
4.2.7. Send ONE batch API call: `update_[doctype]`

### 4.3 Invoice Operations
4.3.1. Only 3 API calls per invoice: CREATE → UPDATE → SUBMIT
4.3.2. Maximum batch wait: 1 second
4.3.3. Maximum batch size: 50 operations
4.3.4. Clear temporary cache after successful API call