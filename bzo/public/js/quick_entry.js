// Them Tinh/Thanh + Xa/Phuong vao Quick Entry cua Customer/Supplier
frappe.provide("frappe.ui.form");

(() => {
	const BZO_VN = "Vietnam";
	const PARTIES = ["Customer", "Supplier"];

	// ERPNext usually aliases both to the shared ContactAddressQuickEntryForm, but some builds ship separate classes
	const patched = new Set();
	for (const name of ["ContactAddressQuickEntryForm", "CustomerQuickEntryForm", "SupplierQuickEntryForm"]) {
		const proto = frappe.ui.form[name]?.prototype;
		if (!proto?.get_variant_fields || patched.has(proto)) continue;
		patched.add(proto);
		patch_party_quick_entry(proto);
	}

	// ERPNext v16 names the dialog's Country field `country_address`, v15 names it `country`
	function country_fieldname(fields) {
		const df = fields.find((f) => f.fieldtype === "Link" && f.options === "Country");
		return df?.fieldname || "country_address";
	}

	function patch_party_quick_entry(proto) {
		const get_variant_fields = proto.get_variant_fields;
		const render_dialog = proto.render_dialog;

		proto.get_variant_fields = function () {
			const fields = get_variant_fields.call(this);
			// The shared class also serves other doctypes; leave them as ERPNext ships them
			if (!PARTIES.includes(this.doctype)) return fields;
			if (fields.some((df) => df.fieldname === "custom_province")) return fields;

			const c = country_fieldname(fields);
			// Empty Country also counts as Vietnam, in case the user clears the default
			const VN = `eval:!doc.${c} || doc.${c}=='${BZO_VN}'`;
			const NOT_VN = `eval:doc.${c} && doc.${c}!='${BZO_VN}'`;
			const VN_REQD = `eval:(!doc.${c} || doc.${c}=='${BZO_VN}') && doc.address_line1`;

			for (const df of fields) {
				if (["address_line2", "pincode", "city", "state"].includes(df.fieldname)) {
					df.depends_on = NOT_VN;
				}
				if (df.fieldname === "city") {
					df.mandatory_depends_on = NOT_VN;
				}
				if (df.fieldname === "address_line1") {
					// The default Country alone must not make the address mandatory
					df.mandatory_depends_on = `eval:doc.city || doc.custom_province || doc.custom_ward || (doc.${c} && doc.${c}!='${BZO_VN}')`;
				}
				if (df.fieldname === c) {
					df.default = BZO_VN;
					// v16 makes Country mandatory once City is set; City is filled from Ward here
					df.mandatory_depends_on = NOT_VN;
				}
			}

			const order = [
				"address_line1",
				"custom_province",
				"custom_ward",
				c,
				"address_line2",
				"city",
				"state",
				"pincode",
			];
			const first = fields.findIndex((df) => df.fieldname === "address_line1");
			if (first === -1) return fields;
			let last = first;
			fields.forEach((df, i) => {
				if (order.includes(df.fieldname)) last = i;
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
			const block = order.map((name) => by_name[name]).filter(Boolean);
			fields.splice(first, last - first + 1, ...block);
			return fields;
		};

		proto.render_dialog = function () {
			const is_party = PARTIES.includes(this.doctype);
			const c = is_party ? country_fieldname(get_variant_fields.call(this)) : null;
			if (is_party) preset_country(this, c);
			render_dialog.call(this);
			if (!is_party) return;
			ensure_country(this.dialog || this, c);
			bzo_bind_divisions(this.dialog || this);
		};
	}

	// Quick Entry cua chinh Address (vd. "+ Tao Address" tu o Link)
	frappe.ui.form.AddressQuickEntryForm = class AddressQuickEntryForm extends (
		frappe.ui.form.QuickEntryForm
	) {
		render_dialog() {
			preset_country(this, "country");
			super.render_dialog();
			ensure_country(this.dialog || this, "country");
			bzo_bind_divisions(this.dialog || this);
		}
	};

	// QuickEntryForm.set_defaults() fills the inputs from this.doc, so the value has to be there before rendering
	function preset_country(form, fieldname) {
		form.check_quick_entry_doc?.();
		if (form.doc) form.doc[fieldname] = BZO_VN;
	}

	function ensure_country(dialog, fieldname) {
		if (dialog.get_value(fieldname) !== BZO_VN) {
			dialog.set_value(fieldname, BZO_VN);
		}
	}

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
