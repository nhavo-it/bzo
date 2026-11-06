import frappe

from bzo.accounting.tax_templates import create_tax_templates


def on_update(doc, method=None):
	"""Company on_update: create VAT templates once the VN chart of accounts exists."""
	if doc.country != "Vietnam" or not doc.flags.in_insert:
		return

	if not frappe.db.exists("Account", {"company": doc.name, "account_number": "33311"}):
		return

	create_tax_templates(doc.name)
