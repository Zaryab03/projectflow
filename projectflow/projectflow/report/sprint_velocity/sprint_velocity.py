import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Sprint"), "fieldname": "name", "fieldtype": "Link", "options": "Agile Sprint", "width": 150},
		{"label": _("Sprint Name"), "fieldname": "sprint_name", "fieldtype": "Data", "width": 180},
		{"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
		{"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 100},
		{"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date", "width": 100},
		{"label": _("Committed Points"), "fieldname": "committed_points", "fieldtype": "Float", "width": 130},
		{"label": _("Completed Points"), "fieldname": "completed_points", "fieldtype": "Float", "width": 130},
		{"label": _("Velocity %"), "fieldname": "velocity", "fieldtype": "Percent", "width": 100},
	]


def get_data(filters):
	sprint_filters = {}
	if filters.get("project"):
		sprint_filters["project"] = filters.get("project")
	if filters.get("status"):
		sprint_filters["status"] = filters.get("status")

	sprints = frappe.get_all(
		"Agile Sprint",
		filters=sprint_filters,
		fields=["name", "sprint_name", "project", "status", "start_date", "end_date"],
		order_by="start_date asc",
	)

	for sprint in sprints:
		tasks = frappe.get_all(
			"Task",
			filters={"custom_sprint": sprint.name, "is_group": 0},
			fields=["status", "custom_story_points"],
		)
		committed = sum(t.custom_story_points or 0 for t in tasks)
		completed = sum(t.custom_story_points or 0 for t in tasks if t.status == "Completed")

		sprint["committed_points"] = committed
		sprint["completed_points"] = completed
		sprint["velocity"] = (completed / committed * 100) if committed else 0

	return sprints


def get_chart_data(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d["sprint_name"] for d in data],
			"datasets": [
				{"name": _("Committed Points"), "values": [d["committed_points"] for d in data]},
				{"name": _("Completed Points"), "values": [d["completed_points"] for d in data]},
			],
		},
		"type": "bar",
		"colors": ["#a4a4a4", "#28a745"],
	}
