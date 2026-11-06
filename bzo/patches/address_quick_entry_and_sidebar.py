from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from bzo.install import CUSTOM_FIELDS, add_contacts_sidebar_items, make_property_setters


def execute():
	create_custom_fields(CUSTOM_FIELDS, update=True)
	make_property_setters()
	add_contacts_sidebar_items()
