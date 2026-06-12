import frappe
from frappe import _


def validate(doc, method=None):
	validate_no_circular_dependency(doc)


def validate_no_circular_dependency(doc):
	"""Ensure none of the tasks this task depends on (transitively) depend back on this task."""
	visited = set()

	def depends_on_self(task_name):
		if task_name == doc.name:
			return True
		if task_name in visited:
			return False
		visited.add(task_name)
		for dep in frappe.get_all("Task Depends On", filters={"parent": task_name}, pluck="task"):
			if dep and depends_on_self(dep):
				return True
		return False

	for row in doc.depends_on:
		if row.task and depends_on_self(row.task):
			frappe.throw(
				_("Circular dependency detected: this task cannot depend on {0}").format(row.task)
			)


def on_update(doc, method=None):
	if doc.project:
		from projectflow.projectflow.events.critical_path import recalculate_critical_path
		from projectflow.projectflow.events.project import recalculate_scores

		recalculate_scores(doc.project)
		recalculate_critical_path(doc.project)


def on_trash(doc, method=None):
	if doc.project:
		from projectflow.projectflow.events.critical_path import recalculate_critical_path
		from projectflow.projectflow.events.project import recalculate_scores

		recalculate_scores(doc.project)
		recalculate_critical_path(doc.project)
