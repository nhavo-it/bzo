// Them Tinh/Thanh + Xa/Phuong vao Quick Entry cua Customer/Supplier
frappe.provide("frappe.ui.form");

(() => {
	const VN = "eval:doc.country_address=='Vietnam'";
	const NOT_VN = "eval:doc.country_address!='Vietnam'";

	// ERPNext usually aliases both to ContactAddressQuickEntryForm, but some builds ship separate classes
	const patched = new Set();
	for (const name of ["ContactAddressQuickEntryForm", "CustomerQuickEntryForm", "SupplierQuickEntryForm"]) {
		const proto = frappe.ui.form[name]?.prototype;
		if (!proto?.get_variant_fields || patched.has(proto)) continue;
		patched.add(proto);
		patch_party_quick_entry(proto);
	}

	function patch_party_quick_entry(proto) {
		const get_variant_fields = proto.get_variant_fields;
		const render_dialog = proto.render_dialog;

		proto.get_variant_fields = function () {
			const fields = get_variant_fields.call(this);
			if (this.doctype === "Supplier") return without_address_section(fields);
			if (fields.some((df) => df.fieldname === "custom_province")) return fields;

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
				idx === -1 ? fields.length : idx + 1,
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
			bzo_bind_divisions(this.dialog);
		};
	}

	// Drop the "Primary Address Details" section: its Section Break through the last address field
	function without_address_section(fields) {
		const first = fields.findIndex((df) => df.fieldname === "address_line1");
		if (first === -1) return fields;
		let start = first;
		while (start > 0 && fields[start - 1].fieldtype !== "Section Break") start--;
		if (start > 0) start--;
		const address = ["address_line1", "address_line2", "pincode", "city", "state", "country_address", "custom_province", "custom_ward"];
		let end = start;
		for (let i = start; i < fields.length; i++) {
			if (address.includes(fields[i].fieldname)) end = i;
		}
		return [...fields.slice(0, start), ...fields.slice(end + 1)];
	}

	// Quick Entry cua chinh Address (vd. "+ Tao Address" tu o Link)
	frappe.ui.form.AddressQuickEntryForm = class AddressQuickEntryForm extends (
		frappe.ui.form.QuickEntryForm
	) {
		render_dialog() {
			super.render_dialog();
			if (!this.dialog.get_value("country")) {
				this.dialog.set_value("country", "Vietnam");
			}
			bzo_bind_divisions(this.dialog);
		}
	};

	function bzo_bind_divisions(d) {
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
	}
})();
