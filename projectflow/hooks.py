app_name = "projectflow"
app_title = "ProjectFlow"
app_publisher = "ProjectFlow"
app_description = "Advanced Project Management platform for Frappe and ERPNext"
app_email = "tafheem.alam.professional@gmail.com"
app_license = "mit"

# Fixtures
# --------

fixtures = [
	{"dt": "Custom Field", "filters": [["dt", "in", ["Project", "Task", "Task Depends On", "Employee", "Issue"]]]},
	{"dt": "Kanban Board", "filters": [["reference_doctype", "in", ["Task", "Issue"]]]},
	{"dt": "Issue Type"},
	{"dt": "Issue Priority", "filters": [["name", "=", "Critical"]]},
	{"dt": "Workflow State", "filters": [["name", "in", ["Planned", "Confirmed", "Completed"]]]},
	{"dt": "Workflow Action Master", "filters": [["name", "in", ["Confirm", "Complete", "Reopen"]]]},
	{"dt": "Workflow", "filters": [["name", "=", "Resource Allocation Approval"]]},
	{"dt": "Notification", "filters": [["name", "=", "Project Risk Escalation"]]},
]

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "projectflow",
# 		"logo": "/assets/projectflow/logo.png",
# 		"title": "ProjectFlow",
# 		"route": "/projectflow",
# 		"has_permission": "projectflow.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/projectflow/css/projectflow.css"
# app_include_js = "/assets/projectflow/js/projectflow.js"

# include js, css files in header of web template
# web_include_css = "/assets/projectflow/css/projectflow.css"
# web_include_js = "/assets/projectflow/js/projectflow.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "projectflow/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {"Task": "public/js/task_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "projectflow/public/icons.svg"

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
# 	"methods": "projectflow.utils.jinja_methods",
# 	"filters": "projectflow.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "projectflow.install.before_install"
# after_install = "projectflow.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "projectflow.uninstall.before_uninstall"
# after_uninstall = "projectflow.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "projectflow.utils.before_app_install"
# after_app_install = "projectflow.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "projectflow.utils.before_app_uninstall"
# after_app_uninstall = "projectflow.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "projectflow.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
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
	"Task": {
		"validate": "projectflow.projectflow.events.task.validate",
		"on_update": "projectflow.projectflow.events.task.on_update",
		"on_trash": "projectflow.projectflow.events.task.on_trash",
	},
	"Issue": {
		"validate": "projectflow.projectflow.events.issue.validate",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"projectflow.projectflow.events.project.recalculate_all_scores",
		"projectflow.projectflow.events.critical_path.recalculate_all_critical_paths",
		"projectflow.projectflow.events.sprint.log_burndown_for_active_sprints",
	],
}

# Testing
# -------

# before_tests = "projectflow.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "projectflow.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "projectflow.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["projectflow.utils.before_request"]
# after_request = ["projectflow.utils.after_request"]

# Job Events
# ----------
# before_job = ["projectflow.utils.before_job"]
# after_job = ["projectflow.utils.after_job"]

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
# 	"projectflow.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

