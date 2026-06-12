import frappe
from frappe.tests.utils import FrappeTestCase


class TestProjectRisk(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_project(self):
		project = frappe.get_doc({"doctype": "Project", "project_name": frappe.generate_hash(length=10)})
		project.insert()
		return project

	def make_risk(self, project, probability="Medium", impact="Medium", status="Open"):
		risk = frappe.get_doc(
			{
				"doctype": "Project Risk",
				"risk_name": "Risk " + frappe.generate_hash(length=5),
				"project": project.name,
				"probability": probability,
				"impact": impact,
				"status": status,
			}
		)
		risk.insert()
		return risk

	def test_risk_score_calculated_from_probability_and_impact(self):
		project = self.make_project()

		risk = self.make_risk(project, probability="High", impact="High")
		self.assertEqual(risk.risk_score, 9)

		risk = self.make_risk(project, probability="Low", impact="Medium")
		self.assertEqual(risk.risk_score, 2)

	def test_open_risk_increases_project_risk_score(self):
		project = self.make_project()

		baseline = frappe.db.get_value("Project", project.name, "custom_risk_score")

		self.make_risk(project, probability="High", impact="High", status="Open")

		updated = frappe.db.get_value("Project", project.name, "custom_risk_score")
		self.assertGreater(updated, baseline or 0)

	def test_closed_risk_does_not_affect_project_risk_score(self):
		project = self.make_project()

		self.make_risk(project, probability="High", impact="High", status="Closed")

		score = frappe.db.get_value("Project", project.name, "custom_risk_score")
		self.assertEqual(score, 0)
