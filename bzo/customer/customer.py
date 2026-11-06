import frappe


def validate(doc, method=None):
	"""Doc event cho Customer (khai bao trong hooks.py -> doc_events)."""
	if doc.get("custom_bzo_code"):
		doc.custom_bzo_code = doc.custom_bzo_code.strip().upper()

		duplicate = frappe.db.exists(
			"Customer", {"custom_bzo_code": doc.custom_bzo_code, "name": ["!=", doc.name]}
		)
		if duplicate:
			frappe.throw(f"Bzo Code {doc.custom_bzo_code} da duoc dung boi {duplicate}")
