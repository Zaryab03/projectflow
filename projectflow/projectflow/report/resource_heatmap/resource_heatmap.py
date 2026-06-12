import frappe
from frappe import _
from frappe.utils import add_days, date_diff, flt, get_datetime, getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.from_date or not filters.to_date:
		frappe.throw(_("Please set both From Date and To Date"))

	columns = get_columns()
	data, chart = get_data_and_chart(filters)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 120},
		{"label": _("Allocated Hours"), "fieldname": "allocated_hours", "fieldtype": "Float", "width": 130},
	]


def get_data_and_chart(filters):
	from_date = getdate(filters.from_date)
	to_date = getdate(filters.to_date)
	if date_diff(to_date, from_date) < 0:
		frappe.throw(_("From Date must be before or equal to To Date"))

	allocation_filters = {
		"allocation_start_date": ["<=", to_date],
		"allocation_end_date": [">=", from_date],
	}
	if filters.get("employee"):
		allocation_filters["employee"] = filters.get("employee")

	allocations = frappe.get_all(
		"Resource Allocation",
		filters=allocation_filters,
		fields=["allocation_start_date", "allocation_end_date", "allocated_hours_per_day"],
	)

	data = []
	data_points = {}

	day = from_date
	while day <= to_date:
		total_hours = 0.0
		for alloc in allocations:
			if getdate(alloc.allocation_start_date) <= day <= getdate(alloc.allocation_end_date):
				total_hours += flt(alloc.allocated_hours_per_day)

		data.append({"date": day, "allocated_hours": total_hours})
		timestamp = int(get_datetime(day).timestamp())
		data_points[timestamp] = total_hours

		day = add_days(day, 1)

	chart = {
		"type": "heatmap",
		"data": {"dataPoints": data_points},
		"countLabel": _("Hours"),
	}

	return data, chart
