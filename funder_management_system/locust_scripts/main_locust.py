from locust import HttpUser, TaskSet, task, between
import csv
import json
import random
from itertools import cycle

# List of all doctypes to test
DOCTYPES = [
    "Expense Item",
    "Utilisation Record",
    "Engagement Checklist Master",
    "Document List",
    "Grant Agreement",
    "Donor",
    "Preferred Means of Communication",
    "Organisation Lead",
    "Compliance Checklist",
    "Source of Connection",
    "Category",
    "Thematic Area",
    "Designation",
    "Organisation POC",
    "Organisation Details",
    "Budget Plan",
    "Budget Plan Template",
    "Budget Sub-Category",
    "Budget Category",
    "Financial Year"
]

# Mapping from Doctype to Module
DOCTYPE_MODULE_MAP = {
    "Expense Item": "Utilisation Module",
    "Utilisation Record": "Utilisation Module",
    "Engagement Checklist Master": "Engagement Module",
    "Document List": "Organisation Tools",
    "Grant Agreement": "Engagement Module",
    "Donor": "Engagement Module",
    "Preferred Means of Communication": "Funder Management System",
    "Organisation Lead": "Donor Acquisition Management",
    "Compliance Checklist": "Funder Management System",
    "Source of Connection": "Funder Management System",
    "Category": "Funder Management System",
    "Thematic Area": "Funder Management System",
    "Designation": "Funder Management System",
    "Organisation POC": "Funder Management System",
    "Organisation Details": "Funder Management System",
    "Budget Plan": "Budget Planning",
    "Budget Plan Template": "Budget Planning",
    "Budget Sub-Category": "Budget Planning",
    "Budget Category": "Budget Planning",
    "Financial Year": "Funder Management System"
}

# List of custom API endpoints to test (all GET)
CUSTOM_API_ENDPOINTS = [
    ("GET", "/api/method/funder_management_system.number_card_util.get_total_leads_by_finanacial_year", "Total Leads by Financial Year"),
    ("GET", "/api/method/funder_management_system.number_card_util.get_conversion_rate_by_fy", "Conversion Rate by FY"),
    ("GET", "/api/method/funder_management_system.number_card_util.get_churn_rate_fy", "Churn Rate by FY"),
    ("GET", "/api/method/funder_management_system.number_card_util.get_total_funds_received_current_fy", "Total Funds Received Current FY"),
    ("GET", "/api/method/funder_management_system.number_card_util.get_total_expenditure_current_fy", "Total Expenditure Current FY"),
    ("GET", "/api/method/funder_management_system.number_card_util.get_total_active_donors_current_fy", "Total Active Donors Current FY"),
    ("GET", "/api/method/funder_management_system.number_card_util.get_total_active_grant_agreements_current_fy", "Total Active Grant Agreements Current FY"),
    ("GET", "/api/method/funder_management_system.utils.get_current_financial_year", "Get Current Financial Year"),
    ("GET", "/api/method/funder_management_system.donor_acquisition_management.page.donor_acquisition_dashboard.donor_acquisition_dashboard.get_number_cards", "Get Number Cards"),
    ("GET", "/api/method/funder_management_system.donor_acquisition_management.page.donor_acquisition_dashboard.donor_acquisition_dashboard.get_total_leads", "Get Total Leads"),
    ("GET", "/api/method/funder_management_system.donor_acquisition_management.page.donor_acquisition_dashboard.donor_acquisition_dashboard.get_conversion_rate_by_fy", "Get Conversion Rate by FY (Dashboard)"),
    ("GET", "/api/method/funder_management_system.donor_acquisition_management.page.donor_acquisition_dashboard.donor_acquisition_dashboard.get_leads_by_category", "Get Leads by Category"),
    ("GET", "/api/method/funder_management_system.donor_acquisition_management.page.donor_acquisition_dashboard.donor_acquisition_dashboard.get_leads_by_lead_stages", "Get Leads by Lead Stages"),
    ("GET", "/api/method/funder_management_system.donor_acquisition_management.page.donor_acquisition_dashboard.donor_acquisition_dashboard.get_leads_by_thematic_area", "Get Leads by Thematic Area"),
    ("GET", "/api/method/funder_management_system.donor_acquisition_management.page.donor_acquisition_dashboard.donor_acquisition_dashboard.get_leads_by_sources_of_connection", "Get Leads by Sources of Connection"),
]

