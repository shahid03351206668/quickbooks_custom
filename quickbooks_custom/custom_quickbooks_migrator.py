# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from erpnext.erpnext_integrations.doctype.quickbooks_migrator.quickbooks_migrator import QuickBooksMigrator

def create_address(self, entity, doctype, address, address_type):
	try:
		if not frappe.db.exists({"doctype": "Address", "quickbooks_id": address.get("Id")}):
			frappe.get_doc(
				{
					"doctype": "Address",
					"quickbooks_address_id": address.get("Id"),
					"address_title": entity.name,
					"address_type": address_type,
					"address_line1": address.get("Line1"),
					"city": address.get("City"),
					"links": [{"link_doctype": doctype, "link_name": entity.name}],
				}
			).insert()
	except Exception as e:
		self._log_error(e, address)


QuickBooksMigrator._create_address = create_address