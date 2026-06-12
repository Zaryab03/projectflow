import frappe
from frappe.utils import add_days, date_diff, getdate


def recalculate_critical_path(project_name):
	"""Run the Critical Path Method over a project's tasks and flag critical tasks."""
	tasks = frappe.get_all(
		"Task",
		filters={"project": project_name, "is_group": 0},
		fields=["name", "exp_start_date", "exp_end_date"],
	)

	task_map = {
		t.name: t for t in tasks if t.exp_start_date and t.exp_end_date
	}
	if not task_map:
		return

	duration = {
		name: max(0, date_diff(t.exp_end_date, t.exp_start_date)) for name, t in task_map.items()
	}

	predecessors = {name: [] for name in task_map}
	successors = {name: [] for name in task_map}

	for name in task_map:
		deps = frappe.get_all(
			"Task Depends On", filters={"parent": name}, fields=["task", "dependency_type"]
		)
		for d in deps:
			if d.task in task_map:
				dep_type = d.dependency_type or "Finish to Start"
				predecessors[name].append((d.task, dep_type))
				successors[d.task].append((name, dep_type))

	order = _topological_order(task_map.keys(), predecessors)

	es, ef = {}, {}
	for name in order:
		candidates = [getdate(task_map[name].exp_start_date)]
		for pred, dep_type in predecessors[name]:
			if dep_type == "Finish to Start":
				candidates.append(ef[pred])
			elif dep_type == "Start to Start":
				candidates.append(es[pred])
			elif dep_type == "Finish to Finish":
				candidates.append(add_days(ef[pred], -duration[name]))
			elif dep_type == "Start to Finish":
				candidates.append(add_days(es[pred], -duration[name]))
		es[name] = max(candidates)
		ef[name] = add_days(es[name], duration[name])

	project_finish = max(ef.values())

	lf, ls = {}, {}
	for name in reversed(order):
		candidates = [project_finish]
		for succ, dep_type in successors[name]:
			if dep_type == "Finish to Start":
				candidates.append(ls[succ])
			elif dep_type == "Start to Start":
				candidates.append(add_days(ls[succ], duration[name]))
			elif dep_type == "Finish to Finish":
				candidates.append(lf[succ])
			elif dep_type == "Start to Finish":
				candidates.append(add_days(lf[succ], duration[name]))
		lf[name] = min(candidates)
		ls[name] = add_days(lf[name], -duration[name])

	for name in task_map:
		slack = date_diff(ls[name], es[name])
		frappe.db.set_value(
			"Task",
			name,
			{"custom_total_slack": slack, "custom_is_critical": 1 if slack <= 0 else 0},
			update_modified=False,
		)


def _topological_order(names, predecessors):
	visited = set()
	order = []

	def visit(name):
		if name in visited:
			return
		visited.add(name)
		for pred, _dep_type in predecessors.get(name, []):
			if pred in predecessors:
				visit(pred)
		order.append(name)

	for name in names:
		visit(name)

	return order


def recalculate_all_critical_paths():
	for project_name in frappe.get_all("Project", filters={"status": "Open"}, pluck="name"):
		recalculate_critical_path(project_name)
