import frappe
from frappe.tests.utils import FrappeTestCase


class TestTaskDependencies(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_task(self, subject):
		task = frappe.get_doc({"doctype": "Task", "subject": subject})
		task.insert()
		return task

	def test_circular_dependency_is_blocked(self):
		task_a = self.make_task("ProjectFlow Test Task A")
		task_b = self.make_task("ProjectFlow Test Task B")

		# B depends on A
		task_b.append("depends_on", {"task": task_a.name, "dependency_type": "Finish to Start"})
		task_b.save()

		# A depends on B -> would create a cycle (A -> B -> A)
		task_a.append("depends_on", {"task": task_b.name, "dependency_type": "Finish to Start"})
		self.assertRaises(frappe.ValidationError, task_a.save)

	def test_non_circular_dependency_allowed(self):
		task_a = self.make_task("ProjectFlow Test Task C")
		task_b = self.make_task("ProjectFlow Test Task D")

		task_b.append("depends_on", {"task": task_a.name, "dependency_type": "Finish to Start"})
		task_b.save()

		self.assertEqual(task_b.depends_on[0].dependency_type, "Finish to Start")
