import math
import frappe, json
from datetime import datetime, timedelta
    
import random

def create_dummy_records():
    try:
        create_test_users()
        Budget_Allocation_Module()
        Donor_Acquisition_Module()
        Donor_Engagement_Module()
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
        
def Donor_Engagement_Module():
    try:
        delete_grant_agreements()
        create_grant_agreement()
        calculate_grant_agreement_tranche_progress()
    except Exception as e:
        print(f"Dummy Records Creation Error in Donor Acquisition Module: {e}")

def Donor_Acquisition_Module():
    try:
        create_organisation_records()
        generate_leads()
        change_lead_stage_and_create_donor()
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
    add_test_user("akanksha@tech4goodcommunity.com","Akanksha","Negi")
    add_test_user("ajith@tech4goodcommunity.com","Ajith","B M")
    add_test_user("chandru@tech4goodcommunity.com","Chandru","M")    
    add_test_user("praveen@tech4goodcommunity.com","Praveen","K S")    
    add_test_user("tushar@tech4goodcommunity.com","Tushar","B")    
    add_test_user("rinju@tech4goodcommunity.com","Rinju","R")
    add_test_user("akhila@tech4goodcommunity.com","Akhila","Amma")
    add_test_user("anusha@tech4goodcommunity.com","Anusha","M B")
    add_test_user("prashant@tech4goodcommunity.com","Prashant","Bala")
    add_test_user("hazel@tech4goodcommunity.com","Hazel","Ronaldo")
    add_test_user("varshini@tech4goodcommunity.com","Varshini","S")

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
            print(f"Created dummy record for budget category and sub-category: {data['budget_category']} - {data['budget_sub_category']}")


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
            {"category": "IT","sub_category": "Cybersecurity"},
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
            print(f"Dummy Budget Plan {budget_plan.name} created successfully!")

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
    print("Creating Organisation records...")
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
            print(f"Created Dummy Organisation record: {org['name']}")

def generate_leads():
    print("Generating leads...")
    organisations = frappe.get_all("Organisation Details", fields=["name", "organisation_name", "website_url", "official_email_id", "pan_card"])
    lead_stages = ["New Lead", "Warm Lead", "Hot Lead", "Cold Lead", "Dropped Lead"]
    categories = frappe.get_all("Category", fields=["category"])
    financial_years = frappe.get_all("Financial Year", fields=["name"])

    if not categories:
        print("Categories are missing.")
        return

    if not financial_years:
        print("Financial Years are missing.")
        return

    for org in organisations:
        org["financial_year"] = random.choice(financial_years)["name"]
        org["lead_category"] = random.choice(categories)["category"]

    for i, org in enumerate(organisations):
        org["lead_stage"] = "Hot Lead" if i == 0 else random.choice(lead_stages)

    for org in organisations:
        if not frappe.db.exists("Organisation Lead", {"lead_name": org["organisation_name"]}):
            lead_doc = frappe.get_doc({
                "doctype": "Organisation Lead",
                "lead_name": org["organisation_name"],
                "website_url": org["website_url"],
                "official_email": org["official_email_id"],
                "pan_card": org["pan_card"],
                "lead_stage": org["lead_stage"],
                "organisation_id": org["name"],
                "lead_category": org["lead_category"],
                "financial_year_of_reachout": org["financial_year"],
            })
            lead_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Created Dummy lead record: {org['organisation_name']}")
        else:
            print(f"Dummy Lead record already exists: {org['organisation_name']}, skipping...")

def change_lead_stage_and_create_donor(stage="Confirmed Lead"):
    print(f"Changing lead stage to {stage}...")
    leads = frappe.get_all("Organisation Lead", filters={"lead_stage": "Hot Lead"}, fields=["name"], limit=1)
    if not leads:
        print("No leads found with stage 'Hot Lead'")
        return
    for lead in leads:
        lead_doc = frappe.get_doc("Organisation Lead", lead["name"])
        lead_doc.lead_stage = stage
        lead_doc.save()
        frappe.db.commit()
        print(f"Updated lead stage to {stage} for lead: {lead['name']}")

        # Create donor record
        if not frappe.db.exists("Donor", {"lead_name": lead["name"]}):
            donor_doc = frappe.get_doc({
                "doctype": "Donor",
                "lead_name": lead["name"],
                "donor_name": lead_doc.lead_name,
            })
            donor_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Created donor record from lead: {lead['name']}")
        else:
            print(f"Donor record already exists for lead: {lead['name']}")

