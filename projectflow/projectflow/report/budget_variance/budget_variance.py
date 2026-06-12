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
		{"label": _("Estimated Cost"), "fieldname": "estimated_costing", "fieldtype": "Currency", "width": 130},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Variance"), "fieldname": "variance", "fieldtype": "Currency", "width": 130},
		{"label": _("Variance %"), "fieldname": "variance_pct", "fieldtype": "Percent", "width": 110},
		{"label": _("Budget Utilization %"), "fieldname": "custom_budget_utilization", "fieldtype": "Percent", "width": 140},
		{"label": _("Over Budget"), "fieldname": "over_budget", "fieldtype": "Check", "width": 100},
	]


def get_data(filters):
	project_filters = {}
	if filters.get("project"):
		project_filters["name"] = filters.get("project")
	if filters.get("status"):
		project_filters["status"] = filters.get("status")

	projects = frappe.get_all(
		"Project",
		filters=project_filters,
		fields=[
			"name",
			"project_name",
			"estimated_costing",
			"total_costing_amount",
			"total_purchase_cost",
			"total_consumed_material_cost",
			"custom_budget_utilization",
		],
	)

	rows = []
	for p in projects:
		if not p.estimated_costing:
			continue

		actual_cost = (
			flt(p.total_costing_amount) + flt(p.total_purchase_cost) + flt(p.total_consumed_material_cost)
		)
		variance = flt(p.estimated_costing) - actual_cost

		rows.append(
			{
				"name": p.name,
				"project_name": p.project_name,
				"estimated_costing": p.estimated_costing,
				"actual_cost": actual_cost,
				"variance": variance,
				"variance_pct": (variance / flt(p.estimated_costing) * 100),
				"custom_budget_utilization": p.custom_budget_utilization,
				"over_budget": 1 if actual_cost > flt(p.estimated_costing) else 0,
			}
		)

	rows.sort(key=lambda r: r["variance"])
	return rows


def get_chart_data(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d["project_name"] for d in data],
			"datasets": [
				{"name": _("Estimated Cost"), "values": [flt(d["estimated_costing"]) for d in data]},
				{"name": _("Actual Cost"), "values": [flt(d["actual_cost"]) for d in data]},
			],
		},
		"type": "bar",
		"colors": ["#5e64ff", "#e24c4c"],
	}
