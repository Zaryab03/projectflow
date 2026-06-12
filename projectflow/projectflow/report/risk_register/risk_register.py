import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.project:
		frappe.throw(_("Please select a Project"))

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Risk"), "fieldname": "name", "fieldtype": "Link", "options": "Project Risk", "width": 120},
		{"label": _("Title"), "fieldname": "risk_name", "fieldtype": "Data", "width": 200},
		{"label": _("Category"), "fieldname": "category", "fieldtype": "Data", "width": 100},
		{"label": _("Probability"), "fieldname": "probability", "fieldtype": "Data", "width": 90},
		{"label": _("Impact"), "fieldname": "impact", "fieldtype": "Data", "width": 90},
		{"label": _("Risk Score"), "fieldname": "risk_score", "fieldtype": "Int", "width": 90},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
		{"label": _("Owner"), "fieldname": "owner_user", "fieldtype": "Link", "options": "User", "width": 150},
		{"label": _("Review Date"), "fieldname": "review_date", "fieldtype": "Date", "width": 100},
	]


def get_data(filters):
	risk_filters = {"project": filters.project}
	if filters.get("status"):
		risk_filters["status"] = filters.get("status")

	return frappe.get_all(
		"Project Risk",
		filters=risk_filters,
		fields=[
			"name",
			"risk_name",
			"category",
			"probability",
			"impact",
			"risk_score",
			"status",
			"owner_user",
			"review_date",
		],
		order_by="risk_score desc",
	)


def get_chart_data(data):
	open_risks = [d for d in data if d["status"] == "Open"]
	if not open_risks:
		return None

	by_category = {}
	for risk in open_risks:
		by_category[risk["category"]] = by_category.get(risk["category"], 0) + risk["risk_score"]

	return {
		"data": {
			"labels": list(by_category.keys()),
			"datasets": [{"name": _("Open Risk Score"), "values": list(by_category.values())}],
		},
		"type": "bar",
		"colors": ["#e24c4c"],
	}
