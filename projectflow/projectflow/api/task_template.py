import frappe
from frappe import _


@frappe.whitelist()
def create_task_from_template(template, project=None, exp_start_date=None):
	"""Create a new Task pre-filled from a Task Template."""
	tmpl = frappe.get_doc("Task Template", template)

	description = tmpl.description or ""
	if tmpl.checklist:
		items = "".join(f"<li>{frappe.utils.escape_html(row.title)}</li>" for row in tmpl.checklist)
		description += f"<ul>{items}</ul>"

	task = frappe.new_doc("Task")
	task.update(
		{
			"subject": tmpl.subject,
			"description": description,
			"priority": tmpl.priority,
			"expected_time": tmpl.expected_time,
			"custom_story_points": tmpl.story_points,
			"project": project,
			"exp_start_date": exp_start_date,
		}
	)
	task.insert()
	return task.name
