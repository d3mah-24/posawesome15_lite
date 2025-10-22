// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Closing Shift', {
	onload: function (frm) {
		frm.set_query("pos_profile", function (doc) {
			return {
				filters: { 'user': doc.user }
			};
		});

		frm.set_query("user", function (doc) {
			return {
				query: "posawesome.posawesome.api.pos_closing_shift.get_cashiers.get_cashiers",
				filters: { 'parent': doc.pos_profile }
			};
		});

		frm.set_query("pos_opening_shift", function (doc) {
			return { filters: { 'status': 'Open', 'docstatus': 1 } };
		});

		if (frm.doc.docstatus === 0) frm.set_value("period_end_date", frappe.datetime.now_datetime());
		if (frm.doc.docstatus === 1) set_html_data(frm);
		
		// Enhance form appearance
		enhance_form_styling(frm);
	},

	refresh: function(frm) {
		// Add custom buttons with better styling
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('View Detailed Report'), function() {
				show_detailed_modal(frm);
			}, __('Reports')).addClass('btn-primary');
			
			frm.add_custom_button(__('Export Summary'), function() {
				export_summary(frm);
			}, __('Reports')).addClass('btn-info');
		}
		
		// Update form colors based on status
		update_form_indicators(frm);
	},

	pos_opening_shift (frm) {
		if (frm.doc.pos_opening_shift && frm.doc.user) {
			// Show progress indicator
			show_loading_indicator(frm, __("Loading shift data..."));
			
			reset_values(frm);
			frappe.run_serially([
				() => frm.trigger("set_opening_amounts"),
				() => frm.trigger("get_pos_invoices"),
				() => frm.trigger("get_pos_payments")
			]).finally(() => {
				hide_loading_indicator(frm);
			});
		}
	},

	set_opening_amounts (frm) {
		frappe.db.get_doc("POS Opening Shift", frm.doc.pos_opening_shift)
			.then(({ balance_details }) => {
				balance_details.forEach(detail => {
					frm.add_child("payment_reconciliation", {
						mode_of_payment: detail.mode_of_payment,
						opening_amount: detail.amount || 0,
						expected_amount: detail.amount || 0
					});
				});
			})
			.catch(e => {
				console.error('[ERROR] Exception in set_opening_amounts:', e);
			});
	},

	get_pos_invoices (frm) {
		frappe.call({
			method: 'posawesome.posawesome.api.pos_closing_shift.get_pos_invoices.get_pos_invoices',
			args: {
				pos_opening_shift: frm.doc.pos_opening_shift,
			},
			callback: (r) => {
				let pos_docs = r.message;
				set_form_data(pos_docs, frm);
				refresh_fields(frm);
				set_html_data(frm);
			},
			error: function(err) {
				console.error('[ERROR] Exception in get_pos_invoices:', err);
			}
		});
	},

	get_pos_payments (frm) {
		frappe.call({
			method: 'posawesome.posawesome.api.pos_closing_shift.get_payments_entries.get_payments_entries',
			args: {
				pos_opening_shift: frm.doc.pos_opening_shift,
			},
			callback: (r) => {
				let pos_payments = r.message;
				set_form_payments_data(pos_payments, frm);
				refresh_fields(frm);
				set_html_data(frm);
			},
			error: function(err) {
				console.error('[ERROR] Exception in get_pos_payments:', err);
			}
		});
	}
});

frappe.ui.form.on('POS Closing Shift Detail', {
	closing_amount: (frm, cdt, cdn) => {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "difference", flt(row.expected_amount - row.closing_amount));
	}
});

function set_form_data (data, frm) {
	try {
		data.forEach(d => {
			add_to_pos_transaction(d, frm);
			frm.doc.grand_total += flt(d.grand_total);
			frm.doc.net_total += flt(d.net_total);
			frm.doc.total_quantity += flt(d.total_qty);
			add_to_payments(d, frm);
			add_to_taxes(d, frm);
		});
	} catch (e) {
		console.error('[ERROR] Exception in set_form_data:', e);
	}
}

