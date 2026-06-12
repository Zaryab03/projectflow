import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()

	if not filters.get("project"):
		return columns, [], None, None

	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Task"), "fieldname": "name", "fieldtype": "Link", "options": "Task", "width": 120},
		{"label": _("Subject"), "fieldname": "subject", "fieldtype": "Data", "width": 220},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Start Date"), "fieldname": "exp_start_date", "fieldtype": "Date", "width": 100},
		{"label": _("End Date"), "fieldname": "exp_end_date", "fieldtype": "Date", "width": 100},
		{"label": _("Slack (Days)"), "fieldname": "custom_total_slack", "fieldtype": "Float", "width": 100},
		{"label": _("Critical"), "fieldname": "custom_is_critical", "fieldtype": "Check", "width": 80},
	]


def get_data(filters):
	return frappe.get_all(
		"Task",
		filters={"project": filters.get("project"), "is_group": 0},
		fields=[
			"name",
			"subject",
			"status",
			"exp_start_date",
			"exp_end_date",
			"custom_total_slack",
			"custom_is_critical",
		],
		order_by="exp_start_date asc",
	)


def get_chart_data(data):
	rows = [d for d in data if d.exp_start_date and d.exp_end_date]
	if not rows:
		return None

	return {
		"data": {
			"labels": [d.subject for d in rows],
			"datasets": [
				{"name": _("Slack (Days)"), "values": [d.custom_total_slack or 0 for d in rows]},
			],
		},
		"type": "bar",
		"colors": ["#ff5858"],
	}
