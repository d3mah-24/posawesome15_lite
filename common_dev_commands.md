# Common Development Commands

## 🔍 Debugging Best Practices

### Backend (Python)
Add at the end of each function to log results:
```python
frappe.log_error(
    title=f"filename.py (function_name)",
    message=f"Results: {results}"
)
```

### Frontend (JavaScript/Vue)
Add to show important context:
```javascript
console.log('filename.js (section):', { param1, param2 });
```

---

## 🔄 Apply Changes Commands

### Frontend Changes
```bash
cd ~/frappe-bench-15
bench clear-cache && 
bench clear-website-cache &&
bench build --app posawesome --force
```

### Backend Changes
```bash
find . -name "*.pyc" -print -delete
find . -type d -name "__pycache__" -print -exec rm -rf {} + &&
bench restart
```

---

## ⚠️ Important Notes

### JSON Files Warning
- Changes in JSON files are **risky**
- Will cause **schema conflicts**
- Only modify through **Custom Field** (safer approach)

---

## 📝 Quick Reference

| Change Type | Command |
|-------------|---------|
| Vue/JS files | `bench clear-cache && bench build --app posawesome --force` |
| Python files | `find . -name "*.pyc" -delete && bench restart` |
| Custom fields | Use Frappe UI (safer than JSON) |
