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

	// Load Material Design Icons CSS only for POS app
	$("head").append("<link rel='stylesheet' href='/assets/posawesome/css/materialdesignicons.css' class='posapp-mdi-css'>");

	// Fix shortcut.js offsetWidth error by hiding layout-main-section
	$("head").append("<style>.layout-main-section { display: none !important; }</style>");

	// Listen for POS Profile load to apply translations based on posa_language
	window.addEventListener('posProfileLoaded', function(e) {
		const posProfile = e.detail.pos_profile;
		if (posProfile && posProfile.posa_language) {
			applyTranslationsFromPosProfile(posProfile.posa_language);
		}
	});
};

// Function to apply translations based on POS Profile language
function applyTranslationsFromPosProfile(language) {
	if (!language || language === 'en') return;

	// Import translations from posapp.js
	if (typeof window.TRANSLATIONS === 'undefined') {
		console.error('TRANSLATIONS not loaded yet');
		return;
	}

	const translations = window.TRANSLATIONS[language];
	if (translations) {
		window.__messages = window.__messages || {};
		$.extend(window.__messages, translations);
	}
}

frappe.pages['posapp'].on_page_leave = function() {
	// Remove Material Design Icons CSS when leaving POS app
	$("head").find("link.posapp-mdi-css").remove();
};
