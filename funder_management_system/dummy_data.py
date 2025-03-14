import frappe, json
from datetime import datetime
    
import random

def create_dummy_records():
    try:
        create_test_users()
        insert_dummy_budget_category_and_sub_categories()
        delete_dummy_budget_plan()
        create_dummy_budget_plan()
        submit_budget_plan(1)
        create_dummy_budget_plan_template()
    except Exception as e:
        print(f"Error creating dummy records: {e}")

def random_budget():
    return random.randint(5000, 20000)

def add_test_user(email, first_name="Test", last_name="User"):
    """Creates a test user with role 'Fundraising Admin' if it doesn't exist."""
    role = "Fundraising Admin"
    default_password = "mk@" + first_name.lower() + ".com"
    try:
        # Check if user already exists
        if frappe.db.exists("User", email):
            print(f"User {email} already exists!")
            return

        # Create new user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "send_welcome_email": 0,  # Avoid sending real emails
            "new_password": default_password
        })
        user.insert(ignore_permissions=True)

        # Assign role "Fundraising Admin"
        user.add_roles(role)
        frappe.db.commit()
        print(f"Test user {email} created with role '{role}' Password : {default_password}")
        
    except Exception as e:
        frappe.log_error(f"Error creating test user {email}: {e}")
        
    
def create_test_users():
    add_test_user("vidya@tech4goodcommunity.com","Vidya","S")
    add_test_user("akansha@tech4goodcommunity.com","Akansha","Negi")
    add_test_user("ajith@tech4goodcommunity.com","Ajith","B M")
    add_test_user("chandru@tech4goodcommunity.com","Chandru","M")    
    add_test_user("praveen@tech4goodcommunity.com","Praveen","K S")    
    add_test_user("tushar@tech4goodcommunity.com","Tushar","B")    


