// Them Tinh/Thanh + Xa/Phuong vao Quick Entry cua Customer/Supplier (ERPNext dung chung ContactAddressQuickEntryForm)
frappe.provide("frappe.ui.form");

(() => {
	const VN = "eval:doc.country_address=='Vietnam'";
	const NOT_VN = "eval:doc.country_address!='Vietnam'";
	const proto = frappe.ui.form.ContactAddressQuickEntryForm.prototype;
	const get_variant_fields = proto.get_variant_fields;
	const render_dialog = proto.render_dialog;

	proto.get_variant_fields = function () {
		const fields = get_variant_fields.call(this);

		for (const df of fields) {
			if (["address_line2", "pincode", "city", "state"].includes(df.fieldname)) {
				df.depends_on = NOT_VN;
			}
			if (df.fieldname === "city") {
				df.mandatory_depends_on =
					"eval:doc.country_address!='Vietnam' && (doc.country_address || doc.address_line1)";
			}
		}

		const idx = fields.findIndex((df) => df.fieldname === "country_address");
		fields.splice(
			idx + 1,
			0,
			{
				label: __("Province/City"),
				fieldname: "custom_province",
				fieldtype: "Link",
				options: "Province",
				depends_on: VN,
				mandatory_depends_on: VN,
			},
			{
				label: __("Ward/Commune/Special Zone"),
				fieldname: "custom_ward",
				fieldtype: "Link",
				options: "Ward",
				depends_on: VN,
				mandatory_depends_on: VN,
			}
		);
		return fields;
	};

	proto.render_dialog = function () {
		render_dialog.call(this);

		const d = this.dialog;
		const province = d.fields_dict.custom_province;
		const ward = d.fields_dict.custom_ward;
		if (!province || !ward) return;

		ward.get_query = () => {
			const p = d.get_value("custom_province");
			return { filters: p ? { province: p } : {} };
		};

		province.df.onchange = () => {
			const w = d.get_value("custom_ward");
			if (!w) return;
			frappe.db.get_value("Ward", w, "province").then((r) => {
				if (r.message.province !== d.get_value("custom_province")) {
					d.set_value("custom_ward", null);
				}
			});
		};

		ward.df.onchange = () => {
			const w = d.get_value("custom_ward");
			if (!w) return;
			frappe.db.get_value("Ward", w, "province").then((r) => {
				if (r.message.province !== d.get_value("custom_province")) {
					d.set_value("custom_province", r.message.province);
				}
			});
		};
	};
})();
