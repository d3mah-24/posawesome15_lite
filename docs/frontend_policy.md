#### Frontend Policy

**Memory Management Rules:**

- ✅ Event listeners cleanup in `beforeDestroy`/`onBeforeUnmount`
- ✅ Timer and interval cleanup
- ✅ Event bus cleanup
- ✅ DOM references release

**UI/UX Rules:**

- Vue.js + HTML + CSS only (NO Vuetify)
- NO caching (only temp operations batches)
- NO animations or heavy CSS
- Virtual scrolling for lists > 50 items
- Simple component structure only

**Asset Management:**

- ✅ Local CDN only - no external requests
- ✅ Local fonts and Material Design Icons
- ✅ Minimize dependencies, named imports only

**API Call Rules (MANDATORY):**

- Use `api_mapper.js` for all API calls
- Maximum 2 API calls on page load
- Batch operations: CREATE → UPDATE → SUBMIT
- 1 second idle time, max 50 operations per batch
- Clear temp cache after successful API call
