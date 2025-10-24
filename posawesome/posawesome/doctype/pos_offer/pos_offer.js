// Copyright (c) 2021, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Offer', {
	setup: function (frm) {
		set_filters(frm);
		controllers(frm);
	},
	refresh: function (frm) {
		controllers(frm);
	},
	onload: function (frm) {
		set_filters(frm);
		controllers(frm);
	},
	validate: function (frm) {
		try {
			// Basic validation for required fields
			if (!frm.doc.title) {
				frappe.throw("Title is required");
			}
			if (!frm.doc.company) {
				frappe.throw("Company is required");
			}
			if (!frm.doc.offer_type) {
				frappe.throw("Offer Type is required");
			}
			if (frm.doc.discount_type === "Discount Percentage" && !frm.doc.discount_percentage) {
				frappe.throw("Discount Percentage is required when Discount Type is 'Discount Percentage'");
			}
		} catch (e) {
			console.error('[ERROR] Exception in validate:', e);
			throw e;
		}
	},
	offer_type: function (frm) {
		controllers(frm);
	},
	discount_type: function (frm) {
		controllers(frm);
	},
});


const controllers = (frm) => {
	// Toggle display based on offer_type
	// Show item_code field when offer_type is 'item_code'
	frm.toggle_display('item_code', frm.doc.offer_type === 'item_code');
	frm.toggle_reqd('item_code', frm.doc.offer_type === 'item_code');

	// Show item_group field when offer_type is 'item_group'
	frm.toggle_display('item_group', frm.doc.offer_type === 'item_group');
	frm.toggle_reqd('item_group', frm.doc.offer_type === 'item_group');

	// Show brand field when offer_type is 'brand'
	frm.toggle_display('brand', frm.doc.offer_type === 'brand');
	frm.toggle_reqd('brand', frm.doc.offer_type === 'brand');

	// Show grand_total field when offer_type is 'grand_total'
	frm.toggle_display('grand_total', frm.doc.offer_type === 'grand_total');
	frm.toggle_reqd('grand_total', frm.doc.offer_type === 'grand_total');

	// Show customer field when offer_type is 'customer'
	frm.toggle_display('customer', frm.doc.offer_type === 'customer');
	frm.toggle_reqd('customer', frm.doc.offer_type === 'customer');

	// Show customer_group field when offer_type is 'customer_group'
	frm.toggle_display('customer_group', frm.doc.offer_type === 'customer_group');
	frm.toggle_reqd('customer_group', frm.doc.offer_type === 'customer_group');

	// Toggle discount fields
	frm.toggle_display('discount_percentage', frm.doc.discount_type === 'Discount Percentage');
	frm.toggle_reqd('discount_percentage', frm.doc.discount_type === 'Discount Percentage');
};

const set_filters = (frm) => {
	frm.set_query('pos_profile', function () {
		return {
			filters: {
				'company': frm.doc.company,
			}
		};
	});
	frm.set_query('warehouse', function () {
		return {
			filters: {
				'company': frm.doc.company,
				'is_group': 0,
			}
		};
	});
	frm.set_query('item_group', function () {
		return {
			filters: {
				'is_group': 0,
			}
		};
	});
};
