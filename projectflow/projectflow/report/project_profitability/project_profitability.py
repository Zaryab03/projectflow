import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Project"), "fieldname": "name", "fieldtype": "Link", "options": "Project", "width": 150},
		{"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 180},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
		{"label": _("Total Billed"), "fieldname": "total_billed_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Total Costing"), "fieldname": "total_costing_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Gross Margin"), "fieldname": "gross_margin", "fieldtype": "Currency", "width": 120},
		{"label": _("Gross Margin %"), "fieldname": "per_gross_margin", "fieldtype": "Percent", "width": 120},
		{"label": _("Client Satisfaction"), "fieldname": "custom_client_satisfaction", "fieldtype": "Rating", "width": 130},
	]


def get_data(filters):
	project_filters = {}
	if filters.get("project"):
		project_filters["name"] = filters.get("project")
	if filters.get("status"):
		project_filters["status"] = filters.get("status")

	return frappe.get_all(
		"Project",
		filters=project_filters,
		fields=[
			"name",
			"project_name",
			"status",
			"total_billed_amount",
			"total_costing_amount",
			"gross_margin",
			"per_gross_margin",
			"custom_client_satisfaction",
		],
		order_by="gross_margin desc",
	)


def get_chart_data(data):
	if not data:
		return None

	rows = [d for d in data if flt(d.get("total_billed_amount")) or flt(d.get("total_costing_amount"))]
	if not rows:
		return None

	return {
		"data": {
			"labels": [d["project_name"] for d in rows],
			"datasets": [
				{"name": _("Total Billed"), "values": [flt(d["total_billed_amount"]) for d in rows]},
				{"name": _("Total Costing"), "values": [flt(d["total_costing_amount"]) for d in rows]},
			],
		},
		"type": "bar",
		"colors": ["#28a745", "#e24c4c"],
	}
