frappe.ui.form.on('POS Profile', {
    setup: function (frm) {
        frm.set_query("posa_cash_mode_of_payment", function (doc) {
            return {
                filters: { 'type': 'Cash' }
            };
        });
    },

    // Control logic - only one option allowed
    posa_allow_user_to_edit_additional_discount: function(frm) {
        if (frm.doc.posa_allow_user_to_edit_additional_discount) {
            // Disable other options
            frm.set_value('posa_allow_user_to_edit_item_discount', 0);
            frm.set_value('posa_auto_fetch_offers', 0);

            frappe.show_alert({
                message: 'Additional discount enabled - other options disabled',
                indicator: 'green'
            });
        }
    },

    posa_allow_user_to_edit_item_discount: function(frm) {
        if (frm.doc.posa_allow_user_to_edit_item_discount) {
            // Disable other options
            frm.set_value('posa_allow_user_to_edit_additional_discount', 0);
            frm.set_value('posa_auto_fetch_offers', 0);

            frappe.show_alert({
                message: 'Item discount enabled - other options disabled',
                indicator: 'blue'
            });
        }
    },

    posa_auto_fetch_offers: function(frm) {
        if (frm.doc.posa_auto_fetch_offers) {
            // Disable other options
            frm.set_value('posa_allow_user_to_edit_additional_discount', 0);
            frm.set_value('posa_allow_user_to_edit_item_discount', 0);

            frappe.show_alert({
                message: 'Auto offers enabled - other options disabled',
                indicator: 'orange'
            });
        }
    },

    posa_apply_tax: function(frm) {
        if (!frm.doc.posa_apply_tax) {
            // Remove tax values when checkbox is unchecked
            frm.set_value('posa_tax_type', '');
            frm.set_value('posa_tax_percent', 0);

            frappe.show_alert({
                message: 'Tax values cleared',
                indicator: 'info'
            });
        }
    },

});
