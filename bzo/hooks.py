app_name = "bzo"
app_title = "Bzo"
app_publisher = "Bzo"
app_description = "Tuy chinh ERPNext 16"
app_email = "dev@example.com"
app_license = "mit"

# Ung dung phu thuoc
required_apps = ["frappe", "erpnext"]

# Quick Entry Customer/Supplier: them Tinh/Thanh + Xa/Phuong
app_include_js = "/assets/bzo/js/quick_entry.js"

# JS mo rong form cua DocType co san
doctype_js = {
	"Address": "public/js/address.js",
}

# Doc events
doc_events = {
	"Company": {
		"on_update": "bzo.accounting.company.on_update",
	},
	"Customer": {
		"before_insert": "bzo.address.address.set_quick_entry_divisions",
		"validate": "bzo.customer.customer.validate",
	},
	"Address": {
		"validate": "bzo.address.address.validate",
	},
}

# Chart of Accounts Vietnam (TT99/2025)
override_whitelisted_methods = {
	"erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_charts_for_country": "bzo.accounting.chart_of_accounts.get_charts_for_country",
}
before_request = ["bzo.accounting.chart_of_accounts.ensure_patched"]
boot_session = "bzo.accounting.chart_of_accounts.ensure_patched"

# Install
after_install = "bzo.install.after_install"
before_uninstall = "bzo.install.before_uninstall"

# Fixtures (xuat bang `bench --site <site> export-fixtures`)
# fixtures = [
# 	{"dt": "Custom Field", "filters": [["module", "=", "Bzo"]]},
# ]

# Scheduler
# scheduler_events = {
# 	"daily": ["bzo.tasks.daily"],
# }