# Insert dummy records for testing
def insert_dummy_budget_category_and_sub_categories():
    dummy_data = [
        {"budget_category": "Marketing", "budget_sub_category": "Social Media"},
        {"budget_category": "Marketing", "budget_sub_category": "Advertising"},
        {"budget_category": "Operations", "budget_sub_category": "Logistics"},
        {"budget_category": "Operations", "budget_sub_category": "Supply Chain"},
        {"budget_category": "HR", "budget_sub_category": "Recruitment"},
        {"budget_category": "HR", "budget_sub_category": "Training"},
        {"budget_category": "Finance", "budget_sub_category": "Budgeting"},
        {"budget_category": "Finance", "budget_sub_category": "Auditing"},
        {"budget_category": "IT", "budget_sub_category": "Software Development"},
        {"budget_category": "IT", "budget_sub_category": "Cybersecurity"},
    ]

    for data in dummy_data:
        # Check if category exists in "Category" Doctype
        if not frappe.db.exists("Budget Category", {"budget_category": data["budget_category"]}):
            doc = frappe.get_doc({
                "doctype": "Budget Category",
                "budget_category": data["budget_category"],
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Inserted budget category: {data['budget_category']}")

        # Check if record already exists
        if not frappe.db.exists("Budget Sub-Category", {"budget_category": data["budget_category"], "budget_sub_category": data["budget_sub_category"]}):
            doc = frappe.get_doc({
                "doctype": "Budget Sub-Category",
                "budget_category": data["budget_category"],  # Link field
                "budget_sub_category": data["budget_sub_category"],  # Text field
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Inserted: {data['budget_category']} - {data['budget_sub_category']}")


import frappe

def create_dummy_budget_plan():
    # Get all the available financial years
    financial_years = frappe.get_all("Financial Year", fields=["financial_year"], order_by="financial_year desc")

    for year in financial_years:
        # Define the categories and subcategories
        budget_items = [
            {"category": "Marketing", "sub_category": "Social Media"},
            {"category": "Marketing", "sub_category": "Advertising"},
            {"category": "Operations", "sub_category": "Logistics"},
            {"category": "Operations", "sub_category": "Supply Chain"},
            {"category": "HR", "sub_category": "Recruitment"},
            {"category": "HR", "sub_category": "Training"},
            {"category": "Finance", "sub_category": "Budgeting"},
            {"category": "Finance", "sub_category": "Auditing"},
            {"category": "IT", "sub_category": "Software Development"},
            {"category": "IT", "sub_category": "Cybersecurity"},
        ]
        
        budget_plan = None
        if not frappe.db.exists("Budget Plan", {"name": f"Budget Plan for {year.financial_year}"}):
            budget_plan = frappe.get_doc({
                "doctype": "Budget Plan",
                "name": f"Budget Plan for {year.financial_year}",
                "financial_year": year.financial_year,
                "currency": "INR",
                "budget_breakdown": [
                    {
                        "budget_category": item["category"],
                        "budget_sub_category": item["sub_category"],
                        "quarter_1_budget": random_budget(),
                        "quarter_2_budget": random_budget(),
                        "quarter_3_budget": random_budget(),
                        "quarter_4_budget": random_budget()
                    }
                    for item in budget_items
                ]
            })

        # Insert and submit the document into the database
        if budget_plan:
            budget_plan.insert()
            frappe.db.commit()
            print(f"Dummy Budget Plan {budget_plan.name} created and submitted successfully!")

def delete_dummy_budget_plan():
    financial_years = frappe.get_all("Financial Year", fields=["financial_year"], order_by="financial_year desc")
    for year in financial_years:
        budget_plan_name = f"Budget Plan for {year.financial_year}"
        if frappe.db.exists("Budget Plan", budget_plan_name):
            budget_plan = frappe.get_doc("Budget Plan", budget_plan_name)
            if budget_plan.docstatus == 1:
                budget_plan.cancel()
                frappe.db.commit()  # Ensure cancellation is saved
                print(f"Budget Plan {budget_plan_name} cancelled!")

            # Reload the document before deletion
            budget_plan = frappe.get_doc("Budget Plan", budget_plan_name)
            budget_plan.delete()
            frappe.db.commit()  # Ensure deletion is saved
            print(f"Budget Plan {budget_plan_name} deleted!")
def create_dummy_budget_plan_template():
    # Define the categories and subcategories (same as Budget Plan)
    budget_items = [
        {"category": "Marketing", "sub_category": "Social Media"},
        {"category": "Marketing", "sub_category": "Advertising"},
        {"category": "Operations", "sub_category": "Logistics"},
        {"category": "Operations", "sub_category": "Supply Chain"},
        {"category": "HR", "sub_category": "Recruitment"},
        {"category": "HR", "sub_category": "Training"},
        {"category": "Finance", "sub_category": "Budgeting"},
        {"category": "Finance", "sub_category": "Auditing"},
        {"category": "IT", "sub_category": "Software Development"},
        {"category": "IT", "sub_category": "Cybersecurity"},
    ]

    if frappe.db.exists("Budget Plan Template", "Standard Budget Template"):
        print("Dummy Budget Plan Template already exists, skipping...")
        return

    budget_plan_template = frappe.get_doc({
        "doctype": "Budget Plan Template",
        "name": "Standard Budget Template",
        "budget_detail": [  
            {
                "budget_category": item["category"],
                "budget_sub_category": item["sub_category"]
            }
            for item in budget_items
        ]
    })

    # Insert the document into the database
    budget_plan_template.insert()
    frappe.db.commit()

    print(f"Dummy Budget Plan Template {budget_plan_template.name} created successfully!")


def submit_budget_plan(number_of_record_to_be_submitted=0):
    financial_years = frappe.get_all("Financial Year", fields=["financial_year"], order_by="financial_year desc")[:number_of_record_to_be_submitted]
    for year in financial_years:
        budget_plan_name = f"Budget Plan for {year.financial_year}"
        if frappe.db.exists("Budget Plan", budget_plan_name):
            budget_plan = frappe.get_doc("Budget Plan", budget_plan_name)
            budget_plan.submit()
            frappe.db.commit()
            print(f"Budget Plan {budget_plan_name} submitted successfully!")
