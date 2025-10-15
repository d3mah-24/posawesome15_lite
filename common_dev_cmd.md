# Common Development Commands

## 🔍 Debug Policy

### Backend (Python) Debug Policy

- **Summary**: Use `frappe.log_error()` at the end of each function to summarize results.
- **Details**: Include the filename, function name, and results in the log.

### Backend Apply Changes

```bash
find . -name "*.pyc" -print -delete
find . -type d -name "__pycache__" -print -exec rm -rf {} + &&
bench restart
```

---

### Frontend Debug Policy

- **Summary**: Use `console.log` to debug.
- **Details**: Include the filename, section, and important parameters only.

---

## 🔄 Apply Changes Commands

### Frontend Apply Changes

```bash
cd ~/frappe-bench-15
bench clear-cache && \
bench clear-website-cache && \
bench build --app posawesome --force
```