function set_form_payments_data (data, frm) {
	try {
		data.forEach(d => {
			add_to_pos_payments(d, frm);
			add_pos_payment_to_payments(d, frm);
		});
	} catch (e) {
		console.error('[ERROR] Exception in set_form_payments_data:', e);
	}
}

function add_to_pos_transaction (d, frm) {
	frm.add_child("pos_transactions", {
		sales_invoice: d.name,
		posting_date: d.posting_date,
		grand_total: d.grand_total,
		customer: d.customer
	});
}

function add_to_pos_payments (d, frm) {
	frm.add_child("pos_payments", {
		payment_entry: d.name,
		posting_date: d.posting_date,
		paid_amount: d.paid_amount,
		customer: d.party,
		mode_of_payment: d.mode_of_payment
	});
}

function add_to_payments (d, frm) {
	try {
		d.payments.forEach(p => {
			const payment = frm.doc.payment_reconciliation.find(pay => pay.mode_of_payment === p.mode_of_payment);
			if (payment) {
				let amount = p.amount;
				let cash_mode_of_payment = get_value("POS Profile", frm.doc.pos_profile, 'posa_cash_mode_of_payment');
				if (!cash_mode_of_payment) {
					cash_mode_of_payment = 'Cash';
				}
				if (payment.mode_of_payment == cash_mode_of_payment) {
					amount = p.amount - d.change_amount;
				}
				payment.expected_amount += flt(amount);
			} else {
				frm.add_child("payment_reconciliation", {
					mode_of_payment: p.mode_of_payment,
					opening_amount: 0,
					expected_amount: p.amount || 0
				});
			}
		});
	} catch (e) {
		console.error('[ERROR] Exception in add_to_payments:', e);
	}
}

function add_pos_payment_to_payments (p, frm) {
	try {
		const payment = frm.doc.payment_reconciliation.find(pay => pay.mode_of_payment === p.mode_of_payment);
		if (payment) {
			let amount = p.paid_amount;
			payment.expected_amount += flt(amount);
		} else {
			frm.add_child("payment_reconciliation", {
				mode_of_payment: p.mode_of_payment,
				opening_amount: 0,
				expected_amount: p.amount || 0
			});
		}
	} catch (e) {
		console.error('[ERROR] Exception in add_pos_payment_to_payments:', e);
	}
};


function add_to_taxes (d, frm) {
	try {
		d.taxes.forEach(t => {
			const tax = frm.doc.taxes.find(tx => tx.account_head === t.account_head && tx.rate === t.rate);
			if (tax) {
				tax.amount += flt(t.tax_amount);
			} else {
				frm.add_child("taxes", {
					account_head: t.account_head,
					rate: t.rate,
					amount: t.tax_amount
				});
			}
		});
	} catch (e) {
		console.error('[ERROR] Exception in add_to_taxes:', e);
	}
}

function reset_values (frm) {
	frm.set_value("pos_transactions", []);
	frm.set_value("payment_reconciliation", []);
	frm.set_value("pos_payments", []);
	frm.set_value("taxes", []);
	frm.set_value("grand_total", 0);
	frm.set_value("net_total", 0);
	frm.set_value("total_quantity", 0);
}

function refresh_fields (frm) {
	frm.refresh_field("pos_transactions");
	frm.refresh_field("payment_reconciliation");
	frm.refresh_field("pos_payments");
	frm.refresh_field("taxes");
	frm.refresh_field("grand_total");
	frm.refresh_field("net_total");
	frm.refresh_field("total_quantity");
}

