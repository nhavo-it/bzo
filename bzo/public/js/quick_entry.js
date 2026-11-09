// Them Tinh/Thanh + Xa/Phuong vao Quick Entry cua Customer/Supplier
frappe.provide("frappe.ui.form");

(() => {
	// Empty Country also counts as Vietnam, in case the user clears the default
	const VN = "eval:!doc.country_address || doc.country_address=='Vietnam'";
	const NOT_VN = "eval:doc.country_address && doc.country_address!='Vietnam'";
	const VN_REQD = "eval:(!doc.country_address || doc.country_address=='Vietnam') && doc.address_line1";
	const PARTIES = ["Customer", "Supplier"];
	const ADDRESS_ORDER = [
		"address_line1",
		"custom_province",
		"custom_ward",
		"country_address",
		"address_line2",
		"city",
		"state",
		"pincode",
	];

	// ERPNext usually aliases both to the shared ContactAddressQuickEntryForm, but some builds ship separate classes
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
			// The shared class also serves other doctypes; leave them as ERPNext ships them
			if (!PARTIES.includes(this.doctype)) return fields;
			if (fields.some((df) => df.fieldname === "custom_province")) return fields;

			for (const df of fields) {
				if (["address_line2", "pincode", "city", "state"].includes(df.fieldname)) {
					df.depends_on = NOT_VN;
				}
				if (df.fieldname === "city") {
					df.mandatory_depends_on = NOT_VN;
				}
				if (df.fieldname === "address_line1") {
					// The default Country alone must not make the address mandatory
					df.mandatory_depends_on =
						"eval:doc.city || doc.custom_province || doc.custom_ward || (doc.country_address && doc.country_address!='Vietnam')";
				}
				if (df.fieldname === "country_address") {
					df.default = "Vietnam";
				}
			}

			const first = fields.findIndex((df) => df.fieldname === "address_line1");
			if (first === -1) return fields;
			let last = first;
			fields.forEach((df, i) => {
				if (ADDRESS_ORDER.includes(df.fieldname)) last = i;
			});

			const by_name = Object.fromEntries(fields.map((df) => [df.fieldname, df]));
			by_name.custom_province = {
				label: __("Province/City"),
				fieldname: "custom_province",
				fieldtype: "Link",
				options: "Province",
				depends_on: VN,
				mandatory_depends_on: VN_REQD,
			};
			by_name.custom_ward = {
				label: __("Ward/Commune/Special Zone"),
				fieldname: "custom_ward",
				fieldtype: "Link",
				options: "Ward",
				depends_on: VN,
				mandatory_depends_on: VN_REQD,
			};
			// One column, so the VN layout has no empty right column
			const block = ADDRESS_ORDER.map((name) => by_name[name]).filter(Boolean);
			fields.splice(first, last - first + 1, ...block);
			return fields;
		};

		proto.render_dialog = function () {
			if (PARTIES.includes(this.doctype) && this.doc && !this.doc.country_address) {
				// The dialog reads its values from this.doc, so a field default alone is not shown
				this.doc.country_address = "Vietnam";
			}
			render_dialog.call(this);
			if (!PARTIES.includes(this.doctype)) return;
			if (!this.dialog.get_value("country_address")) {
				this.dialog.set_value("country_address", "Vietnam");
			}
			bzo_bind_divisions(this.dialog);
		};
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
