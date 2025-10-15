# ⌨️ Keyboard Shortcuts - POS Awesome Lite

## Global Shortcuts

### Invoice Management
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl/Cmd + S` | Open Payment | Opens the payment dialog for current invoice |
| `Ctrl/Cmd + X` | Submit Payment | Submits the payment and finalizes the invoice |
| `Ctrl/Cmd + D` | Delete First Item | Removes the first item from the invoice |
| `Ctrl/Cmd + A` | Expand First Item | Expands the first item for editing |
| `Ctrl/Cmd + Z` | Focus Discount | Focuses on the discount input field |

### Item Search
| Shortcut | Action | Description |
|----------|--------|-------------|
| `ESC` | Clear Search | Clears the item search field and resets search |

### Form Input
| Shortcut | Action | Description |
|----------|--------|-------------|
| `Enter` | Confirm Input | Confirms changes in rate and discount percentage fields |
| `Enter` | Search Invoices | Triggers invoice search in returns dialog |
| `Enter` | Confirm Amount | Confirms cash denomination amounts in closing dialog |

---

## Shortcut Details

### Payment Shortcuts
- **Ctrl/Cmd + S**: Opens payment dialog when invoice has items
- **Ctrl/Cmd + X**: Submits payment and processes the invoice (only works in payment dialog)

### Item Management Shortcuts
- **Ctrl/Cmd + D**: Quickly removes the first item from the invoice list
- **Ctrl/Cmd + A**: Expands the first item for detailed editing
- **Ctrl/Cmd + Z**: Focuses the discount input field for quick discount entry

### Search Shortcuts
- **ESC**: Clears the item search field and resets the search state
- **Enter**: Confirms input in various form fields

---

## Barcode Scanner Integration

### Hardware Scanner Support
- **Automatic Detection**: Hardware barcode scanners are automatically detected
- **Real-time Processing**: Barcodes are processed immediately upon scanning
- **Multiple Formats**: Supports standard EAN/UPC, weight scale, and private barcodes

### Scanner Behavior
- **Direct Addition**: Scanned items are added directly to the invoice
- **No Confirmation**: Items are added immediately without user confirmation
- **Error Handling**: Shows error messages for invalid or not-found barcodes

---

## Usage Tips

### Efficient Workflow
1. **Quick Payment**: Use `Ctrl/Cmd + S` to quickly open payment dialog
2. **Fast Item Removal**: Use `Ctrl/Cmd + D` to remove first item without clicking
3. **Quick Discount**: Use `Ctrl/Cmd + Z` to focus discount field
4. **Clear Search**: Use `ESC` to quickly clear search and start over

### Form Navigation
- **Enter Key**: Use Enter to confirm changes in input fields
- **Tab Navigation**: Use Tab to move between form fields
- **Focus Management**: Shortcuts automatically focus relevant fields

---

## Technical Implementation

### Event Listeners
- Global keyboard event listeners are attached to the document
- Shortcuts work across all POS components
- Event listeners are properly cleaned up when components are destroyed

### Cross-Platform Support
- **Ctrl**: Works on Windows/Linux
- **Cmd**: Works on macOS
- **Meta Key**: Automatically detects the correct modifier key

### Performance
- Shortcuts use `preventDefault()` to avoid browser conflicts
- Event handling is optimized for fast response
- No performance impact on normal operations