function set_html_data (frm) {
	// Add loading indicator
	const wrapper = frm.get_field("payment_reconciliation_details").$wrapper;
	wrapper.html(`
		<div style="text-align: center; padding: 40px; color: #6c757d;">
			<div class="spinner-border" role="status" style="width: 3rem; height: 3rem;">
				<span class="sr-only">Loading...</span>
			</div>
			<div style="margin-top: 15px; font-size: 0.9rem;">
				${__("Generating closing shift report...")}
			</div>
		</div>
	`);
	
	frappe.call({
		method: "get_payment_reconciliation_details",
		doc: frm.doc,
		callback: (r) => {
			if (r.message) {
				wrapper.html(r.message);
				// Add smooth fade-in animation
				wrapper.find('.pos-closing-shift-details').hide().fadeIn(800);
				
				// Add print functionality
				add_print_button(wrapper, frm);
			} else {
				wrapper.html(`
					<div style="text-align: center; padding: 40px; color: #dc3545;">
						<i class="fa fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 15px;"></i>
						<div style="font-size: 1.1rem; margin-bottom: 10px;">
							${__("Failed to generate report")}
						</div>
						<div style="font-size: 0.9rem; color: #6c757d;">
							${__("Please try refreshing the form or contact your administrator")}
						</div>
					</div>
				`);
			}
		},
		error: function(err) {
			console.error('[ERROR] Exception in set_html_data:', err);
			wrapper.html(`
				<div style="text-align: center; padding: 40px; color: #dc3545;">
					<i class="fa fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 15px;"></i>
					<div style="font-size: 1.1rem; margin-bottom: 10px;">
						${__("Error loading closing shift details")}
					</div>
					<div style="font-size: 0.9rem; color: #6c757d;">
						${err.message || __("An unexpected error occurred")}
					</div>
					<button class="btn btn-sm btn-primary" onclick="cur_frm.trigger('refresh')" style="margin-top: 15px;">
						<i class="fa fa-refresh"></i> ${__("Retry")}
					</button>
				</div>
			`);
		}
	});
}

function add_print_button(wrapper, frm) {
	// Add print button to the report
	const print_btn = $(`
		<div style="text-align: center; margin: 20px 0; padding: 20px;">
			<button class="btn btn-primary btn-print-closing-shift" style="margin-right: 10px;">
				<i class="fa fa-print"></i> ${__("Print Report")}
			</button>
			<button class="btn btn-secondary btn-export-pdf">
				<i class="fa fa-file-pdf-o"></i> ${__("Export as PDF")}
			</button>
		</div>
	`);
	
	wrapper.find('.summary-container').append(print_btn);
	
	// Print functionality
	wrapper.find('.btn-print-closing-shift').on('click', function() {
		const print_content = wrapper.find('.pos-closing-shift-details').clone();
		const print_window = window.open('', '_blank');
		print_window.document.write(`
			<!DOCTYPE html>
			<html>
			<head>
				<title>POS Closing Shift Report - ${frm.doc.name}</title>
				<style>
					body { margin: 0; padding: 0; }
					@media print {
						.btn-print-closing-shift, .btn-export-pdf { display: none !important; }
						.summary-card:hover { transform: none !important; box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important; }
						.pos-closing-shift-details { background: white !important; }
					}
				</style>
			</head>
			<body>
				${print_content.html()}
			</body>
			</html>
		`);
		print_window.document.close();
		setTimeout(() => {
			print_window.print();
		}, 500);
	});
	
	// PDF export functionality (placeholder)
	wrapper.find('.btn-export-pdf').on('click', function() {
		frappe.msgprint({
			title: __("Export Feature"),
			message: __("PDF export functionality can be implemented using a PDF library like jsPDF or by creating a server-side PDF generation endpoint."),
			indicator: 'blue'
		});
	});
}

const get_value = (doctype, name, field) => {
	let value;
	frappe.call({
		method: 'frappe.client.get_value',
		args: {
			'doctype': doctype,
			'filters': { 'name': name },
			'fieldname': field
		},
		async: false,
		callback: function (r) {
			if (!r.exc) {
				value = r.message[field];
			}
		},
		error: function(err) {
			console.error('[ERROR] Exception in get_value:', err);
		}
	});
	return value;
};

