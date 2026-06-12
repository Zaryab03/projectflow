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
		{"label": _("Portfolio"), "fieldname": "name", "fieldtype": "Link", "options": "Project Portfolio", "width": 160},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
		{"label": _("Projects"), "fieldname": "project_count", "fieldtype": "Int", "width": 90},
		{"label": _("Avg Health Score"), "fieldname": "avg_health_score", "fieldtype": "Percent", "width": 130},
		{"label": _("Avg Risk Score"), "fieldname": "avg_risk_score", "fieldtype": "Percent", "width": 120},
		{"label": _("Total Estimated Cost"), "fieldname": "total_estimated_costing", "fieldtype": "Currency", "width": 150},
		{"label": _("Total Billed"), "fieldname": "total_billed_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Open Risks"), "fieldname": "open_risk_count", "fieldtype": "Int", "width": 100},
	]


def get_data(filters):
	portfolio_filters = {}
	if filters.get("portfolio"):
		portfolio_filters["name"] = filters.get("portfolio")

	portfolios = frappe.get_all(
		"Project Portfolio", filters=portfolio_filters, fields=["name", "status"]
	)

	rows = []
	for portfolio in portfolios:
		projects = frappe.get_all(
			"Project",
			filters={"custom_portfolio": portfolio.name},
			fields=[
				"name",
				"custom_health_score",
				"custom_risk_score",
				"estimated_costing",
				"total_billed_amount",
			],
		)

		project_count = len(projects)
		avg_health_score = (
			sum(flt(p.custom_health_score) for p in projects) / project_count if project_count else 0
		)
		avg_risk_score = (
			sum(flt(p.custom_risk_score) for p in projects) / project_count if project_count else 0
		)
		total_estimated_costing = sum(flt(p.estimated_costing) for p in projects)
		total_billed_amount = sum(flt(p.total_billed_amount) for p in projects)

		open_risk_count = 0
		if projects:
			open_risk_count = frappe.db.count(
				"Project Risk",
				filters={"project": ["in", [p.name for p in projects]], "status": "Open"},
			)

		rows.append(
			{
				"name": portfolio.name,
				"status": portfolio.status,
				"project_count": project_count,
				"avg_health_score": avg_health_score,
				"avg_risk_score": avg_risk_score,
				"total_estimated_costing": total_estimated_costing,
				"total_billed_amount": total_billed_amount,
				"open_risk_count": open_risk_count,
			}
		)

	return rows


def get_chart_data(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d["name"] for d in data],
			"datasets": [
				{"name": _("Avg Health Score"), "values": [round(d["avg_health_score"], 1) for d in data]},
				{"name": _("Avg Risk Score"), "values": [round(d["avg_risk_score"], 1) for d in data]},
			],
		},
		"type": "bar",
		"colors": ["#28a745", "#e24c4c"],
	}
