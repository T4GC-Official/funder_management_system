from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.exceptions import ValidationError
import frappe

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]

class UnitTestBudgetPlan(UnitTestCase):
    """
    Unit tests for BudgetPlan.
    Use this class for testing individual functions and methods.
    """
    
    def setUp(self):
        self.budget_plan = frappe.get_doc({
            "doctype": "Budget Plan",
            "financial_year": "2025",
            "currency": "USD"
        })
    
    def test_required_fields(self):
        """Test that required fields must be present"""
        self.budget_plan.financial_year = None
        with self.assertRaises(ValidationError):
            self.budget_plan.insert()
    
    def test_currency_field(self):
        """Test that the currency field must be valid"""
        self.budget_plan.currency = "INVALID_CURRENCY"
        with self.assertRaises(ValidationError):
            self.budget_plan.insert()
    
    def test_yearly_budget_non_negative(self):
        """Test that yearly budget values must be non-negative"""
        self.budget_plan.yearly_budget = -5000
        with self.assertRaises(ValidationError):
            self.budget_plan.insert()

    def test_amended_from_read_only(self):
        """Test that 'amended_from' field is read-only"""
        self.budget_plan.amended_from = "Some Value"
        with self.assertRaises(ValidationError):
            self.budget_plan.save()

class IntegrationTestBudgetPlan(IntegrationTestCase):
    """
    Integration tests for BudgetPlan.
    Use this class for testing interactions between multiple components.
    """
    
    def test_create_budget_plan(self):
        """Test creating a Budget Plan"""
        budget_plan = frappe.get_doc({
            "doctype": "Budget Plan",
            "financial_year": "2025-26",
            "currency": "USD"
        })
        budget_plan.insert()
        self.assertIsNotNone(budget_plan.name)
    
    def test_budget_plan_submission(self):
        """Test submitting a Budget Plan"""
        budget_plan = frappe.get_doc({
            "doctype": "Budget Plan",
            "financial_year": "2025-26",
            "currency": "USD"
        })
        budget_plan.insert()
        budget_plan.submit()
        self.assertEqual(budget_plan.docstatus, 1)
    
    def test_budget_plan_deletion(self):
        """Test deleting a Budget Plan"""
        budget_plan = frappe.get_doc({
            "doctype": "Budget Plan",
            "financial_year": "2025-26",
            "currency": "USD"
        })
        budget_plan.insert()
        budget_plan.delete()
        self.assertIsNone(frappe.get_value("Budget Plan", budget_plan.name, "name"))
