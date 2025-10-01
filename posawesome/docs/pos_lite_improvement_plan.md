# POS Awesome Lite Improvement Plan

## Principles
- Use a simple, flat structure: one Vue file and one Python file for each complete component.
- Each Vue file calls specific functions (defs) in its matching Python file for all logic and data.
- Keep all code in the same places as now (no folder restructuring).
- Naming convention: `component.vue` calls `component.py` (e.g., `customer.vue` calls `customer.py`).

## Example Structure
- `customer.vue` <-> `customer.py`
- `itemselector.vue` <-> `itemselector.py`
- `invoice_itemcart.vue` <-> `invoice_itemcart.py`
- ...and so on for each main UI element.

## 1:1 Solution
- Every Vue file has a single, specific role and only calls its matching Python file.
- All calculations, business rules, and data processing are done in Python.
- Vue files only handle user input and display data returned from Python.

## Implementation Steps
1. For each complete UI element, create a single Vue file and a single Python file.
2. Remove calculations and logic from Vue files—move everything to Python.
3. Use `frappe.call` in Vue to interact with the backend Python file.
4. Keep the codebase minimal and easy to read.

## Example

**customer.vue**
```vue
<template>
  <div>
    <!-- Display customer info -->
    <button @click="createCustomer">Create</button>
  </div>
</template>
<script>
export default {
  methods: {
    async createCustomer() {
      await frappe.call({ method: 'posawesome.posawesome.api.customer.create_customer' });
    }
  }
}
</script>
```

**customer.py**
```python
import frappe
@frappe.whitelist()
def create_customer():
    # All logic and calculations here
    pass
```