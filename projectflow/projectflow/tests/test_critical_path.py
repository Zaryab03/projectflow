import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate

from projectflow.projectflow.events.critical_path import recalculate_critical_path


class TestCriticalPath(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_project(self):
		project = frappe.get_doc({"doctype": "Project", "project_name": frappe.generate_hash(length=10)})
		project.insert()
		return project

	def make_task(self, project, subject, duration, depends_on=None):
		today = nowdate()
		task = frappe.get_doc(
			{
				"doctype": "Task",
				"subject": subject,
				"project": project.name,
				"exp_start_date": today,
				"exp_end_date": add_days(today, duration),
			}
		)
		for dep in depends_on or []:
			task.append("depends_on", {"task": dep, "dependency_type": "Finish to Start"})
		task.insert()
		return task

	def test_critical_path_identifies_longest_chain(self):
		project = self.make_project()

		task_a = self.make_task(project, "A", 2)
		task_b = self.make_task(project, "B", 3, depends_on=[task_a.name])
		task_c = self.make_task(project, "C", 1, depends_on=[task_a.name])
		task_d = self.make_task(project, "D", 1, depends_on=[task_b.name, task_c.name])

		recalculate_critical_path(project.name)

		def reload(t):
			return frappe.db.get_value(
				"Task", t.name, ["custom_is_critical", "custom_total_slack"], as_dict=True
			)

		a, b, c, d = (reload(t) for t in (task_a, task_b, task_c, task_d))

		# A -> B -> D is the critical (longest, zero-slack) path
		self.assertEqual(a.custom_is_critical, 1)
		self.assertEqual(b.custom_is_critical, 1)
		self.assertEqual(d.custom_is_critical, 1)

		# A -> C -> D has slack (2 days shorter than the critical path)
		self.assertEqual(c.custom_is_critical, 0)
		self.assertEqual(c.custom_total_slack, 2)
