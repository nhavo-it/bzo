import frappe

VIETNAM = "Vietnam"


def set_quick_entry_divisions(doc, method=None):
	"""Customer/Supplier before_insert: ERPNext make_address() drops custom fields, so hand them to Address.validate."""
	province, ward = doc.get("custom_province"), doc.get("custom_ward")
	if doc.get("country") != VIETNAM or not doc.get("address_line1") or not (province or ward):
		return

	if ward:
		# make_address() requires city
		doc.city = frappe.db.get_value("Ward", ward, "ward_name")
	frappe.flags.bzo_quick_entry_divisions = (province, ward)


def validate(doc, method=None):
	"""Sync custom_province/custom_ward -> state/city on Address (2-level administrative model)."""
	divisions = frappe.flags.pop("bzo_quick_entry_divisions", None)
	if divisions and doc.is_new() and not (doc.custom_province or doc.custom_ward):
		doc.custom_province, doc.custom_ward = divisions

	if doc.country != VIETNAM:
		return

	if doc.custom_ward:
		ward_name, province = frappe.db.get_value("Ward", doc.custom_ward, ["ward_name", "province"])
		if doc.custom_province and doc.custom_province != province:
			frappe.throw(f"Ward {ward_name} does not belong to the selected province")
		doc.custom_province = province
		doc.city = ward_name

	if doc.custom_province:
		doc.state = frappe.db.get_value("Province", doc.custom_province, "province_name")
