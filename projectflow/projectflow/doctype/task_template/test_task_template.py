import frappe
from frappe.tests.utils import FrappeTestCase

from projectflow.projectflow.api.task_template import create_task_from_template


class TestTaskTemplate(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create_task_from_template(self):
		template = frappe.get_doc(
			{
				"doctype": "Task Template",
				"template_name": "Test Template - Code Review",
				"subject": "Review pull request",
				"priority": "High",
				"story_points": 3,
				"expected_time": 2,
				"description": "Review the diff for correctness.",
				"checklist": [
					{"title": "Check for security issues"},
					{"title": "Check test coverage"},
				],
			}
		)
		template.insert()

		task_name = create_task_from_template(template.name)
		task = frappe.get_doc("Task", task_name)

		self.assertEqual(task.subject, "Review pull request")
		self.assertEqual(task.priority, "High")
		self.assertEqual(task.custom_story_points, 3)
		self.assertIn("Check for security issues", task.description)
		self.assertIn("Check test coverage", task.description)
