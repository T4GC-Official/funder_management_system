# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OrganisationPOC(Document):
	def validate(self):
		autoname(self)


def autoname(doc):
	if not doc.organisation:
		frappe.throw("Please select an Organisation")

	org_name = frappe.db.get_value("Organisation Details", doc.organisation, "organisation_name")
	existing_count = frappe.db.count("Organisation POC", {"organisation": doc.organisation})
	doc.id = f"{org_name}-{existing_count + 1}"
