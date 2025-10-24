# POS Awesome Lite: AI Agent Guide
## Architecture Snapshot
- Frontend: Vue 3 SFCs (pure HTML/CSS, no Vuetify), mitt event bus, barcode handling via `public/js/onscan.js`.
- Backend: ERPNext v15/Frappe v15; every API lives in `posawesome/posawesome/api/*/*.py` with one whitelisted function per file.
- Data flow: UI builds invoice state, queues operations, then relies on ERPNext controllers for all calculations and persistence.
## Must-Know Files
- `posawesome/public/js/posapp/api_mapper.js` – single source for `frappe.call` methods (example: `API_MAP.SALES_INVOICE.CREATE`).
- `posawesome/public/js/posapp/components/` – core Vue screens (`pos/Invoice.vue`, `ItemsSelector.vue`, `Payments.vue`, `Navbar.vue`).
- `posawesome/public/js/posapp/bus.js` – mitt instance; clean listeners in `beforeUnmount()`.
- `posawesome/posawesome/api/` – CREATE/UPDATE/SUBMIT handlers plus shift/profile endpoints; always specify fields in ORM/SQL.
- `.vscode/` – enforced editor setup; run `.vscode/check-extensions.sh` if extensions drift.
## Critical Patterns
- Invoice lifecycle calls: `CREATE` on first item → debounced batch `UPDATE` (1s idle, max 50 ops) → `SUBMIT`; never add extra calls.
- Always call APIs through `API_MAP`; do not hardcode dotted method paths.
- Backend queries: no `SELECT *`; use field lists or parametrized SQL with `%s` and backticked table names.
- Event flow: emit via `evntBus.emit('add_item', item)`; unsubscribe timers and listeners in `beforeUnmount()`.
- Logging: frontend limited to `console.error` / `console.warn`; backend only uses `frappe.log_error` for real errors.
## Developer Workflows
- Rebuild frontend: `bench build --app posawesome`; add `bench clear-cache` first if assets stale.
- Apply backend code: `bench restart` after Python edits; remove caches with `find . -name "*.pyc" -delete` and friends.
- Schema checks: `bench mariadb` then `DESCRIBE tabDocType;` to confirm column names before querying.
- Validate extension policy: see `.vscode/README.md`; scripts prevent unwanted installs.
## Integration Touchpoints
- `hooks.py` wires `posawesome.bundle.js` and DocType-specific JS into ERPNext.
- Barcode lookups go through `API_MAP.ITEM.GET_BARCODE_ITEM`, which tests scale/private/regular codes server-side.
- Navbar cash/non-cash totals reuse the same logic as closing shifts; keep queries consistent with `pos_closing_shift` APIs.
## Common Pitfalls
- Hardcoded API routes, stray `console.log`, `SELECT *`, or forgetting `beforeUnmount()` cleanup will be flagged.
- Do not introduce caching beyond the temporary operation queue; clear it immediately after successful updates.
- New UI must stay under 500 lines per component and avoid external CDN assets.
## Quick References
- Policies: `docs/backend_policy.md`, `docs/frontend_policy.md`, `docs/dev_common_commands.md`.
- Key components/APIs: `Invoice.vue`, `Navbar.vue`, `posawesome/posawesome/api/sales_invoice/*`.
- Ask for clarification if a pattern is unclear; conventions here override generic best practices.