// Enhanced UI Functions
function enhance_form_styling(frm) {
	// Add custom CSS directly to the page
	const style = `
		<style id="pos-closing-custom-styles">
		/* POS Closing Shift Enhanced Styling */
		
		/* Form Container Improvements */
		.frappe-control[data-doctype="POS Closing Shift"] .form-layout {
			background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
			min-height: 100vh;
			padding: 20px;
		}

		/* Section Headers */
		.frappe-control[data-doctype="POS Closing Shift"] .form-layout .section-head {
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
			color: white !important;
			border-radius: 12px 12px 0 0 !important;
			padding: 15px 25px !important;
			font-weight: 600 !important;
			text-transform: uppercase;
			letter-spacing: 1px;
			border: none !important;
			box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
		}

		/* Form Sections */
		.frappe-control[data-doctype="POS Closing Shift"] .form-layout .form-section {
			background: white;
			border: none !important;
			border-radius: 12px !important;
			margin-bottom: 25px !important;
			box-shadow: 0 8px 30px rgba(0,0,0,0.1) !important;
			overflow: hidden;
			transition: transform 0.3s ease, box-shadow 0.3s ease;
		}

		.frappe-control[data-doctype="POS Closing Shift"] .form-layout .form-section:hover {
			transform: translateY(-2px);
			box-shadow: 0 12px 40px rgba(0,0,0,0.15) !important;
		}

		/* Currency Fields Enhancement */
		.frappe-control[data-doctype="POS Closing Shift"] .frappe-control[data-fieldtype="Currency"] .control-input {
			background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%) !important;
			border: 2px solid #28a745 !important;
			border-radius: 8px !important;
			font-weight: 700 !important;
			color: #155724 !important;
			font-size: 1.1rem !important;
			padding: 12px 16px !important;
		}

		.frappe-control[data-doctype="POS Closing Shift"] .frappe-control[data-fieldtype="Currency"] .control-input:focus {
			border-color: #20c997 !important;
			box-shadow: 0 0 0 0.25rem rgba(40, 167, 69, 0.25) !important;
			transform: scale(1.02);
		}

		/* Table Enhancements */
		.frappe-control[data-doctype="POS Closing Shift"] .grid-wrapper .grid-row {
			border-radius: 8px !important;
			margin-bottom: 10px !important;
			transition: all 0.3s ease !important;
			border: 1px solid #e9ecef !important;
		}

		.frappe-control[data-doctype="POS Closing Shift"] .grid-wrapper .grid-row:hover {
			background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%) !important;
			transform: translateX(8px) !important;
			box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
		}

		.frappe-control[data-doctype="POS Closing Shift"] .grid-wrapper .grid-row .grid-row-index {
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
			color: white !important;
			border-radius: 50% !important;
			width: 28px !important;
			height: 28px !important;
			display: flex !important;
			align-items: center !important;
			justify-content: center !important;
			font-weight: 600 !important;
		}

		/* Button Improvements */
		.frappe-control[data-doctype="POS Closing Shift"] .btn-primary {
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
			border: none !important;
			border-radius: 25px !important;
			padding: 10px 25px !important;
			font-weight: 600 !important;
			text-transform: uppercase;
			letter-spacing: 0.5px;
			box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
			transition: all 0.3s ease !important;
		}

		.frappe-control[data-doctype="POS Closing Shift"] .btn-primary:hover {
			transform: translateY(-2px) !important;
			box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
		}

		/* Field Labels */
		.frappe-control[data-doctype="POS Closing Shift"] .control-label {
			font-weight: 600 !important;
			color: #495057 !important;
			margin-bottom: 8px !important;
			font-size: 0.95rem !important;
			text-transform: uppercase;
			letter-spacing: 0.5px;
		}

		/* Input Fields */
		.frappe-control[data-doctype="POS Closing Shift"] .form-control {
			border-radius: 8px !important;
			border: 2px solid #e9ecef !important;
			padding: 12px 16px !important;
			transition: all 0.3s ease !important;
		}

		.frappe-control[data-doctype="POS Closing Shift"] .form-control:focus {
			border-color: #667eea !important;
			box-shadow: 0 0 0 0.25rem rgba(102, 126, 234, 0.25) !important;
			transform: scale(1.02);
		}

		/* Status Indicators */
		.pos-closing-indicator {
			position: fixed;
			top: 20px;
			right: 20px;
			padding: 10px 20px;
			border-radius: 25px;
			color: white;
			font-weight: 600;
			z-index: 1000;
			box-shadow: 0 4px 15px rgba(0,0,0,0.2);
		}
		
		/* Responsive Design */
		@media (max-width: 768px) {
			.frappe-control[data-doctype="POS Closing Shift"] .form-layout {
				padding: 10px !important;
			}
			
			.frappe-control[data-doctype="POS Closing Shift"] .section-head {
				padding: 12px 15px !important;
				font-size: 0.9rem !important;
			}
		}
		</style>
	`;
	
	if (!$('#pos-closing-custom-styles').length) {
		$('head').append(style);
	}
}

