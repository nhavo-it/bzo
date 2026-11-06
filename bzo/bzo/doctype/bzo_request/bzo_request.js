frappe.ui.form.on("Bzo Request", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.status !== "Closed") {
			frm.add_custom_button(__("Close"), () => {
				frm.set_value("status", "Closed");
				frm.save();
			});
		}
	},
});
