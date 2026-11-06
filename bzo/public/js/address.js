const BZO_VN = "Vietnam";

async function bzo_set_state(frm) {
	if (!frm.doc.custom_province) {
		return frm.set_value("state", "");
	}
	const r = await frappe.db.get_value("Province", frm.doc.custom_province, "province_name");
	return frm.set_value("state", r.message.province_name);
}

frappe.ui.form.on("Address", {
	setup(frm) {
		frm.set_query("custom_ward", () => ({
			filters: frm.doc.custom_province ? { province: frm.doc.custom_province } : {},
		}));
	},

	onload(frm) {
		if (frm.is_new() && !frm.doc.country) {
			frm.set_value("country", BZO_VN);
		}
	},

	async custom_province(frm) {
		if (frm._bzo_syncing) return;
		await frm.set_value("custom_ward", null);
		await frm.set_value("city", "");
		await bzo_set_state(frm);
	},

	async custom_ward(frm) {
		if (!frm.doc.custom_ward) {
			return frm.set_value("city", "");
		}
		const r = await frappe.db.get_value("Ward", frm.doc.custom_ward, ["ward_name", "province"]);
		await frm.set_value("city", r.message.ward_name);
		if (r.message.province !== frm.doc.custom_province) {
			frm._bzo_syncing = true;
			await frm.set_value("custom_province", r.message.province);
			frm._bzo_syncing = false;
			await bzo_set_state(frm);
		}
	},
});
