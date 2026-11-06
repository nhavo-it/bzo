// Mo rong form Customer cua ERPNext (khai bao trong hooks.py -> doctype_js)
frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button(__("Tao Bzo Request"), () => {
			frappe.new_doc("Bzo Request", { customer: frm.doc.name });
		}, __("Tao"));
	},
});
