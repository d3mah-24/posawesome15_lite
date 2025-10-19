// composables/useInvoice.js
// ═══════════════════════════════════════════════════════════════
// Core Invoice Logic - Simplified (replaces 2000+ lines)
// ═══════════════════════════════════════════════════════════════

import { ref, computed, watch } from 'vue';
import { evntBus } from '@/bus';

export function useInvoice() {
    // ═══════════════════════════════════════════
    // STATE (Reactive)
    // ═══════════════════════════════════════════
    
    const items = ref([]);
    const invoice_doc = ref(null);
    const customer = ref('');
    const pos_profile = ref(null);
    const pos_opening_shift = ref(null);
    const additional_discount_percentage = ref(0);
    
    // ═══════════════════════════════════════════
    // COMPUTED PROPERTIES
    // ═══════════════════════════════════════════
    
    const invoiceSummary = computed(() => {
        const doc = invoice_doc.value || {};
        const itemsList = items.value || [];
        
        return {
            // From backend (calculated)
            net_total: doc.net_total || 0,
            grand_total: doc.grand_total || 0,
            tax_amount: doc.total_taxes_and_charges || 0,
            discount_amount: doc.discount_amount || 0,
            
            // Local calculations
            total_qty: itemsList.reduce((s, i) => s + (i.qty || 0), 0),
            total_before_discount: itemsList.reduce((s, i) => 
                s + ((i.qty || 0) * (i.price_list_rate || 0)), 0
            ),
        };
    });
    
    const canPay = computed(() => {
        return items.value.length > 0 
            && customer.value 
            && !invoice_doc.value?.is_return;
    });
    
    const canPrint = computed(() => {
        return canPay.value && invoice_doc.value?.payments?.some(p => p.amount > 0);
    });
    
    const readonly = computed(() => {
        return invoice_doc.value?.is_return || false;
    });
    
    // ═══════════════════════════════════════════
    // ITEM OPERATIONS (Simplified)
    // ═══════════════════════════════════════════
    
    const generateRowId = () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    };
    
    const addItem = async (item) => {
        if (!item?.item_code) return;
        
        // Check if exists
        const existing = items.value.find(
            i => i.item_code === item.item_code && i.uom === item.uom
        );
        
        if (existing) {
            existing.qty = (existing.qty || 0) + (item.qty || 1);
        } else {
            // Add new item - PRESERVE price_list_rate!
            const newItem = {
                ...item,
                posa_row_id: generateRowId(),
                qty: item.qty || 1,
                price_list_rate: item.price_list_rate || item.rate || 0,
                base_rate: item.base_rate || item.price_list_rate || item.rate || 0,
                rate: item.rate || item.price_list_rate || 0,
                discount_percentage: item.discount_percentage || 0,
            };
            
            items.value.push(newItem);
        }
        
        // Sync with backend
        await syncInvoice();
    };
    
    const removeItem = async (item) => {
        const index = items.value.findIndex(i => i.posa_row_id === item.posa_row_id);
        if (index >= 0) {
            items.value.splice(index, 1);
            
            if (items.value.length === 0) {
                await deleteInvoice();
            } else {
                await syncInvoice();
            }
        }
    };
    
    const updateItemQty = (item, delta = 0, source = 'input') => {
        const oldQty = item.qty || 0;
        const newQty = source === 'input'
            ? Number(item.qty) || 0
            : Math.max(0, oldQty + delta);
        
        item.qty = newQty;
        
        if (newQty === 0) {
            removeItem(item);
        }
    };
    
    const updateItemPricing = (item, field, value) => {
        const basePrice = item.price_list_rate || item.base_rate || 0;
        
        if (field === 'rate') {
            item.rate = parseFloat(value) || 0;
            // Auto-calculate discount
            if (basePrice > 0 && item.rate < basePrice) {
                item.discount_percentage = ((basePrice - item.rate) / basePrice) * 100;
            } else {
                item.discount_percentage = 0;
            }
        } else if (field === 'discount_percentage') {
            const maxDiscount = getMaxDiscount(item);
            item.discount_percentage = Math.min(parseFloat(value) || 0, maxDiscount);
            // Auto-calculate rate
            if (basePrice > 0) {
                item.rate = basePrice * (1 - item.discount_percentage / 100);
            }
        }
        
        // Sync will be triggered by debounce in component
    };
    
    const getMaxDiscount = (item) => {
        return item.max_discount 
            || pos_profile.value?.posa_item_max_discount_allowed 
            || 100;
    };
    
    // ═══════════════════════════════════════════
    // INVOICE OPERATIONS (Backend-First)
    // ═══════════════════════════════════════════
    
    const syncInvoice = async () => {
        if (items.value.length === 0) return;
        if (invoice_doc.value?.submitted_for_payment) return;
        
        try {
            const result = await callAPI('posawesome.api.sales_invoice.sync', {
                invoice_name: invoice_doc.value?.name,
                customer: customer.value,
                items: items.value.map(item => ({
                    item_code: item.item_code,
                    qty: item.qty,
                    rate: item.rate,
                    uom: item.uom,
                    discount_percentage: item.discount_percentage,
                })),
                discount_percentage: additional_discount_percentage.value,
            });
            
            if (result) {
                updateFromBackend(result);
            }
        } catch (error) {
            console.error('Sync failed:', error);
            showMessage('Failed to sync invoice', 'error');
        }
    };
    
    const updateFromBackend = (result) => {
        // Update invoice doc
        invoice_doc.value = result;
        
        // Update ONLY calculated fields in items
        if (result.items && Array.isArray(result.items)) {
            items.value.forEach(localItem => {
                const apiItem = result.items.find(
                    a => a.item_code === localItem.item_code && a.uom === localItem.uom
                );
                
                if (apiItem) {
                    // Update calculated fields only
                    localItem.amount = apiItem.amount;
                    localItem.net_amount = apiItem.net_amount;
                    localItem.discount_amount = apiItem.discount_amount;
                    
                    // DO NOT update: price_list_rate, rate, qty (user inputs)
                    // PRESERVE local state!
                }
            });
        }
    };
    
    const deleteInvoice = async () => {
        if (invoice_doc.value?.name) {
            await callAPI('posawesome.api.sales_invoice.delete', {
                invoice_name: invoice_doc.value.name,
            });
        }
        resetInvoice();
    };
    
    const resetInvoice = () => {
        items.value = [];
        invoice_doc.value = null;
        customer.value = pos_profile.value?.customer || '';
        additional_discount_percentage.value = 0;
    };
    
    // ═══════════════════════════════════════════
    // PAYMENT OPERATIONS
    // ═══════════════════════════════════════════
    
    const showPayment = async () => {
        if (!canPay.value) {
            showMessage('Cannot proceed to payment', 'error');
            return;
        }
        
        try {
            // Final sync before payment
            await syncInvoice();
            
            // Emit to payment component
            evntBus.emit('send_invoice_doc_payment', invoice_doc.value);
            evntBus.emit('show_payment', 'true');
        } catch (error) {
            showMessage('Error preparing payment', 'error');
        }
    };
    
    const printInvoice = async () => {
        if (!canPrint.value) {
            showMessage('Cannot print invoice', 'error');
            return;
        }
        
        try {
            const result = await callAPI('posawesome.api.sales_invoice.submit', {
                invoice_name: invoice_doc.value.name,
            });
            
            if (result) {
                // Open print window
                const url = `/printview?doctype=Sales%20Invoice&name=${result.name}`;
                const printWindow = window.open(url, 'Print');
                printWindow.addEventListener('load', () => {
                    printWindow.print();
                });
                
                // Reset after print
                resetInvoice();
            }
        } catch (error) {
            showMessage('Error printing invoice', 'error');
        }
    };
    
    // ═══════════════════════════════════════════
    // HELPERS
    // ═══════════════════════════════════════════
    
    const callAPI = (method, args) => {
        return new Promise((resolve, reject) => {
            frappe.call({
                method,
                args,
                callback: (r) => resolve(r.message),
                error: (err) => reject(err),
            });
        });
    };
    
    const showMessage = (text, color = 'info') => {
        evntBus.emit('show_mesage', { text, color });
    };
    
    // ═══════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════
    
    const initialize = (profileData) => {
        pos_profile.value = profileData.pos_profile;
        pos_opening_shift.value = profileData.pos_opening_shift;
        customer.value = profileData.pos_profile?.customer || '';
    };
    
    // ═══════════════════════════════════════════
    // RETURN PUBLIC API
    // ═══════════════════════════════════════════
    
    return {
        // State
        items,
        invoice_doc,
        customer,
        pos_profile,
        pos_opening_shift,
        additional_discount_percentage,
        
        // Computed
        invoiceSummary,
        canPay,
        canPrint,
        readonly,
        
        // Actions
        addItem,
        removeItem,
        updateItemQty,
        updateItemPricing,
        syncInvoice,
        deleteInvoice,
        resetInvoice,
        showPayment,
        printInvoice,
        initialize,
    };
}
