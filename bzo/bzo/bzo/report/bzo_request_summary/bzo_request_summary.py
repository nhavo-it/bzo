import frappe


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters), None, get_chart(filters)


def get_columns():
	return [
		{"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 220},
		{"label": "Open", "fieldname": "open_count", "fieldtype": "Int", "width": 100},
		{"label": "In Progress", "fieldname": "in_progress_count", "fieldtype": "Int", "width": 110},
		{"label": "Closed", "fieldname": "closed_count", "fieldtype": "Int", "width": 100},
		{"label": "Total", "fieldname": "total", "fieldtype": "Int", "width": 100},
	]


def get_data(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " AND request_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND request_date <= %(to_date)s"
	if filters.get("customer"):
		conditions += " AND customer = %(customer)s"

	return frappe.db.sql(
		f"""
		SELECT
			customer,
			customer_name,
			SUM(status = 'Open') AS open_count,
			SUM(status = 'In Progress') AS in_progress_count,
			SUM(status = 'Closed') AS closed_count,
			COUNT(*) AS total
		FROM `tabBzo Request`
		WHERE docstatus < 2 {conditions}
		GROUP BY customer, customer_name
		ORDER BY total DESC
		""",
		filters,
		as_dict=True,
	)


def get_chart(filters):
	rows = get_data(filters)
	return {
		"data": {
			"labels": ["Open", "In Progress", "Closed"],
			"datasets": [
				{
					"name": "Requests",
					"values": [
						sum(r.open_count or 0 for r in rows),
						sum(r.in_progress_count or 0 for r in rows),
						sum(r.closed_count or 0 for r in rows),
					],
				}
			],
		},
		"type": "donut",
	}