# Load users from CSV
with open("users.csv") as f:
    reader = csv.DictReader(f)
    users = list(reader)
    user_pool = cycle(users)

class FrappeAPITestBehavior(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        self.credentials = next(user_pool)
        with self.client.post("/api/method/login", data=self.credentials, catch_response=True) as response:
            try:
                result = response.json()
                if response.status_code == 200 and result.get("message") == "Logged In":
                    response.success()
                else:
                    response.failure(f"Login failed for {self.credentials['usr']} - {response.status_code}")
            except Exception:
                response.failure(f"Login failed for {self.credentials['usr']} - Invalid JSON")

    def generate_test_data(self, doctype):
        test_data = {
            "Expense Item": {
                "item_name": f"Test Expense {random.randint(1000, 9999)}",
                "description": "Test expense item created by Locust"
            },
            "Category": {
                "category_name": f"Test Category {random.randint(1000, 9999)}",
                "description": "Test category created by Locust"
            },
            "Designation": {
                "designation_name": f"Test Designation {random.randint(1000, 9999)}"
            },
            "Financial Year": {
                "year": f"Test FY {random.randint(2025, 2030)}",
                "year_start_date": "2025-04-01",
                "year_end_date": "2026-03-31"
            }
        }
        return test_data.get(doctype, {"name": f"Test {doctype} {random.randint(1000, 9999)}"})

    def run_for_all_doctypes(self, method):
        for doctype in DOCTYPES:
            safe_doctype = doctype.replace(" ", "%20")
            module_name = DOCTYPE_MODULE_MAP.get(doctype, "Unknown Module")
            if method == "get_list":
                self.client.get(
                    f"/api/resource/{safe_doctype}",
                    name=f"GET [{module_name}] /api/resource/{doctype}"
                )
            elif method == "get_specific":
                get_response = self.client.get(f"/api/resource/{safe_doctype}?limit_page_length=1")
                if get_response.status_code == 200:
                    try:
                        data = get_response.json()
                        if data.get("data") and len(data["data"]) > 0:
                            record_name = data["data"][0]["name"]
                            self.client.get(
                                f"/api/resource/{safe_doctype}/{record_name}",
                                name=f"GET [{module_name}] /api/resource/{doctype} (specific)"
                            )
                    except Exception:
                        pass
            elif method == "post":
                data = self.generate_test_data(doctype)
                with self.client.post(
                    f"/api/resource/{safe_doctype}",
                    json={"data": data},
                    headers={"Content-Type": "application/json"},
                    catch_response=True,
                    name=f"POST [{module_name}] /api/resource/{doctype}"
                ) as response:
                    if response.status_code in [200, 201]:
                        response.success()
                    else:
                        response.failure(f"POST failed: {response.status_code} - {response.text}")
            elif method == "put":
                get_response = self.client.get(f"/api/resource/{safe_doctype}?limit_page_length=1")
                if get_response.status_code == 200:
                    try:
                        data = get_response.json()
                        if data.get("data") and len(data["data"]) > 0:
                            record_name = data["data"][0]["name"]
                            update_data = {"description": f"Updated by Locust at {random.randint(1000, 9999)}"}
                            with self.client.put(
                                f"/api/resource/{safe_doctype}/{record_name}",
                                json={"data": update_data},
                                headers={"Content-Type": "application/json"},
                                catch_response=True,
                                name=f"PUT [{module_name}] /api/resource/{doctype}"
                            ) as response:
                                if response.status_code in [200, 201]:
                                    response.success()
                                else:
                                    response.failure(f"PUT failed: {response.status_code} - {response.text}")
                    except Exception:
                        pass

    def run_custom_api_endpoints(self):
        for method, endpoint, desc in CUSTOM_API_ENDPOINTS:
            # All are GET now
            self.client.get(endpoint, name=f"GET [Custom] {desc}")

    @task(2)
    def test_get_all_doctypes(self):
        self.run_for_all_doctypes("get_list")

    @task(2)
    def test_get_specific_all_doctypes(self):
        self.run_for_all_doctypes("get_specific")

   #  @task(1)
   #  def test_post_all_doctypes(self):
   #      self.run_for_all_doctypes("post")

    @task(1)
    def test_put_all_doctypes(self):
         self.run_for_all_doctypes("put")

    @task(3)
    def test_custom_api_endpoints(self):
        self.run_custom_api_endpoints()

class FrappeAPITestUser(HttpUser):
    tasks = [FrappeAPITestBehavior]
    wait_time = between(1, 3)
