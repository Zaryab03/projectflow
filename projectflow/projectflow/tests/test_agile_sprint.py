import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate

from projectflow.projectflow.events.sprint import log_burndown_for_active_sprints


class TestAgileSprint(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_project(self):
		project = frappe.get_doc({"doctype": "Project", "project_name": frappe.generate_hash(length=10)})
		project.insert()
		return project

	def make_sprint(self, project, status="Planned"):
		sprint = frappe.get_doc(
			{
				"doctype": "Agile Sprint",
				"sprint_name": "Sprint " + frappe.generate_hash(length=5),
				"project": project.name,
				"status": status,
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 14),
			}
		)
		sprint.insert()
		return sprint

	def test_invalid_dates_blocked(self):
		project = self.make_project()
		sprint = frappe.get_doc(
			{
				"doctype": "Agile Sprint",
				"sprint_name": "Bad Date Sprint",
				"project": project.name,
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), -1),
			}
		)
		self.assertRaises(frappe.ValidationError, sprint.insert)

	def test_only_one_active_sprint_per_project(self):
		project = self.make_project()
		sprint1 = self.make_sprint(project, status="Active")

		sprint2 = frappe.get_doc(
			{
				"doctype": "Agile Sprint",
				"sprint_name": "Second Sprint",
				"project": project.name,
				"status": "Active",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 14),
			}
		)
		self.assertRaises(frappe.ValidationError, sprint2.insert)

	def test_burndown_log_created_for_active_sprint(self):
		project = self.make_project()
		sprint = self.make_sprint(project, status="Active")

		task = frappe.get_doc(
			{
				"doctype": "Task",
				"subject": "Sprint task " + frappe.generate_hash(length=5),
				"project": project.name,
				"custom_sprint": sprint.name,
				"custom_story_points": 5,
				"status": "Completed",
			}
		)
		task.insert()

		log_burndown_for_active_sprints()

		log = frappe.db.get_value(
			"Sprint Burndown Log",
			{"sprint": sprint.name, "date": nowdate()},
			["total_points", "completed_points", "remaining_points"],
			as_dict=True,
		)
		self.assertIsNotNone(log)
		self.assertEqual(log.total_points, 5)
		self.assertEqual(log.completed_points, 5)
		self.assertEqual(log.remaining_points, 0)
