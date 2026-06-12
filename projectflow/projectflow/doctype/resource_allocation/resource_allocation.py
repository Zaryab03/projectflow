import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, getdate


class ResourceAllocation(Document):
	def validate(self):
		self.validate_dates()
		self.check_over_allocation()

	def validate_dates(self):
		if self.allocation_start_date and self.allocation_end_date and self.allocation_start_date > self.allocation_end_date:
			frappe.throw(_("Allocation Start Date cannot be after Allocation End Date"))

	def check_over_allocation(self):
		capacity = flt(frappe.db.get_value("Employee", self.employee, "custom_daily_capacity_hours")) or 8

		other_allocations = frappe.get_all(
			"Resource Allocation",
			filters={
				"employee": self.employee,
				"name": ["!=", self.name or ""],
				"allocation_start_date": ["<=", self.allocation_end_date],
				"allocation_end_date": [">=", self.allocation_start_date],
			},
			fields=["allocation_start_date", "allocation_end_date", "allocated_hours_per_day"],
		)

		if not other_allocations:
			return

		overloaded_days = []
		day = getdate(self.allocation_start_date)
		end = getdate(self.allocation_end_date)
		while day <= end:
			total_hours = flt(self.allocated_hours_per_day)
			for row in other_allocations:
				if getdate(row.allocation_start_date) <= day <= getdate(row.allocation_end_date):
					total_hours += flt(row.allocated_hours_per_day)
			if total_hours > capacity:
				overloaded_days.append((day, total_hours))
			day = add_days(day, 1)

		if overloaded_days:
			first_day, first_total = overloaded_days[0]
			frappe.msgprint(
				_(
					"{0} is over-allocated on {1} ({2} hrs vs {3} hrs capacity). "
					"Please review their workload."
				).format(
					frappe.bold(self.employee_name or self.employee),
					frappe.format(first_day, {"fieldtype": "Date"}),
					first_total,
					capacity,
				),
				title=_("Over-allocation Warning"),
				indicator="orange",
			)
