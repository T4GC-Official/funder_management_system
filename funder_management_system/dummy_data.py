import frappe, json
from datetime import datetime
    
import random

def create_dummy_records():
    try:
        create_test_users()
        Budget_Allocation_Module()
        Donor_Acquisition_Module()
    except Exception as e:
        print(f"Error creating dummy records: {e}")

def Budget_Allocation_Module():
    try:
        insert_dummy_budget_category_and_sub_categories()
        delete_dummy_budget_plan()
        create_dummy_budget_plan()
        submit_budget_plan(1)
        create_dummy_budget_plan_template()
    except Exception as e:
        print(f"Dummy Records Creation Error in Budget Allocation Module: {e}")

def Donor_Acquisition_Module():
    try:
        create_organisation_records()
        generate_leads()
    except Exception as e:
        print(f"Dummy Records Creation Error in Donor Acquisition Module: {e}")

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

# Donor Acquisition Module
def create_organisation_records():
    organisations = [
        {"name": "Tech4Good", "address": "123 Tech Street, Silicon Valley", "contact_email": "info@tech4good.org", "website_url": "https://www.tech4good.org", "pan_card": "AAAAP1234A"},
        {"name": "Green Initiatives", "address": "456 Green Ave, New York", "contact_email": "contact@greeninitiatives.com", "website_url": "https://www.greeninitiatives.com", "pan_card": "ADAAP1234A"},
        {"name": "Health Innovators", "address": "789 Health Blvd, Boston", "contact_email": "support@healthinnovators.org", "website_url": "https://www.healthinnovators.org", "pan_card": "AHEAP1234A"},
        {"name": "Education First", "address": "321 Education Lane, Chicago", "contact_email": "hello@educationfirst.edu", "website_url": "https://www.educationfirst.edu", "pan_card": "DDAAP1235F"},
        {"name": "Food for All", "address": "654 Food Street, Seattle", "contact_email": "info@foodforall.org", "website_url": "https://www.foodforall.org", "pan_card": "FFAAP1234G"},
        {"name": "Water Watch", "address": "987 Water Drive, Miami", "contact_email": "contact@waterwatch.org", "website_url": "https://www.waterwatch.org", "pan_card": "WWWAP1234H"},
        {"name": "Clean Energy", "address": "213 Solar Park, Austin", "contact_email": "support@cleanenergy.org", "website_url": "https://www.cleanenergy.org", "pan_card": "CEAP1234I"},
        {"name": "Animal Welfare", "address": "789 Wildlife Road, Denver", "contact_email": "hello@animalwelfare.org", "website_url": "https://www.animalwelfare.org", "pan_card": "AWAAP1234J"},
        {"name": "Arts Alive", "address": "456 Culture Lane, San Francisco", "contact_email": "info@artsalive.org", "website_url": "https://www.artsalive.org", "pan_card": "AAAAP5678K"},
        {"name": "Tech Education", "address": "123 Innovation Blvd, San Jose", "contact_email": "contact@techeducation.org", "website_url": "https://www.techeducation.org", "pan_card": "TEAP5678L"},
        {"name": "Green Earth", "address": "321 Eco Drive, Portland", "contact_email": "support@greenearth.org", "website_url": "https://www.greenearth.org", "pan_card": "GEAP5678M"},
        {"name": "Community Builders", "address": "654 Unity Ave, Philadelphia", "contact_email": "hello@communitybuilders.org", "website_url": "https://www.communitybuilders.org", "pan_card": "CBAP5678N"},
        {"name": "World Health", "address": "987 Health Street, Houston", "contact_email": "info@worldhealth.org", "website_url": "https://www.worldhealth.org", "pan_card": "WHAP5678O"},
        {"name": "Youth Empowerment", "address": "213 Young Road, Atlanta", "contact_email": "contact@youthempowerment.org", "website_url": "https://www.youthempowerment.org", "pan_card": "YEAP5678P"},
        {"name": "Literacy for All", "address": "789 Knowledge Lane, Phoenix", "contact_email": "support@literacyforall.org", "website_url": "https://www.literacyforall.org", "pan_card": "LFAAP5678Q"},
        {"name": "Disaster Relief", "address": "456 Help Ave, Dallas", "contact_email": "hello@disasterrelief.org", "website_url": "https://www.disasterrelief.org", "pan_card": "DRAP5678R"},
        {"name": "Elder Care", "address": "123 Senior Street, San Diego", "contact_email": "info@eldercare.org", "website_url": "https://www.eldercare.org", "pan_card": "ECAP5678S"},
        {"name": "Wildlife Conservation", "address": "321 Nature Blvd, Orlando", "contact_email": "contact@wildlifeconservation.org", "website_url": "https://www.wildlifeconservation.org", "pan_card": "WCAP5678T"},
        {"name": "Women's Rights", "address": "654 Equality Ave, Minneapolis", "contact_email": "support@womensrights.org", "website_url": "https://www.womensrights.org", "pan_card": "WRAP5678U"},
        {"name": "Mental Health Support", "address": "987 Wellness Drive, Nashville", "contact_email": "hello@mentalhealthsupport.org", "website_url": "https://www.mentalhealthsupport.org", "pan_card": "MHSP5678V"}
    ]

    for org in organisations:
        if not frappe.db.exists("Organisation Details", {"organisation_name": org["name"]}):
            doc = frappe.get_doc({
                "doctype": "Organisation Details",
                "organisation_name": org["name"],
                "website_url": org["website_url"],
                "official_address": org["address"],
                "pan_card": org["pan_card"],
                "official_email_id": org["contact_email"]
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Inserted organisation record: {org['name']}")

def generate_leads():
    organisations = frappe.get_all("Organisation Details", fields=["name", "organisation_name", "website_url", "official_email_id", "pan_card"])
    lead_stages = ["New Lead","Warm Lead", "Hot Lead", "Cold Lead", "Dropped Lead"]
    category = [item.name for item in frappe.get_all("Category", fields=["name"])]
    financial_year = [item.name for item in frappe.get_all("Financial Year", fields=["name"])]
    for org in organisations:
        org["financial_year"]= random.choice(financial_year)
        org["lead_category"] = random.choice(category)
        org["lead_stage"] = random.choice(lead_stages)
    for org in organisations:
        if not frappe.db.exists("Organisation Lead", {"lead_name": org["organisation_name"]}):
            lead_doc = frappe.get_doc({
                "doctype": "Organisation Lead",
                "lead_name": org["organisation_name"],
                "website_url": org["website_url"],
                "official_email": org["official_email_id"],
                "pan_card": org["pan_card"],
                "lead_stage":  org["lead_stage"],
                "organisation_id": org["name"],
                "lead_category": org["lead_category"],
                "financial_year_of_reachout": org["financial_year"],
            })
            lead_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Inserted lead record: {org['organisation_name']}")
