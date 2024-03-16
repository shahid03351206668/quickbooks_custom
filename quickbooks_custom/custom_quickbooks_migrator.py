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

def _save_vendor(self, vendor):
	try:
		if not frappe.db.exists(
			{"doctype": "Supplier", "quickbooks_id": vendor["Id"], "company": self.company}
		):
			erpsupplier = frappe.get_doc(
				{
					"doctype": "Supplier",
					"quickbooks_id": vendor["Id"],
					"supplier_name": encode_company_abbr(vendor["DisplayName"], self.company),
					"supplier_group": "All Supplier Groups",
					"company": self.company,
				}
			).insert()
			if "BillAddr" in vendor:
				create_address(erpsupplier, "Supplier", vendor["BillAddr"], "Billing")
			if "ShipAddr" in vendor:
				create_address(erpsupplier, "Supplier", vendor["ShipAddr"], "Shipping")
	except Exception as e:
		self._log_error(e)

def _save_customer(self, customer):
	try:
		if not frappe.db.exists(
			{"doctype": "Customer", "quickbooks_id": customer["Id"], "company": self.company}
		):
			try:
				receivable_account = frappe.get_all(
					"Account",
					filters={
						"account_type": "Receivable",
						"account_currency": customer["CurrencyRef"]["value"],
						"company": self.company,
					},
				)[0]["name"]
			except Exception:
				receivable_account = None
			erpcustomer = frappe.get_doc(
				{
					"doctype": "Customer",
					"quickbooks_id": customer["Id"],
					"customer_name": encode_company_abbr(customer["DisplayName"], self.company),
					"customer_type": "Individual",
					"customer_group": "Commercial",
					"default_currency": customer["CurrencyRef"]["value"],
					"accounts": [{"company": self.company, "account": receivable_account}],
					"territory": "All Territories",
					"company": self.company,
				}
			).insert()
			if "BillAddr" in customer:
				create_address(erpcustomer, "Customer", customer["BillAddr"], "Billing")
			if "ShipAddr" in customer:
				create_address(erpcustomer, "Customer", customer["ShipAddr"], "Shipping")
	except Exception as e:
		self._log_error(e, customer)


# QuickBooksMigrator.create_address = create_address
QuickBooksMigrator._save_vendor = _save_vendor
QuickBooksMigrator._save_customer = _save_customer