import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate


class TestResourceAllocation(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_project(self):
		project = frappe.get_doc({"doctype": "Project", "project_name": frappe.generate_hash(length=10)})
		project.insert()
		return project

	def make_employee(self, daily_capacity_hours=8):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test " + frappe.generate_hash(length=5),
				"company": "Demo 1",
				"gender": "Prefer not to say",
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2020-01-01",
				"custom_daily_capacity_hours": daily_capacity_hours,
			}
		)
		employee.insert()
		return employee

	def make_allocation(self, employee, project, start_date, end_date, hours_per_day=8):
		allocation = frappe.get_doc(
			{
				"doctype": "Resource Allocation",
				"employee": employee.name,
				"project": project.name,
				"allocation_start_date": start_date,
				"allocation_end_date": end_date,
				"allocated_hours_per_day": hours_per_day,
			}
		)
		allocation.insert()
		return allocation

	def test_invalid_dates_blocked(self):
		project = self.make_project()
		employee = self.make_employee()

		allocation = frappe.get_doc(
			{
				"doctype": "Resource Allocation",
				"employee": employee.name,
				"project": project.name,
				"allocation_start_date": nowdate(),
				"allocation_end_date": add_days(nowdate(), -1),
				"allocated_hours_per_day": 8,
			}
		)
		self.assertRaises(frappe.ValidationError, allocation.insert)

	def test_over_allocation_warning_raised(self):
		project = self.make_project()
		employee = self.make_employee(daily_capacity_hours=8)

		self.make_allocation(employee, project, nowdate(), add_days(nowdate(), 5), hours_per_day=6)

		frappe.clear_messages()
		self.make_allocation(employee, project, nowdate(), add_days(nowdate(), 5), hours_per_day=4)

		messages = frappe.get_message_log()
		self.assertTrue(any("over-allocated" in m.get("message", "").lower() for m in messages))

	def test_no_warning_when_within_capacity(self):
		project = self.make_project()
		employee = self.make_employee(daily_capacity_hours=8)

		self.make_allocation(employee, project, nowdate(), add_days(nowdate(), 5), hours_per_day=4)

		frappe.clear_messages()
		self.make_allocation(employee, project, nowdate(), add_days(nowdate(), 5), hours_per_day=4)

		messages = frappe.get_message_log()
		self.assertFalse(any("over-allocated" in m.get("message", "").lower() for m in messages))
