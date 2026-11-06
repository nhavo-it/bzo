frappe.query_reports["Bzo Request Summary"] = {
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
		{ fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer" },
	],
};
