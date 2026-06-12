import frappe
from frappe.utils import nowdate


def log_burndown_for_active_sprints():
	today = nowdate()

	for sprint in frappe.get_all("Agile Sprint", filters={"status": "Active"}, pluck="name"):
		tasks = frappe.get_all(
			"Task",
			filters={"custom_sprint": sprint, "is_group": 0},
			fields=["status", "custom_story_points"],
		)

		total_points = sum(t.custom_story_points or 0 for t in tasks)
		completed_points = sum(
			t.custom_story_points or 0 for t in tasks if t.status == "Completed"
		)
		remaining_points = total_points - completed_points

		existing = frappe.db.exists("Sprint Burndown Log", {"sprint": sprint, "date": today})
		if existing:
			frappe.db.set_value(
				"Sprint Burndown Log",
				existing,
				{
					"total_points": total_points,
					"completed_points": completed_points,
					"remaining_points": remaining_points,
				},
			)
		else:
			frappe.get_doc(
				{
					"doctype": "Sprint Burndown Log",
					"sprint": sprint,
					"date": today,
					"total_points": total_points,
					"completed_points": completed_points,
					"remaining_points": remaining_points,
				}
			).insert(ignore_permissions=True)
