import frappe
from frappe.tests.utils import FrappeTestCase


class TestProjectRiskNotification(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_project(self):
		project = frappe.get_doc({"doctype": "Project", "project_name": frappe.generate_hash(length=10)})
		project.insert()
		return project

	def make_risk(self, project, probability, impact, status="Open"):
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

	def get_alert(self):
		return frappe.get_doc("Notification", "Project Risk Escalation")

	def test_alert_configuration(self):
		alert = self.get_alert()
		self.assertEqual(alert.document_type, "Project Risk")
		self.assertEqual(alert.event, "Save")
		self.assertEqual(alert.enabled, 1)
		self.assertIn("doc.risk_score >= 6", alert.condition)

	def test_high_severity_open_risk_triggers_condition(self):
		project = self.make_project()
		risk = self.make_risk(project, probability="High", impact="High")  # risk_score = 9

		alert = self.get_alert()
		self.assertTrue(frappe.safe_eval(alert.condition, None, {"doc": risk}))

	def test_low_severity_risk_does_not_trigger_condition(self):
		project = self.make_project()
		risk = self.make_risk(project, probability="Low", impact="Low")  # risk_score = 1

		alert = self.get_alert()
		self.assertFalse(frappe.safe_eval(alert.condition, None, {"doc": risk}))

	def test_high_severity_closed_risk_does_not_trigger_condition(self):
		project = self.make_project()
		risk = self.make_risk(project, probability="High", impact="High", status="Closed")

		alert = self.get_alert()
		self.assertFalse(frappe.safe_eval(alert.condition, None, {"doc": risk}))
