import frappe
from frappe.model.document import Document


class BzoRequest(Document):
	def validate(self):
		if self.request_date and self.request_date > frappe.utils.today():
			frappe.throw("Request Date khong duoc o tuong lai")
