import frappe
from frappe.tests.utils import FrappeTestCase

from projectflow.projectflow.events.project import recalculate_scores


class TestProjectProfitability(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_project(self, estimated_costing=0, total_costing_amount=0):
		project = frappe.get_doc(
			{
				"doctype": "Project",
				"project_name": frappe.generate_hash(length=10),
				"estimated_costing": estimated_costing,
			}
		)
		project.insert()
		if total_costing_amount:
			frappe.db.set_value("Project", project.name, "total_costing_amount", total_costing_amount)
		return project

	def test_budget_utilization_under_budget(self):
		project = self.make_project(estimated_costing=1000, total_costing_amount=400)

		recalculate_scores(project.name)

		utilization = frappe.db.get_value("Project", project.name, "custom_budget_utilization")
		self.assertEqual(utilization, 40)

	def test_budget_utilization_over_budget(self):
		project = self.make_project(estimated_costing=1000, total_costing_amount=1500)

		recalculate_scores(project.name)

		utilization = frappe.db.get_value("Project", project.name, "custom_budget_utilization")
		self.assertEqual(utilization, 150)

	def test_no_estimated_costing_gives_zero_utilization(self):
		project = self.make_project(estimated_costing=0)

		recalculate_scores(project.name)

		utilization = frappe.db.get_value("Project", project.name, "custom_budget_utilization")
		self.assertEqual(utilization, 0)
