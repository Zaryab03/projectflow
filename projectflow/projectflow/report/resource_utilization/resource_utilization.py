import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.from_date or not filters.to_date:
		frappe.throw(_("Please set both From Date and To Date"))

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 160},
		{"label": _("Capacity (Hrs)"), "fieldname": "capacity_hours", "fieldtype": "Float", "width": 110},
		{"label": _("Allocated (Hrs)"), "fieldname": "allocated_hours", "fieldtype": "Float", "width": 120},
		{"label": _("Actual (Hrs)"), "fieldname": "actual_hours", "fieldtype": "Float", "width": 110},
		{"label": _("Allocation %"), "fieldname": "allocation_pct", "fieldtype": "Percent", "width": 100},
		{"label": _("Utilization %"), "fieldname": "utilization_pct", "fieldtype": "Percent", "width": 100},
		{"label": _("Over-Allocated"), "fieldname": "over_allocated", "fieldtype": "Check", "width": 100},
	]


def get_data(filters):
	from_date = getdate(filters.from_date)
	to_date = getdate(filters.to_date)
	total_days = date_diff(to_date, from_date) + 1
	if total_days <= 0:
		frappe.throw(_("From Date must be before or equal to To Date"))

	employees = get_employees(filters)
	if not employees:
		return []

	allocations = get_allocations(filters, list(employees.keys()))
	actuals = get_actual_hours(filters, list(employees.keys()))

	rows = []
	for employee, emp in employees.items():
		capacity_hours = flt(total_days) * flt(emp.custom_daily_capacity_hours or 8)
		allocated_hours = 0.0

		for alloc in allocations.get(employee, []):
			overlap_start = max(getdate(alloc.allocation_start_date), from_date)
			overlap_end = min(getdate(alloc.allocation_end_date), to_date)
			overlap_days = date_diff(overlap_end, overlap_start) + 1
			if overlap_days > 0:
				allocated_hours += overlap_days * flt(alloc.allocated_hours_per_day)

		actual_hours = flt(actuals.get(employee, 0))

		rows.append(
			{
				"employee": employee,
				"employee_name": emp.employee_name,
				"capacity_hours": capacity_hours,
				"allocated_hours": allocated_hours,
				"actual_hours": actual_hours,
				"allocation_pct": (allocated_hours / capacity_hours * 100) if capacity_hours else 0,
				"utilization_pct": (actual_hours / capacity_hours * 100) if capacity_hours else 0,
				"over_allocated": 1 if allocated_hours > capacity_hours else 0,
			}
		)

	return rows


def get_employees(filters):
	employee_filters = {"status": "Active"}
	if filters.get("employee"):
		employee_filters["name"] = filters.get("employee")

	employees = frappe.get_all(
		"Employee",
		filters=employee_filters,
		fields=["name", "employee_name", "custom_daily_capacity_hours"],
	)
	return {e.name: e for e in employees}


def get_allocations(filters, employee_names):
	if not employee_names:
		return {}

	allocation_filters = {
		"employee": ["in", employee_names],
		"allocation_start_date": ["<=", filters.to_date],
		"allocation_end_date": [">=", filters.from_date],
	}
	if filters.get("project"):
		allocation_filters["project"] = filters.get("project")

	allocations = frappe.get_all(
		"Resource Allocation",
		filters=allocation_filters,
		fields=["employee", "allocation_start_date", "allocation_end_date", "allocated_hours_per_day"],
	)

	by_employee = {}
	for alloc in allocations:
		by_employee.setdefault(alloc.employee, []).append(alloc)
	return by_employee


def get_actual_hours(filters, employee_names):
	if not employee_names:
		return {}

	conditions = ["ts.employee in %(employees)s", "ts.start_date <= %(to_date)s", "ts.end_date >= %(from_date)s"]
	values = {
		"employees": tuple(employee_names),
		"from_date": filters.from_date,
		"to_date": filters.to_date,
	}

	if filters.get("project"):
		conditions.append("tsd.project = %(project)s")
		values["project"] = filters.get("project")

	rows = frappe.db.sql(
		f"""
		select ts.employee, sum(tsd.hours) as hours
		from `tabTimesheet Detail` tsd
		inner join `tabTimesheet` ts on ts.name = tsd.parent
		where {" and ".join(conditions)} and ts.docstatus < 2
		group by ts.employee
		""",
		values,
		as_dict=True,
	)

	return {row.employee: row.hours for row in rows}


def get_chart_data(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d["employee_name"] for d in data],
			"datasets": [
				{"name": _("Allocation %"), "values": [round(d["allocation_pct"], 1) for d in data]},
				{"name": _("Utilization %"), "values": [round(d["utilization_pct"], 1) for d in data]},
			],
		},
		"type": "bar",
		"colors": ["#5e64ff", "#28a745"],
	}
