import frappe
from frappe import _

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]


def execute(filters=None):
	filters = frappe._dict(filters or {})

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Issue"), "fieldname": "name", "fieldtype": "Link", "options": "Issue", "width": 100},
		{"label": _("Subject"), "fieldname": "subject", "fieldtype": "Data", "width": 220},
		{"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
		{"label": _("Task"), "fieldname": "custom_task", "fieldtype": "Link", "options": "Task", "width": 120},
		{"label": _("Issue Type"), "fieldname": "issue_type", "fieldtype": "Link", "options": "Issue Type", "width": 120},
		{"label": _("Severity"), "fieldname": "custom_severity", "fieldtype": "Data", "width": 90},
		{"label": _("Priority"), "fieldname": "priority", "fieldtype": "Link", "options": "Issue Priority", "width": 90},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
		{"label": _("Opening Date"), "fieldname": "opening_date", "fieldtype": "Date", "width": 100},
	]


def get_data(filters):
	issue_filters = {}
	if filters.get("project"):
		issue_filters["project"] = filters.get("project")
	if filters.get("severity"):
		issue_filters["custom_severity"] = filters.get("severity")
	if filters.get("status"):
		issue_filters["status"] = filters.get("status")

	return frappe.get_all(
		"Issue",
		filters=issue_filters,
		fields=[
			"name",
			"subject",
			"project",
			"custom_task",
			"issue_type",
			"custom_severity",
			"priority",
			"status",
			"opening_date",
		],
		order_by="opening_date desc",
	)


def get_chart_data(data):
	if not data:
		return None

	by_severity = {severity: 0 for severity in SEVERITY_ORDER}
	for row in data:
		severity = row.get("custom_severity") or "Medium"
		by_severity[severity] = by_severity.get(severity, 0) + 1

	return {
		"data": {
			"labels": SEVERITY_ORDER,
			"datasets": [{"name": _("Open Issues"), "values": [by_severity.get(s, 0) for s in SEVERITY_ORDER]}],
		},
		"type": "bar",
		"colors": ["#e24c4c"],
	}
