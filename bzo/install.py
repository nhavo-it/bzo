import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

VN = "eval:doc.country=='Vietnam'"
NOT_VN = "eval:doc.country!='Vietnam'"

CUSTOM_FIELDS = {
	"Customer": [
		{
			"fieldname": "bzo_section",
			"label": "Bzo",
			"fieldtype": "Section Break",
			"insert_after": "customer_details",
			"collapsible": 1,
		},
		{
			"fieldname": "custom_bzo_code",
			"label": "Bzo Code",
			"fieldtype": "Data",
			"insert_after": "bzo_section",
			"unique": 0,
			"in_standard_filter": 1,
		},
	],
	"Address": [
		{
			"fieldname": "custom_province",
			"label": "Province/City",
			"fieldtype": "Link",
			"options": "Province",
			"insert_after": "address_line1",
			"depends_on": VN,
			"mandatory_depends_on": VN,
			"in_standard_filter": 1,
			"allow_in_quick_entry": 1,
		},
		{
			"fieldname": "custom_ward",
			"label": "Ward/Commune/Special Zone",
			"fieldtype": "Link",
			"options": "Ward",
			"insert_after": "custom_province",
			"depends_on": VN,
			"mandatory_depends_on": VN,
			"in_standard_filter": 1,
			"allow_in_quick_entry": 1,
		},
	],
}

# (doctype, fieldname, property, value, property_type)
PROPERTY_SETTERS = [
	# VN addresses have no district level; city/state are auto-filled from Ward/Province
	("Address", "city", "reqd", 0, "Check"),
	# Quick entry only shows reqd fields, so keep City there for non-VN addresses
	("Address", "city", "allow_in_quick_entry", 1, "Check"),
	("Address", "city", "mandatory_depends_on", NOT_VN, "Small Text"),
	("Address", "city", "depends_on", NOT_VN, "Small Text"),
	("Address", "state", "depends_on", NOT_VN, "Small Text"),
	("Address", "address_line2", "depends_on", NOT_VN, "Small Text"),
	("Address", "pincode", "depends_on", NOT_VN, "Small Text"),
	("Address", "county", "depends_on", NOT_VN, "Small Text"),
]

ADDRESS_TEMPLATE = """{{ address_line1 }}<br>{% if address_line2 %}{{ address_line2 }}<br>{% endif -%}
{{ city }}{% if state %}, {{ state }}{% endif %}<br>
{% if pincode %}{{ pincode }}<br>{% endif -%}
{% if country %}{{ country }}<br>{% endif -%}
{% if phone %}Phone: {{ phone }}<br>{% endif -%}
{% if email_id %}Email: {{ email_id }}<br>{% endif -%}"""


def after_install():
	setup_all()


def setup_all():
	"""Idempotent: dung cho after_install va patch."""
	create_custom_fields(CUSTOM_FIELDS, update=True)
	make_property_setters()
	create_vietnam_address_template()
	add_contacts_sidebar_items()

	from bzo.address.vn_divisions import import_divisions

	import_divisions()


def make_property_setters():
	for doctype, fieldname, prop, value, prop_type in PROPERTY_SETTERS:
		make_property_setter(
			doctype, fieldname, prop, value, prop_type, validate_fields_for_doctype=False
		)


def create_vietnam_address_template():
	if not frappe.db.exists("Country", "Vietnam") or frappe.db.exists("Address Template", "Vietnam"):
		return

	frappe.get_doc(
		{"doctype": "Address Template", "country": "Vietnam", "template": ADDRESS_TEMPLATE}
	).insert(ignore_permissions=True)


CONTACTS_SIDEBAR_ITEMS = [
	{"type": "Link", "label": "Province", "link_type": "DocType", "link_to": "Province", "icon": "map"},
	{"type": "Link", "label": "Ward", "link_type": "DocType", "link_to": "Ward", "icon": "map-pinned"},
]


# Base rows of frappe's Contacts sidebar that come before our items
CONTACTS_SIDEBAR_BEFORE = ["Address", "Contact", "Address Template", "Gender", "Salutation"]


def add_contacts_sidebar_items():
	"""Them Province/Ward sau Salutation trong sidebar Contacts, qua lop Custom Sidebar cua site."""
	from frappe.desk.doctype.custom_sidebar.custom_sidebar import SITE_LAYER

	ours = {item["link_to"] for item in CONTACTS_SIDEBAR_ITEMS}

	def is_doctype_row(row, name):
		return row.get("link_type") == "DocType" and row.get("link_to") == name

	name = frappe.db.exists("Custom Sidebar", {"module": "Contacts", "user": ["in", ["", None]]})
	if name:
		doc = frappe.get_doc("Custom Sidebar", name)
	else:
		doc = frappe.new_doc("Custom Sidebar")
		doc.module = "Contacts"
		doc.user = SITE_LAYER

	items = [
		row.as_dict(no_default_fields=True)
		for row in doc.sidebar_items
		if not (row.link_type == "DocType" and row.link_to in ours)
	]
	# A layer only positions the rows it names, so name the base rows up to Salutation
	for dt in CONTACTS_SIDEBAR_BEFORE:
		if not any(is_doctype_row(row, dt) for row in items):
			items.append({"type": "Link", "link_type": "DocType", "link_to": dt})

	pos = next(i for i, row in enumerate(items) if is_doctype_row(row, "Salutation")) + 1
	items[pos:pos] = [{**item, "added": 1} for item in CONTACTS_SIDEBAR_ITEMS]

	doc.set("sidebar_items", [])
	for row in items:
		doc.append("sidebar_items", row)
	doc.save(ignore_permissions=True)


def before_uninstall():
	for doctype, fields in CUSTOM_FIELDS.items():
		for df in fields:
			name = frappe.db.get_value("Custom Field", {"dt": doctype, "fieldname": df["fieldname"]})
			if name:
				frappe.delete_doc("Custom Field", name, force=True)

	for doctype, fieldname, prop, _value, _type in PROPERTY_SETTERS:
		frappe.db.delete(
			"Property Setter", {"doc_type": doctype, "field_name": fieldname, "property": prop}
		)
