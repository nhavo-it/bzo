"""Chart of Accounts Vietnam (TT99/2025).

- ``get_charts_for_country`` replaces ERPNext's RPC of the same name (via the
  ``override_whitelisted_methods`` hook) so the dropdown lists our chart when
  creating a Company with country = Vietnam.
- ``ensure_patched`` monkey-patches ERPNext internals that are imported
  directly (not via RPC): ``get_chart`` loads our JSON tree and
  ``sync_financial_report_templates`` skips our chart. Called from the
  ``before_request`` and ``boot_session`` hooks and once on module import.

Chart data lives in ``bzo/accounting/data/``. Tree keys are plain account
names; ERPNext prepends ``account_number`` itself.
"""

import json
import os

import frappe

COA_DIR = os.path.join(os.path.dirname(__file__), "data")

CHARTS = {
	"Vietnam - Hệ thống tài khoản TT99/2025": "vn_tt99.json",
}

_PATCHED = False


@frappe.whitelist()
def get_charts_for_country(country, with_standard=False):
	"""Return ERPNext's standard charts for the country plus the Vietnamese one."""
	ensure_patched()

	from erpnext.accounts.doctype.account.chart_of_accounts import chart_of_accounts as erpnext_coa

	charts = []

	def _add_chart_name(content):
		if content:
			content = json.loads(content)
			if (
				content and content.get("disabled", "No") == "No"
			) or frappe.local.flags.allow_unverified_charts:
				charts.append(content["name"])

	country_code = frappe.get_cached_value("Country", country, "code")
	if country_code:
		folders = ("verified",)
		if frappe.local.flags.allow_unverified_charts:
			folders = ("verified", "unverified")

		for folder in folders:
			path = os.path.join(os.path.dirname(erpnext_coa.__file__), folder)
			if not os.path.exists(path):
				continue
			for fname in os.listdir(path):
				fname = frappe.as_unicode(fname)
				if (fname.startswith(country_code) or fname.startswith(country)) and fname.endswith(".json"):
					with open(os.path.join(path, fname), encoding="utf-8") as f:
						_add_chart_name(f.read())

	if country == "Vietnam":
		for chart_name in CHARTS:
			if chart_name not in charts:
				charts.append(chart_name)

	if len(charts) != 1 or with_standard:
		charts += ["Standard", "Standard with Numbers"]

	return charts


def get_vn_chart(chart_template):
	"""Return the account tree if chart_template is one of ours, else None."""
	filename = CHARTS.get(chart_template)
	if not filename:
		return None
	with open(os.path.join(COA_DIR, filename), encoding="utf-8") as f:
		return json.load(f).get("tree")


def ensure_patched(bootinfo=None):
	"""Idempotent monkey-patch of ERPNext's chart loading."""
	global _PATCHED
	if _PATCHED:
		return

	try:
		from erpnext.accounts.doctype.account.chart_of_accounts import chart_of_accounts as coa_mod
		from erpnext.accounts.doctype.financial_report_template import (
			financial_report_template as frt_mod,
		)
	except ImportError:
		return

	original_get_chart = coa_mod.get_chart

	def patched_get_chart(chart_template, existing_company=None):
		vn_tree = get_vn_chart(chart_template)
		if vn_tree:
			return vn_tree
		return original_get_chart(chart_template, existing_company)

	coa_mod.get_chart = patched_get_chart

	# ERPNext's default Balance Sheet / P&L templates assume English headings.
	original_sync = frt_mod.sync_financial_report_templates

	def patched_sync(chart_of_accounts=None, existing_company=None):
		if chart_of_accounts in CHARTS:
			return
		return original_sync(chart_of_accounts, existing_company)

	frt_mod.sync_financial_report_templates = patched_sync

	# Some modules import the function by name; refresh those references.
	try:
		from erpnext.setup.doctype.company import company as company_mod

		if hasattr(company_mod, "sync_financial_report_templates"):
			company_mod.sync_financial_report_templates = patched_sync
	except ImportError:
		pass

	_PATCHED = True


ensure_patched()
