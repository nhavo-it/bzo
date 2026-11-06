import json
from pathlib import Path

import frappe

DATA_FILE = Path(__file__).resolve().parent / "data" / "vn_divisions.json"

PROVINCE_TYPES = {"tỉnh": "Province", "thành phố trung ương": "Municipality"}
WARD_TYPES = {"phường": "Ward", "xã": "Commune", "đặc khu": "Special Zone"}


def import_divisions():
	"""Import 34 provinces and 3321 wards/communes/special zones (2-level model, effective 2025-07-01).

	Idempotent: existing records are skipped.
	"""
	with open(DATA_FILE, encoding="utf-8") as f:
		provinces = json.load(f)

	existing_provinces = set(frappe.get_all("Province", pluck="name"))
	existing_wards = set(frappe.get_all("Ward", pluck="name"))

	for p in provinces:
		province_code = str(p["code"])
		if province_code not in existing_provinces:
			frappe.get_doc(
				{
					"doctype": "Province",
					"province_code": province_code,
					"province_name": p["name"],
					"type": PROVINCE_TYPES.get(p["division_type"], "Province"),
				}
			).insert(ignore_permissions=True)

		for w in p.get("wards", []):
			ward_code = str(w["code"])
			if ward_code in existing_wards:
				continue
			frappe.get_doc(
				{
					"doctype": "Ward",
					"ward_code": ward_code,
					"ward_name": w["name"],
					"type": WARD_TYPES.get(w["division_type"], "Ward"),
					"province": province_code,
					"province_name": p["name"],
				}
			).insert(ignore_permissions=True)

	frappe.db.commit()