function update_form_indicators(frm) {
	// Remove existing indicators
	$('.pos-closing-indicator').remove();
	
	let indicator_class = '';
	let indicator_text = '';
	
	if (frm.doc.docstatus === 0) {
		indicator_class = 'bg-warning';
		indicator_text = __('Draft');
	} else if (frm.doc.docstatus === 1) {
		indicator_class = 'bg-success';
		indicator_text = __('Submitted');
	} else if (frm.doc.docstatus === 2) {
		indicator_class = 'bg-danger';
		indicator_text = __('Cancelled');
	}
	
	if (indicator_text) {
		$('body').append(`
			<div class="pos-closing-indicator ${indicator_class}">
				<i class="fa fa-circle" style="margin-right: 8px;"></i>
				${indicator_text}
			</div>
		`);
	}
}

function show_loading_indicator(frm, message) {
	frm.dashboard.show_progress(__('Processing'), 0, message);
}

function hide_loading_indicator(frm) {
	frm.dashboard.hide_progress();
}

function show_detailed_modal(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __('Detailed Closing Shift Report'),
		fields: [
			{
				fieldname: 'report_html',
				fieldtype: 'HTML',
				options: `
					<div style="max-height: 70vh; overflow-y: auto;">
						${frm.get_field("payment_reconciliation_details").$wrapper.html()}
					</div>
				`
			}
		],
		size: 'large'
	});
	dialog.show();
}

function export_summary(frm) {
	const summary_data = {
		shift_name: frm.doc.name,
		period_start: frm.doc.period_start_date,
		period_end: frm.doc.period_end_date,
		cashier: frm.doc.user,
		grand_total: frm.doc.grand_total,
		net_total: frm.doc.net_total,
		total_quantity: frm.doc.total_quantity,
		payment_methods: frm.doc.payment_reconciliation.map(p => ({
			mode: p.mode_of_payment,
			amount: p.expected_amount - p.opening_amount
		}))
	};
	
	// Create CSV content
	let csv_content = "data:text/csv;charset=utf-8,";
	csv_content += "Field,Value\n";
	csv_content += `Shift Name,${summary_data.shift_name}\n`;
	csv_content += `Period Start,${summary_data.period_start}\n`;
	csv_content += `Period End,${summary_data.period_end}\n`;
	csv_content += `Cashier,${summary_data.cashier}\n`;
	csv_content += `Grand Total,${summary_data.grand_total}\n`;
	csv_content += `Net Total,${summary_data.net_total}\n`;
	csv_content += `Total Quantity,${summary_data.total_quantity}\n`;
	csv_content += "\nPayment Methods\n";
	csv_content += "Mode,Amount\n";
	
	summary_data.payment_methods.forEach(pm => {
		csv_content += `${pm.mode},${pm.amount}\n`;
	});
	
	const encoded_uri = encodeURI(csv_content);
	const link = document.createElement("a");
	link.setAttribute("href", encoded_uri);
	link.setAttribute("download", `closing_shift_${frm.doc.name}.csv`);
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
	
	frappe.show_alert({
		message: __('Summary exported successfully'),
		indicator: 'green'
	});
}