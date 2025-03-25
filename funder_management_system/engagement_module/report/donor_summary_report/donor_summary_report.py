# Copyright (c) 2025, Tech4Good Community and contributors
# For license information, please see license.txt

# import frappe
from frappe import _


import frappe

def execute(filters: dict | None = None):
    """Return columns and hierarchical data for the report."""
    columns = get_columns()
    data = get_data()

    return columns, data

def get_columns():
    """Define report columns."""
    return [
        {"fieldname": "entity", "label": "Entity", "fieldtype": "Data", "width": 300},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency", "width": 150},
        {"fieldname": "received_amount", "label": "Amount Received", "fieldtype": "Currency", "width": 150},
        {"fieldname": "utilised_amount", "label": "Utilised Amount", "fieldtype": "Currency", "width": 150},
        {"fieldname": "available_amount", "label": "Available Amount", "fieldtype": "Currency", "width": 150},
    ]

def get_data():
    """Fetch hierarchical data for the report."""
    donors = frappe.get_all("Donor", fields=["name", "donor_name"])
    report_data = []

    for donor in donors:
        report_data.append({
            "entity": donor["donor_name"],
            "indent": 0,
            "status": None,
            "total_amount": sum((grant.total_grant_amount or 0) for grant in frappe.get_all("Grant Agreement", filters={"donor": donor["name"]}, fields=["total_grant_amount"])),
            "received_amount": sum((grant.total_tranche_amount_received or 0) for grant in frappe.get_all("Grant Agreement", filters={"donor": donor["name"]}, fields=["total_tranche_amount_received"])),
            "utilised_amount": sum((grant.total_grant_amount_utilised or 0) for grant in frappe.get_all("Grant Agreement", filters={"donor": donor["name"]}, fields=["total_grant_amount_utilised"])),
            "available_amount": sum((grant.total_grant_amount or 0) - (grant.total_grant_amount_utilised or 0) for grant in frappe.get_all("Grant Agreement", filters={"donor": donor["name"]}, fields=["total_grant_amount", "total_grant_amount_utilised"])),
           
        })

        grant_agreements = frappe.get_all("Grant Agreement", 
                                          filters={"donor": donor["name"]}, 
                                          fields=["name", "grant_name", "total_grant_amount","total_tranche_amount_received","total_grant_amount_utilised"])

        for grant in grant_agreements:
            report_data.append({
                "entity": f"{grant['grant_name']}",
                "indent": 1,
                "status": None,
                "total_amount": grant["total_grant_amount"],
                "received_amount": grant["total_tranche_amount_received"],
                "utilised_amount": grant["total_grant_amount_utilised"],
                "available_amount": grant["total_grant_amount"] - grant["total_grant_amount_utilised"]
               
            })

            tranches = frappe.get_all("Tranche Details", 
                                      filters={"parent": grant["name"]}, 
                                      fields=["tranche_name", "tranche_status", "tranche_amount","total_tranche_expenditure"],
                                      order_by="tranche_name asc")

            for tranche in tranches:
                report_data.append({
                    "entity": '<span style="margin-left: 1em;">&#x21B3;</span>'+f"{tranche['tranche_name']}",
                    "indent": 2,
                    "status": tranche["tranche_status"],
                    "total_amount": tranche["tranche_amount"],
                    "received_amount": tranche["tranche_amount"] if tranche["tranche_status"] in ["Received - On Time", "Received - Delayed"] else None,
                    "utilised_amount": tranche["total_tranche_expenditure"],
                    "available_amount": tranche["tranche_amount"] - tranche["total_tranche_expenditure"], 
                   
                })

    return report_data
