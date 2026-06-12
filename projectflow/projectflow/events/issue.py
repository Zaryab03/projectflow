import frappe
from frappe import _


def validate(doc, method=None):
	if doc.custom_task and doc.project:
		task_project = frappe.db.get_value("Task", doc.custom_task, "project")
		if task_project and task_project != doc.project:
			frappe.throw(
				_("Task {0} belongs to Project {1}, not {2}").format(
					doc.custom_task, task_project, doc.project
				)
			)
