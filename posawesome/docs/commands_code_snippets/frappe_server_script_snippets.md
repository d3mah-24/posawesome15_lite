# Frappe Server-Side Script Snippets (Python)

**Based on:** Frappe v15.82.1 & ERPNext v15.79.1  
**Analyzed from:** Real production code in `/frappe/` and `/erpnext/`

---

## Table of Contents
1. [Document Operations](#document-operations)
2. [Database Queries](#database-queries)
3. [API Development](#api-development)
4. [Error Handling](#error-handling)
5. [Background Jobs](#background-jobs)
6. [Hooks and Events](#hooks-and-events)
7. [Utilities](#utilities)

---

## Document Operations

### Basic Document CRUD

```python
import frappe
from frappe import _

# Get a document
doc = frappe.get_doc("Sales Order", "SO-001")

# Create new document
new_doc = frappe.new_doc("Sales Order")
new_doc.customer = "CUST-001"
new_doc.transaction_date = frappe.utils.today()
new_doc.insert(ignore_permissions=True)

# Update document
doc.status = "Completed"
doc.save()

# Delete document
frappe.delete_doc("Sales Order", "SO-001")
```

### Document Controller Methods

```python
from frappe.model.document import Document

class SalesOrder(Document):
	def validate(self):
		"""Called before save - validate document"""
		if not self.customer:
			frappe.throw(_("Customer is required"))
		
		if self.grand_total <= 0:
			frappe.throw(_("Grand Total must be positive"))
	
	def before_save(self):
		"""Called before save - modify document"""
		self.status = "Draft"
	
	def after_insert(self):
		"""Called after document is inserted"""
		frappe.logger().info(f"Sales Order {self.name} created")
	
	def on_submit(self):
		"""Called when document is submitted"""
		self.update_stock_ledger()
	
	def on_cancel(self):
		"""Called when document is cancelled"""
		self.reverse_stock_ledger()
	
	def on_trash(self):
		"""Called before document is deleted"""
		self.check_linked_documents()
	
	@frappe.whitelist()
	def custom_method(self):
		"""Custom whitelisted method callable from client"""
		return {"success": True}
```

### Document Hooks

```python
# In hooks.py
doc_events = {
	"Sales Order": {
		"validate": "myapp.custom.validate_sales_order",
		"on_submit": "myapp.custom.on_sales_order_submit",
		"on_cancel": "myapp.custom.on_sales_order_cancel",
	},
	"*": {
		"before_save": "myapp.custom.before_save_all_docs",
	}
}

# In myapp/custom.py
def validate_sales_order(doc, method=None):
	"""Hook function for Sales Order validation"""
	if doc.delivery_date < doc.transaction_date:
		frappe.throw(_("Delivery date cannot be before transaction date"))
```

---

## Database Queries

### frappe.db Methods

```python
import frappe

# Get single value
customer_name = frappe.db.get_value("Customer", "CUST-001", "customer_name")

# Get multiple fields
customer = frappe.db.get_value(
	"Customer", 
	"CUST-001", 
	["customer_name", "territory", "customer_group"],
	as_dict=True
)

# Check if exists
exists = frappe.db.exists("Customer", "CUST-001")
# or with filters
exists = frappe.db.exists("Customer", {"customer_name": "John Doe"})

# Get list of documents
customers = frappe.db.get_list(
	"Customer",
	filters={"customer_group": "Retail"},
	fields=["name", "customer_name", "territory"],
	order_by="customer_name asc",
	limit=20
)

# Get all records
all_customers = frappe.db.get_all(
	"Customer",
	filters={"disabled": 0},
	fields=["name", "customer_name"]
)

# Count records
count = frappe.db.count("Customer", {"customer_group": "Retail"})

# Set value (updates database directly)
frappe.db.set_value("Customer", "CUST-001", "credit_limit", 50000)

# Set multiple values
frappe.db.set_value("Customer", "CUST-001", {
	"credit_limit": 50000,
	"payment_terms": "Net 30"
})
```

### SQL Queries

```python
# Simple SQL query
results = frappe.db.sql("""
	SELECT name, customer_name, territory
	FROM `tabCustomer`
	WHERE customer_group = %s
	ORDER BY customer_name
""", ("Retail",))

# SQL with dict results
customers = frappe.db.sql("""
	SELECT name, customer_name, territory
	FROM `tabCustomer`
	WHERE customer_group = %(group)s
	AND territory = %(territory)s
""", {"group": "Retail", "territory": "India"}, as_dict=True)

# SQL with single column result
names = frappe.db.sql_list("""
	SELECT name FROM `tabCustomer`
	WHERE customer_group = %s
""", ("Retail",))

# SQL UPDATE/DELETE
frappe.db.sql("""
	UPDATE `tabCustomer`
	SET credit_limit = %s
	WHERE customer_group = %s
""", (50000, "Retail"))

# Always commit after direct SQL modifications
frappe.db.commit()
```

### Query Builder (New in v14+)

```python
from frappe.query_builder import DocType

# Using Query Builder
Customer = DocType("Customer")
customers = (
	frappe.qb.from_(Customer)
	.select(Customer.name, Customer.customer_name, Customer.territory)
	.where(Customer.customer_group == "Retail")
	.where(Customer.disabled == 0)
	.orderby(Customer.customer_name)
	.limit(10)
).run(as_dict=True)

# Complex query with joins
SalesOrder = DocType("Sales Order")
SalesOrderItem = DocType("Sales Order Item")

orders = (
	frappe.qb.from_(SalesOrder)
	.join(SalesOrderItem)
	.on(SalesOrder.name == SalesOrderItem.parent)
	.select(
		SalesOrder.name,
		SalesOrder.customer,
		SalesOrderItem.item_code,
		SalesOrderItem.qty
	)
	.where(SalesOrder.docstatus == 1)
	.where(SalesOrderItem.qty > 0)
).run(as_dict=True)
```

---

## API Development

### REST API Endpoints

```python
import frappe
from frappe import _

@frappe.whitelist()
def get_customer_details(customer_id):
	"""
	Whitelist decorator makes function accessible via HTTP
	URL: /api/method/myapp.api.get_customer_details
	"""
	if not customer_id:
		frappe.throw(_("Customer ID is required"))
	
	customer = frappe.get_doc("Customer", customer_id)
	
	return {
		"customer_name": customer.customer_name,
		"territory": customer.territory,
		"credit_limit": customer.credit_limit
	}

@frappe.whitelist(allow_guest=True)
def public_api():
	"""Allow non-logged-in users to access this API"""
	return {"message": "This is public"}

@frappe.whitelist(methods=['POST'])
def create_customer(customer_name, territory):
	"""Only allow POST method"""
	doc = frappe.new_doc("Customer")
	doc.customer_name = customer_name
	doc.territory = territory
	doc.insert()
	
	return doc.as_dict()
```

### Document Methods (Called from client)

```python
class SalesOrder(Document):
	@frappe.whitelist()
	def calculate_total(self):
		"""Can be called via frm.call('calculate_total')"""
		total = sum(item.amount for item in self.items)
		self.total = total
		self.save()
		return total
	
	@frappe.whitelist()
	def send_email(self, recipient):
		"""Custom method with parameters"""
		frappe.sendmail(
			recipients=[recipient],
			subject=f"Sales Order {self.name}",
			message=f"Your order {self.name} has been confirmed"
		)
		return {"sent": True}
```

### API Response Patterns

```python
@frappe.whitelist()
def process_order(order_id):
	try:
		# Validate
		if not frappe.db.exists("Sales Order", order_id):
			return {
				"success": False,
				"message": _("Order not found")
			}
		
		# Process
		order = frappe.get_doc("Sales Order", order_id)
		order.submit()
		
		# Return success
		return {
			"success": True,
			"message": _("Order processed successfully"),
			"order": order.as_dict()
		}
		
	except Exception as e:
		frappe.log_error(f"Error processing order: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}
```

---

## Error Handling

### Exception Types

```python
import frappe
from frappe import _

def process_document(name):
	try:
		doc = frappe.get_doc("Sales Order", name)
		doc.submit()
		
	except frappe.DoesNotExistError:
		# Document doesn't exist
		frappe.msgprint(_("Document not found"))
		
	except frappe.PermissionError:
		# User doesn't have permission
		frappe.msgprint(_("You don't have permission"))
		
	except frappe.ValidationError:
		# Validation failed
		frappe.msgprint(_("Validation failed"))
		
	except Exception as e:
		# Catch all other errors
		frappe.log_error(f"Error: {str(e)}")
		frappe.throw(_("An error occurred"))
```

### Error Logging

```python
import frappe

# Log error with title
try:
	risky_operation()
except Exception as e:
	frappe.log_error(
		message=frappe.get_traceback(),
		title="Risky Operation Failed"
	)

# Log error with custom message
frappe.log_error(
	message=f"Failed to process order {order_id}",
	title="Order Processing Error"
)

# Throw error to user
frappe.throw(_("Customer is required"))

# Throw with specific exception type
frappe.throw(
	_("Insufficient stock for item {0}").format(item_code),
	exc=frappe.ValidationError
)

# Message print (info message)
frappe.msgprint(_("Document saved successfully"))

# Message print with indicator
frappe.msgprint(
	msg=_("Document saved"),
	title=_("Success"),
	indicator="green"
)
```

---

## Background Jobs

### Enqueue Tasks

```python
import frappe

# Enqueue a function to run in background
@frappe.whitelist()
def process_large_data():
	"""API that queues background job"""
	frappe.enqueue(
		"myapp.tasks.process_data",
		queue="long",
		timeout=3600,
		is_async=True,
		job_name="Process Large Data"
	)
	return {"message": "Processing started in background"}

# The actual background function
def process_data():
	"""Function that runs in background"""
	# Long running operation
	for i in range(1000):
		# Process item
		frappe.db.commit()
		
	# Send notification when done
	frappe.publish_realtime(
		event="processing_complete",
		message={"status": "completed"},
		user=frappe.session.user
	)
```

### Scheduled Tasks (Cron Jobs)

```python
# In hooks.py
scheduler_events = {
	"daily": [
		"myapp.tasks.daily_cleanup"
	],
	"hourly": [
		"myapp.tasks.send_reminders"
	],
	"cron": {
		"0 */6 * * *": [
			"myapp.tasks.sync_data"  # Every 6 hours
		]
	}
}

# In myapp/tasks.py
def daily_cleanup():
	"""Runs every day"""
	frappe.db.sql("""
		DELETE FROM `tabError Log`
		WHERE creation < DATE_SUB(NOW(), INTERVAL 30 DAY)
	""")
	frappe.db.commit()

def send_reminders():
	"""Runs every hour"""
	overdue_invoices = frappe.get_all(
		"Sales Invoice",
		filters={"status": "Overdue"},
		fields=["name", "customer", "customer_email"]
	)
	
	for invoice in overdue_invoices:
		send_reminder_email(invoice)
```

---

## Hooks and Events

### Document Events (hooks.py)

```python
# hooks.py
doc_events = {
	"Sales Order": {
		"validate": "myapp.custom.validate_sales_order",
		"before_insert": "myapp.custom.before_insert_sales_order",
		"after_insert": "myapp.custom.after_insert_sales_order",
		"before_save": "myapp.custom.before_save_sales_order",
		"before_submit": "myapp.custom.before_submit_sales_order",
		"on_submit": "myapp.custom.on_submit_sales_order",
		"before_cancel": "myapp.custom.before_cancel_sales_order",
		"on_cancel": "myapp.custom.on_cancel_sales_order",
		"on_trash": "myapp.custom.on_trash_sales_order",
		"on_update_after_submit": "myapp.custom.on_update_sales_order",
	},
	"*": {
		"before_save": "myapp.custom.before_save_all",
		"on_submit": "myapp.custom.on_submit_all",
	}
}
```

### Override Whitelisted Methods

```python
# hooks.py
override_whitelisted_methods = {
	"frappe.desk.form.save.savedocs": "myapp.custom.custom_save"
}

# In myapp/custom.py
@frappe.whitelist()
def custom_save():
	"""Override default save functionality"""
	# Custom save logic
	pass
```

---

## Utilities

### Date and Time

```python
from frappe.utils import (
	today, now, nowdate, nowtime, now_datetime,
	add_days, add_months, add_years,
	date_diff, get_first_day, get_last_day,
	getdate, get_datetime
)

# Get current date/time
current_date = today()  # or nowdate()
current_time = nowtime()
current_datetime = now_datetime()

# Add to dates
future_date = add_days(today(), 7)
next_month = add_months(today(), 1)

# Date difference
days = date_diff(end_date, start_date)

# Parse dates
date_obj = getdate("2025-01-01")
datetime_obj = get_datetime("2025-01-01 10:30:00")

# Format for display
from frappe.utils import formatdate
display_date = formatdate(today())  # Uses user's format
```

### Number Formatting

```python
from frappe.utils import flt, cint, fmt_money

# Float conversion (safe)
qty = flt(value)  # Returns 0 if None/invalid
qty = flt(value, 2)  # With precision

# Integer conversion
count = cint(value)

# Currency formatting
amount_str = fmt_money(1000.50, currency="USD")
```

### Email

```python
import frappe

# Send email
frappe.sendmail(
	recipients=["user@example.com"],
	subject="Test Email",
	message="This is a test email",
	attachments=[{
		"fname": "document.pdf",
		"fcontent": pdf_content
	}],
	now=False  # Queue for sending
)

# Send email with template
frappe.sendmail(
	recipients=["user@example.com"],
	template="sales_order_confirmation",
	args={
		"order_name": "SO-001",
		"customer": "John Doe"
	},
	reference_doctype="Sales Order",
	reference_name="SO-001"
)
```

### Permissions

```python
import frappe

# Check permission
if frappe.has_permission("Sales Order", "write", doc=doc):
	# User can write
	pass

# Check if user has role
if "Sales Manager" in frappe.get_roles():
	# User is Sales Manager
	pass

# Get current user
user = frappe.session.user
user_email = frappe.session.user
full_name = frappe.utils.get_fullname()

# Set user (for background jobs)
frappe.set_user("Administrator")
```

### Cache

```python
import frappe

# Simple cache
@frappe.cache()
def get_item_price(item_code):
	"""Cached for default TTL"""
	return frappe.db.get_value("Item Price", {"item_code": item_code}, "price_list_rate")

# Cache with TTL
@frappe.cache(ttl=300)  # 5 minutes
def get_exchange_rate(from_currency, to_currency):
	"""Cached for 5 minutes"""
	return fetch_exchange_rate(from_currency, to_currency)

# Manual cache operations
frappe.cache().set_value("key", "value")
value = frappe.cache().get_value("key")
frappe.cache().delete_value("key")
```

### Realtime Updates (SocketIO)

```python
import frappe

# Publish to specific user
frappe.publish_realtime(
	event="order_updated",
	message={"order_id": "SO-001", "status": "Completed"},
	user=user_email
)

# Publish to all users
frappe.publish_realtime(
	event="system_notification",
	message={"text": "System maintenance in 10 minutes"}
)

# Publish after commit
frappe.publish_realtime(
	event="order_created",
	message={"order_id": doc.name},
	after_commit=True
)
```

### File Operations

```python
import frappe

# Save file
file_doc = frappe.get_doc({
	"doctype": "File",
	"file_name": "document.pdf",
	"content": pdf_content,
	"is_private": 1,
	"folder": "Home"
})
file_doc.insert()

# Get file
file_doc = frappe.get_doc("File", file_url)
content = file_doc.get_content()

# Attach file to document
frappe.get_doc({
	"doctype": "File",
	"file_url": file_url,
	"attached_to_doctype": "Sales Order",
	"attached_to_name": "SO-001"
}).insert()
```

---

## Best Practices

1. **Always use `frappe.whitelist()`** for API endpoints
2. **Use `frappe.throw()` for user-facing errors**
3. **Use `frappe.log_error()` for debugging**
4. **Always use `_()`** for translatable strings
5. **Use `flt()` and `cint()`** for safe number conversions
6. **Commit database changes** explicitly when needed
7. **Use `frappe.enqueue()`** for long-running tasks
8. **Validate permissions** before operations
9. **Use hooks** instead of modifying core files
10. **Cache expensive operations** appropriately

---

**Documentation generated from:** Frappe v15.82.1 | ERPNext v15.79.1  
**Last updated:** October 2025

