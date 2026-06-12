import frappe
from frappe import _
from frappe.utils import date_diff


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()

	if not filters.get("sprint"):
		return columns, [], None, None

	data = get_data(filters)
	chart = get_chart_data(filters, data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
		{"label": _("Total Points"), "fieldname": "total_points", "fieldtype": "Float", "width": 110},
		{"label": _("Completed Points"), "fieldname": "completed_points", "fieldtype": "Float", "width": 130},
		{"label": _("Remaining Points"), "fieldname": "remaining_points", "fieldtype": "Float", "width": 130},
		{"label": _("Ideal Remaining"), "fieldname": "ideal_remaining", "fieldtype": "Float", "width": 130},
	]


def get_data(filters):
	logs = frappe.get_all(
		"Sprint Burndown Log",
		filters={"sprint": filters.get("sprint")},
		fields=["date", "total_points", "completed_points", "remaining_points"],
		order_by="date asc",
	)

	sprint = frappe.db.get_value(
		"Agile Sprint", filters.get("sprint"), ["start_date", "end_date"], as_dict=True
	)

	if sprint and sprint.start_date and sprint.end_date:
		total_days = max(1, date_diff(sprint.end_date, sprint.start_date))
		starting_points = logs[0].total_points if logs else 0

		for row in logs:
			elapsed = date_diff(row.date, sprint.start_date)
			ideal = starting_points * (1 - (elapsed / total_days))
			row["ideal_remaining"] = max(0, round(ideal, 2))

	return logs


def get_chart_data(filters, data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d["date"].strftime("%Y-%m-%d") if hasattr(d["date"], "strftime") else d["date"] for d in data],
			"datasets": [
				{"name": _("Remaining Points"), "values": [d.get("remaining_points") for d in data]},
				{"name": _("Ideal Burndown"), "values": [d.get("ideal_remaining") for d in data]},
			],
		},
		"type": "line",
		"colors": ["#ff5858", "#a4a4a4"],
	}
