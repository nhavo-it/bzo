import frappe

VIETNAM = "Vietnam"


def validate(doc, method=None):
	"""Sync custom_province/custom_ward -> state/city on Address (2-level administrative model)."""
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
