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
- Simple structure only

**Asset Management:**

- ✅ Local CDN only - no external requests
- ✅ Local fonts and Material Design Icons
- ✅ Minimize dependencies, named imports only

**API Call Rules (MANDATORY):**

- Use `api_mapper.js` for all API calls
- 1 API calls to submit invoice
- Clear temp cache after successful API call
