import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate


class TestResourceAllocationWorkflow(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_project(self):
		project = frappe.get_doc({"doctype": "Project", "project_name": frappe.generate_hash(length=10)})
		project.insert()
		return project

	def make_employee(self):
		employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"first_name": "Test " + frappe.generate_hash(length=5),
				"company": "Demo 1",
				"gender": "Prefer not to say",
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2020-01-01",
			}
		)
		employee.insert()
		return employee

	def make_allocation(self, employee, project):
		allocation = frappe.get_doc(
			{
				"doctype": "Resource Allocation",
				"employee": employee.name,
				"project": project.name,
				"allocation_start_date": nowdate(),
				"allocation_end_date": add_days(nowdate(), 5),
				"allocated_hours_per_day": 4,
			}
		)
		allocation.insert()
		return allocation

	def test_default_status_is_planned(self):
		project = self.make_project()
		employee = self.make_employee()
		allocation = self.make_allocation(employee, project)

		self.assertEqual(allocation.status, "Planned")

	def test_confirm_and_complete_transitions(self):
		project = self.make_project()
		employee = self.make_employee()
		allocation = self.make_allocation(employee, project)

		allocation = apply_workflow(allocation, "Confirm")
		self.assertEqual(allocation.status, "Confirmed")

		allocation = apply_workflow(allocation, "Complete")
		self.assertEqual(allocation.status, "Completed")

	def test_reopen_transition(self):
		project = self.make_project()
		employee = self.make_employee()
		allocation = self.make_allocation(employee, project)

		allocation = apply_workflow(allocation, "Confirm")
		self.assertEqual(allocation.status, "Confirmed")

		allocation = apply_workflow(allocation, "Reopen")
		self.assertEqual(allocation.status, "Planned")

	def test_invalid_action_blocked(self):
		project = self.make_project()
		employee = self.make_employee()
		allocation = self.make_allocation(employee, project)

		self.assertRaises(frappe.ValidationError, apply_workflow, allocation, "Complete")
