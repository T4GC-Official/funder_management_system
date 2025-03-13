import frappe, json
from datetime import datetime

def create_financial_year():
    current_year = datetime.now().year
    start_year = current_year - 5
    end_year = current_year + 5

    for year in range(start_year, end_year + 1):
        financial_year = f"{year}-{str(year + 1)[-2:]}"
        start_date = f"{year}-04-01"
        end_date = f"{year + 1}-03-31"

        if not frappe.db.exists("Financial Year", financial_year):
            doc = frappe.get_doc({
                "doctype": "Financial Year",
                "financial_year": financial_year,
                "year_start_date": start_date,
                "year_end_date": end_date
            })
            doc.insert(ignore_permissions=True)

    frappe.db.commit()
    
def set_currency_permission_using_custom():
    """Set or update Currency DocType permissions for Fundraising Admin role."""
    doctype = "Currency"
    role = "Fundraising Admin"

    try:
        existing_permissions = frappe.get_all(
            "Custom DocPerm",
            filters={"parent": doctype, "role": role},
            fields=["name"]
        )

        if existing_permissions:
            # Update existing permissions
            for perm in existing_permissions:
                docperm = frappe.get_doc("Custom DocPerm", perm.name)
                docperm.read = 1
                docperm.write = 1
                docperm.create = 1
                docperm.delete = 1
                docperm.save(ignore_permissions=True)
            frappe.msgprint(f"Updated existing permissions for {role} on {doctype}")
        else:
            # Create a new Custom DocPerm entry
            custom_perm = frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": doctype,
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": role,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1
            })
            custom_perm.insert(ignore_permissions=True)
            frappe.msgprint(f"Added new permissions for {role} on {doctype}")

        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error setting permissions for {role} on {doctype}: {e}")
    
    
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
        
def skip_setup_wizard():
    """Automatically skip the setup wizard after install."""
    frappe.db.set_value("System Settings", "System Settings", "setup_complete", 1)
    frappe.db.commit()
    print("Setup wizard skipped!")

def set_default_landing_page():
    """Set the default landing page to /app/main-workspace"""
    frappe.db.set_value("System Settings", "System Settings", "home_page", "/app/main-workspace")
    frappe.db.commit()
    print("Default landing page set to /app/main-workspace")
    
def create_test_users():
    add_test_user("vidya@tech4goodcommunity.com","Vidya","S")
    add_test_user("akansha@tech4goodcommunity.com","Akansha","Negi")
    add_test_user("ajith@tech4goodcommunity.com","Ajith","B M")
    add_test_user("chandru@tech4goodcommunity.com","Chandru","M")    
    add_test_user("praveen@tech4goodcommunity.com","Praveen","K S")    
    add_test_user("tushar@tech4goodcommunity.com","Tushar","B")    


# Insert dummy records for testing
def create_dummy_records():
    insert_dummy_budget_categories()

def insert_dummy_budget_categories():
    dummy_categories = [
        {"category": "Marketing", "description": "Marketing Expenses"},
        {"category": "Operations", "description": "Operational Costs"},
        {"category": "HR", "description": "Human Resources Budget"},
    ]

    for data in dummy_categories:
        if not frappe.db.exists("Category", data["category"]):
            doc = frappe.get_doc({
                "doctype": "Category",
                "category": data["category"],
                "description": data.get("description", ""),
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()    
            print(f"Inserted dummy budget category: {data['category']}")