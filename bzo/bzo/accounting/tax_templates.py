import frappe

VAT_RATES = [
	{"title": "VAT 0% - Xuất khẩu", "rate": 0, "description": "Thuế suất 0% cho hàng xuất khẩu"},
	{"title": "VAT 5% - Thiết yếu", "rate": 5, "description": "Thuế suất 5% cho hàng thiết yếu"},
	{"title": "VAT 8% - Giảm thuế", "rate": 8, "description": "Thuế suất 8% theo Nghị quyết giảm thuế"},
	{"title": "VAT 10% - Phổ thông", "rate": 10, "description": "Thuế suất phổ thông 10%"},
]


def create_tax_templates(company):
	"""Create Sales/Purchase VAT templates for a company using a VN chart of accounts.

	33311 (output VAT) and 1331 (input VAT) exist in the TT99 chart.
	"""
	abbr = frappe.get_cached_value("Company", company, "abbr")

	sales_tax_account = f"33311 - Thuế GTGT đầu ra - {abbr}"
	purchase_tax_account = f"1331 - Thuế GTGT được khấu trừ của hàng hóa, dịch vụ - {abbr}"

	if not frappe.db.exists("Account", sales_tax_account):
		sales_tax_account = _find_account(company, ["33311"])
	if not frappe.db.exists("Account", purchase_tax_account):
		purchase_tax_account = _find_account(company, ["1331"])
	if not (sales_tax_account and purchase_tax_account):
		return

	for doctype, account in (
		("Sales Taxes and Charges Template", sales_tax_account),
		("Purchase Taxes and Charges Template", purchase_tax_account),
	):
		for vat in VAT_RATES:
			if frappe.db.exists(doctype, f"{vat['title']} - {abbr}"):
				continue
			frappe.get_doc(
				{
					"doctype": doctype,
					"title": vat["title"],
					"company": company,
					"taxes": [
						{
							"charge_type": "On Net Total",
							"account_head": account,
							"description": vat["description"],
							"rate": vat["rate"],
						}
					],
				}
			).insert(ignore_permissions=True)


def _find_account(company, account_numbers):
	for number in account_numbers:
		name = frappe.db.get_value(
			"Account", {"company": company, "account_number": number, "is_group": 0}, "name"
		)
		if name:
			return name
