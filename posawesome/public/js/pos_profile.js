frappe.ui.form.on('POS Profile', {
    setup: function (frm) {
        frm.set_query("posa_cash_mode_of_payment", function (doc) {
            return {
                filters: { 'type': 'Cash' }
            };
        });
    },

    // منطق التحكم - خيار واحد فقط
    posa_allow_user_to_edit_additional_discount: function(frm) {
        if (frm.doc.posa_allow_user_to_edit_additional_discount) {
            // إلغاء الخيارات الأخرى
            frm.set_value('posa_allow_user_to_edit_item_discount', 0);
            frm.set_value('posa_auto_fetch_offers', 0);
            frm.set_value('posa_fetch_coupon', 0);
            
            frappe.show_alert({
                message: 'تم تفعيل الخصم الإضافي - تم إلغاء الخيارات الأخرى',
                indicator: 'green'
            });
        }
    },

    posa_allow_user_to_edit_item_discount: function(frm) {
        if (frm.doc.posa_allow_user_to_edit_item_discount) {
            // إلغاء الخيارات الأخرى
            frm.set_value('posa_allow_user_to_edit_additional_discount', 0);
            frm.set_value('posa_auto_fetch_offers', 0);
            frm.set_value('posa_fetch_coupon', 0);
            
            frappe.show_alert({
                message: 'تم تفعيل خصم الأصناف - تم إلغاء الخيارات الأخرى',
                indicator: 'blue'
            });
        }
    },

    posa_auto_fetch_offers: function(frm) {
        if (frm.doc.posa_auto_fetch_offers) {
            // إلغاء الخيارات الأخرى
            frm.set_value('posa_allow_user_to_edit_additional_discount', 0);
            frm.set_value('posa_allow_user_to_edit_item_discount', 0);
            frm.set_value('posa_fetch_coupon', 0);
            
            frappe.show_alert({
                message: 'تم تفعيل العروض التلقائية - تم إلغاء الخيارات الأخرى',
                indicator: 'orange'
            });
        }
    },

    posa_fetch_coupon: function(frm) {
        if (frm.doc.posa_fetch_coupon) {
            // إلغاء الخيارات الأخرى
            frm.set_value('posa_allow_user_to_edit_additional_discount', 0);
            frm.set_value('posa_allow_user_to_edit_item_discount', 0);
            frm.set_value('posa_auto_fetch_offers', 0);
            
            frappe.show_alert({
                message: 'تم تفعيل الكوبونات - تم إلغاء الخيارات الأخرى',
                indicator: 'purple'
            });
        }
    }
});