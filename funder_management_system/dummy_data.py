import frappe, json
from datetime import datetime
    
    
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

        print(f"Test user {email} created with role '{role}' Password : {default_password}")
        frappe.db.commit()
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
def create_dummy_records():
    insert_dummy_budget_category_and_sub_categories()
    create_test_users()

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