def create_grant_agreement():
    donors = frappe.get_all("Donor", fields=["name", "lead_name", "donor_name"])
    donors = frappe.get_all("Donor", fields=["name", "lead_name", "donor_name"])
    if not donors:
        print("No donors found. failed to create grant agreements and tranches.")
        return

    for donor in donors:
        if not frappe.db.exists("Grant Agreement", {"donor": donor["name"]}):
            amount = random.randint(9000, 140000)
            grant_agreement_doc = frappe.get_doc({
                "doctype": "Grant Agreement",
                "donor": donor["name"],
                "donor_name": donor["donor_name"],
                "lead_name": donor["lead_name"],
                "grant_name": "Grant for " + "Climate Change",
                "total_number_of_tranches": random.randint(1, 10),
                "grant_name": donor["name"]+" | Grant for " + random.choice(["Climate Change", "Education", "Healthcare", "Women Empowerment", "Children Welfare", "Disaster Response", "Community Development", "Animal Welfare", "Environmental Conservation", "Other"]),
                "total_grant_amount": amount,
                "grant_agreement_start_date": "2020-01-01",
                "grant_agreement_end_date": "2020-12-31",
            })
            # add data in tranche table for each tranche
            for i in range(grant_agreement_doc.total_number_of_tranches):
                due_date = random_date(grant_agreement_doc.grant_agreement_start_date, grant_agreement_doc.grant_agreement_end_date)
                tranche_status = random.choice(["Pending - On Time","Pending - Delayed","Received - On Time","Received - Delayed"])
                tranche_doc = frappe.get_doc({
                    "doctype": "Tranche Details",
                    "grant_agreement": grant_agreement_doc.name,
                    "tranche_name": "Tranche " + str(i+1),
                    "tranche_amount": math.floor(amount / grant_agreement_doc.total_number_of_tranches),
                    "due_date": due_date,
                    "tranche_status": tranche_status,
                    "tranche_financial_year": get_financial_year_for_due_date(due_date),
                    "mode_of_payment": random.choice(["Cheque", "UPI", "Netbanking"]),
                    # if tranche status is "Received - On Time" or "Received - Delayed", then received on date will be due date other wise it will be null
                    "received_on": add_days_to_date(due_date,3) if tranche_status == "Received - Delayed" else (due_date if tranche_status == "Received - On Time" else None),
                })
                grant_agreement_doc.append("tranche_table", tranche_doc)
                    
            grant_agreement_doc.save()
            frappe.db.commit()
            print(f"Created grant agreement for donor: {donor['name']}")
        else:
            print(f"Grant agreement already exists for donor: {donor['name']}")
            

def delete_grant_agreements():
    donors = frappe.get_all("Donor", fields=["name"])
    if not donors:
        print("No donors found. Can't delete grant agreements.")
        return
    for donor in donors:
        grant_agreements = frappe.get_all("Grant Agreement", filters={"donor": donor["name"]}, fields=["name"])
        for grant_agreement in grant_agreements:
            frappe.delete_doc("Grant Agreement", grant_agreement["name"], force=True)
            frappe.db.commit()
            print(f"Deleted grant agreement for donor: {donor['name']}")
def random_date(start_date, end_date):
    """Get a random date between start_date and end_date"""
    start_timestamp = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
    end_timestamp = datetime.strptime(end_date, "%Y-%m-%d").timestamp()
    random_timestamp = random.uniform(start_timestamp, end_timestamp)
    return datetime.fromtimestamp(random_timestamp).strftime("%Y-%m-%d")

def get_financial_year_for_due_date(due_date):
    due_date_year = datetime.strptime(due_date, "%Y-%m-%d").year
    # the format of the financial year will be 2023-24
    financial_year_start = due_date_year
    financial_year_end = due_date_year + 1
    financial_year = str(financial_year_start) + "-" + str(financial_year_end)[2:]
    return financial_year
    
def add_days_to_date(date_str, days):
    print("Due Date: ", date_str, "Days: ", days)
    date_format = "%Y-%m-%d"
    date_obj = datetime.strptime(date_str, date_format)
    new_date_obj = date_obj + timedelta(days=days)
    return new_date_obj.strftime(date_format)    


def calculate_grant_agreement_tranche_progress():
    grant_agreements = frappe.get_all("Grant Agreement", fields=["name"])
    for grant_agreement in grant_agreements:
        total_tranche_progress = 0
        grant_agreement_doc = frappe.get_doc("Grant Agreement", grant_agreement["name"])
        for tranche in grant_agreement_doc.tranche_table:
            if tranche.tranche_status in  ["Received - Delayed","Received - On Time"]:
                total_tranche_progress +=1
        grant_agreement_doc.total_tranche_progress_percentage = math.floor((total_tranche_progress/grant_agreement_doc.total_number_of_tranches)*100)
        grant_agreement_doc.total_tranche_progress = str(total_tranche_progress)+"/"+str(grant_agreement_doc.total_number_of_tranches)
        grant_agreement_doc.total_tranche_amount_received = grant_agreement_doc.total_grant_amount * grant_agreement_doc.total_tranche_progress_percentage/100
        grant_agreement_doc.save()
        frappe.db.commit()
        print(f"Calculated progress for grant agreement: {grant_agreement['name']}")
        total_tranche_progress = 0
