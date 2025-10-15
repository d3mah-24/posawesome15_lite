# Frontend Queue System Analysis - POS Awesome Invoice.vue

## Overview
Advanced queue system in frontend for managing item operations and auto-save in POS system.

---

## Main Queues

### 1. Item Operations Queue (`_itemOperationsQueue`)

#### Variables:
```javascript
_itemOperationsQueue: [],           // Pending operations list
_processingOperations: false,        // Processing state
_itemOperationTimer: null,          // Operations timer
```

#### Flow:
```
1. User performs operation (add/remove/modify item)
   ↓
2. Add operation to queue: _itemOperationsQueue.push(operation)
   ↓
3. Reset timer (200ms)
   ↓
4. On timer end: processItemOperations()
   ↓
5. Process offers: handelOffers()
   ↓
6. Combine operations: _itemOperationsQueue.join("-")
   ↓
7. Send to second queue: queue_auto_save()
   ↓
8. Clear queue: _itemOperationsQueue = []
```

---

### 2. Auto-Save Queue (`_pendingAutoSaveDoc`)

#### Variables:
```javascript
_autoSaveProcessing: false,         // Processing state
_pendingAutoSaveDoc: null,          // Pending document
_pendingAutoSaveReason: "auto",     // Save reason
_autoSaveWorkerTimer: null,         // Worker timer
```

#### Flow:
```
1. Receive save request from operations queue
   ↓
2. Create document: _pendingAutoSaveDoc = get_invoice_doc()
   ↓
3. Check processing state: if (!_autoSaveProcessing)
   ↓
4. Run worker: _run_auto_save_worker()
   ↓
5. Send to server: auto_update_invoice()
   ↓
6. Process result: .then() / .catch()
   ↓
7. Reset state: _autoSaveProcessing = false
   ↓
8. Check new requests: if (_pendingAutoSaveDoc)
   ↓
9. Process next request: setTimeout(_run_auto_save_worker, 0)
```

---

## Offers Queue (`_offersDebounceTimer`)

#### Variables:
```javascript
_offersDebounceTimer: null,         // Offers timer
_offersCache: null,                 // Cache memory
_offersProcessing: false,           // Processing state
```

#### Flow:
```
1. Operations processing complete
   ↓
2. Call: handelOffers()
   ↓
3. Reset timer (200ms)
   ↓
4. On timer end: _processOffers()
   ↓
5. Check cache (30 seconds)
   ↓
6. If not found: call server
   ↓
7. Save to cache
   ↓
8. Apply offers: updatePosOffers()
```

---

## Complete Operation Flow

### Scenario: Adding New Item
```
1. User adds item
   ↓
2. add_item() → Add to local list
   ↓
3. refreshTotals() → Update totals
   ↓
4. debouncedItemOperation("item-added") → Add to queue
   ↓
5. Wait 200ms
   ↓
6. processItemOperations() → Process queue
   ↓
7. handelOffers() → Process offers
   ↓
8. queue_auto_save() → Send to second queue
   ↓
9. _run_auto_save_worker() → Process save
   ↓
10. auto_update_invoice() → Send to server
    ↓
11. Update interface with result
```

### Scenario: Deleting Last Item
```
1. User deletes last item
   ↓
2. remove_item() → Remove from list
   ↓
3. Check: if (items.length === 0 && invoice_doc?.name)
   ↓
4. delete_draft_invoice() → Delete document
   ↓
5. Call server: delete_invoice()
   ↓
6. reset_invoice_session() → Reset session
```

---

## Key Features

### 1. **Debouncing (200ms)**
- Combine multiple operations
- Reduce server requests
- Fast user response

### 2. **Sequential Processing**
- Prevent operation conflicts
- Ensure operation order
- Separate error handling

### 3. **Cache Memory**
- Store offer results (30 seconds)
- Reduce server queries
- Improve performance

### 4. **Error Handling**
- Automatic retry
- Reload document on conflict
- Clear error messages

---

## Performance Statistics

- **Response Time**: 200ms for local operations
- **Save Time**: Immediate in background
- **Cache Memory**: 30 seconds for offers
- **Operation Limit**: Unlimited (with batching)