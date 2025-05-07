app_name = "funder_management_system"
app_title = "Funder Management System"
app_publisher = "Tech4Good Community"
app_description = "FMS"
app_email = "hello@tech4goodcommunity.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "funder_management_system",
# 		"logo": "/assets/funder_management_system/logo.png",
# 		"title": "Funder Management System",
# 		"route": "/funder_management_system",
# 		"has_permission": "funder_management_system.api.permission.has_app_permission"
# 	}
# ]

fixtures = [{
    "dt": "Thematic Area"
},
{
    "dt": "Category"
},
{
    "dt": "Source of Connection"
},
{
    "dt": "Compliance Checklist"
},
{
	"dt": "Engagement Checklist Master"
}]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_js = "/assets/funder_management_system/js/custom_toolbar.js"

# app_include_css = "/assets/funder_management_system/css/funder_management_system.css"
# app_include_js = "/assets/funder_management_system/js/funder_management_system.js"

# include js, css files in header of web template
# web_include_css = "/assets/funder_management_system/css/funder_management_system.css"
# web_include_js = "/assets/funder_management_system/js/funder_management_system.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "funder_management_system/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_list_js = {"Expense Item": "public/js/expense_item_list.js"}
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "funder_management_system/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "funder_management_system.utils.jinja_methods",
# 	"filters": "funder_management_system.utils.jinja_filters"
# }

# Installation
# ------------

#before_install = ["funder_management_system.utils.enable_developer_mode"]
after_install = [
    "funder_management_system.utils.create_financial_year",
    "funder_management_system.utils.setup_website_customizations"
    ]
after_migrate = [
    "funder_management_system.utils.set_currency_permission_using_custom",
    "funder_management_system.utils.enable_permission_for_fms_roles",
    "funder_management_system.utils.share_custom_number_cards_with_everyone",
    "funder_management_system.utils.setup_website_customizations"
    ]
# Uninstallation
# ------------

# before_uninstall = "funder_management_system.uninstall.before_uninstall"
# after_uninstall = "funder_management_system.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "funder_management_system.utils.before_app_install"
# after_app_install = "funder_management_system.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "funder_management_system.utils.before_app_uninstall"
# after_app_uninstall = "funder_management_system.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "funder_management_system.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#     "Expense Item": "funder_management_system.utils.has_permission"
# }
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    "User": {
        "after_insert":"funder_management_system.utils.set_default_workspace"}
}


# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

#to-do change the all to daily for funder_management_system.task.daily.grant_agreement_daily

scheduler_events = {
	"all": [
	 	"funder_management_system.task.daily.grant_agreement_daily",
   		"funder_management_system.task.daily.organisation_toolkit_daily"
	 ],
	"daily": [
		"funder_management_system.task.daily.donor_daily",
	]}
# 	"hourly": [
# 		"funder_management_system.tasks.hourly"
# 	],
# 	"weekly": [
# 		"funder_management_system.tasks.weekly"
# 	],
# 	"monthly": [
# 		"funder_management_system.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "funder_management_system.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "funder_management_system.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "funder_management_system.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["funder_management_system.utils.before_request"]
# after_request = ["funder_management_system.utils.after_request"]

# Job Events
# ----------
# before_job = ["funder_management_system.utils.before_job"]
# after_job = ["funder_management_system.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"funder_management_system.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

