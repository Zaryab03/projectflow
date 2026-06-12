import frappe
from frappe.utils import add_days, flt, getdate, nowdate


def recalculate_scores(project_name):
	project = frappe.get_doc("Project", project_name)
	tasks = frappe.get_all(
		"Task",
		filters={"project": project_name, "is_group": 0},
		fields=["status", "exp_end_date", "progress"],
	)

	total = len(tasks)
	today = getdate(nowdate())

	overdue_ratio = 0
	if total:
		overdue = sum(
			1
			for t in tasks
			if t.exp_end_date
			and getdate(t.exp_end_date) < today
			and t.status not in ("Completed", "Cancelled")
		)
		overdue_ratio = overdue / total

	budget_overrun_ratio = 0
	if project.estimated_costing:
		budget_overrun_ratio = max(
			0, (flt(project.total_costing_amount) - flt(project.estimated_costing)) / flt(project.estimated_costing)
		)

	open_risk_scores = frappe.get_all(
		"Project Risk",
		filters={"project": project_name, "status": "Open"},
		pluck="risk_score",
	)
	register_risk_factor = (sum(open_risk_scores) / len(open_risk_scores) / 9) if open_risk_scores else 0

	health_score = 100 - (overdue_ratio * 40) - (min(budget_overrun_ratio, 1) * 40) - (register_risk_factor * 20)
	risk_score = min(100, (overdue_ratio * 50) + (min(budget_overrun_ratio, 1) * 20) + (register_risk_factor * 30))

	forecast_completion_date = None
	percent_complete = flt(project.percent_complete)
	if project.expected_start_date and 0 < percent_complete < 100:
		elapsed_days = (today - getdate(project.expected_start_date)).days
		if elapsed_days > 0:
			total_estimated_days = elapsed_days * (100 / percent_complete)
			remaining_days = total_estimated_days - elapsed_days
			forecast_completion_date = add_days(today, round(remaining_days))

	actual_cost = (
		flt(project.total_costing_amount)
		+ flt(project.total_purchase_cost)
		+ flt(project.total_consumed_material_cost)
	)
	budget_utilization = (actual_cost / flt(project.estimated_costing) * 100) if project.estimated_costing else 0

	values = {
		"custom_health_score": max(0, min(100, health_score)),
		"custom_risk_score": max(0, min(100, risk_score)),
		"custom_budget_utilization": max(0, budget_utilization),
	}
	if forecast_completion_date:
		values["custom_forecast_completion_date"] = forecast_completion_date

	frappe.db.set_value("Project", project_name, values)


def recalculate_all_scores():
	for project_name in frappe.get_all("Project", filters={"status": "Open"}, pluck="name"):
		recalculate_scores(project_name)
