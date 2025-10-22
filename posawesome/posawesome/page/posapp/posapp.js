// @ts-nocheck
{% include "posawesome/posawesome/page/posapp/onscan.js" %}
frappe.pages['posapp'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Andalus Group',
		single_column: true
	});

	this.page.$PosApp = new frappe.PosApp.posapp(this.page);

	$('div.navbar-fixed-top').find('.container').css('padding', '0');

	$("head").append("<link rel='stylesheet' href='/assets/posawesome/css/materialdesignicons.css'>");
	
	// Fix shortcut.js offsetWidth error by hiding layout-main-section
	$("head").append("<style>.layout-main-section { display: none !important; }</style>");
};
