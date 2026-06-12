import frappe
from frappe.tests.utils import FrappeTestCase


class TestIssueBugTracking(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_project(self):
		project = frappe.get_doc({"doctype": "Project", "project_name": frappe.generate_hash(length=10)})
		project.insert()
		return project

	def make_task(self, project):
		task = frappe.get_doc(
			{
				"doctype": "Task",
				"subject": "Task " + frappe.generate_hash(length=5),
				"project": project.name,
			}
		)
		task.insert()
		return task

	def make_issue(self, project=None, task=None, severity="Medium"):
		issue = frappe.get_doc(
			{
				"doctype": "Issue",
				"subject": "Bug " + frappe.generate_hash(length=5),
				"project": project.name if project else None,
				"custom_task": task.name if task else None,
				"custom_severity": severity,
			}
		)
		issue.insert()
		return issue

	def test_issue_can_be_linked_to_task_in_same_project(self):
		project = self.make_project()
		task = self.make_task(project)

		issue = self.make_issue(project=project, task=task, severity="High")
		self.assertEqual(issue.custom_task, task.name)
		self.assertEqual(issue.custom_severity, "High")

	def test_issue_task_must_belong_to_same_project(self):
		project_a = self.make_project()
		project_b = self.make_project()
		task = self.make_task(project_a)

		issue = frappe.get_doc(
			{
				"doctype": "Issue",
				"subject": "Mismatched bug",
				"project": project_b.name,
				"custom_task": task.name,
				"custom_severity": "High",
			}
		)
		self.assertRaises(frappe.ValidationError, issue.insert)

	def test_severity_defaults_to_medium(self):
		project = self.make_project()
		issue = frappe.get_doc(
			{
				"doctype": "Issue",
				"subject": "Default severity bug",
				"project": project.name,
			}
		)
		issue.insert()
		self.assertEqual(issue.custom_severity, "Medium")
