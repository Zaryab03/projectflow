## ProjectFlow

ProjectFlow is a Jira / ClickUp / Asana-style project management layer built on top of
**ERPNext (Frappe v15)**. Instead of duplicating ERPNext's `Project` and `Task` doctypes,
it extends them with the agile, resourcing, risk, financial, and reporting workflows that
modern delivery teams expect — while continuing to use Frappe's built-in assignments,
comments, tags, Kanban, Gantt, and costing features.

<img width="1366" height="601" alt="Screenshot from 2026-06-17 04-03-26" src="https://github.com/user-attachments/assets/3749f32a-7b10-4456-b035-917828839c1e" />


After installation you get three new Workspaces (**ProjectFlow Team**, **ProjectFlow
Manager**, **ProjectFlow Executive**) that act as your starting points for everything
below.

---

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Zaryab03/projectflow --branch main
bench --site your-site install-app projectflow
bench --site your-site migrate
```

ProjectFlow requires `erpnext` to be installed on the site (it is listed as a
`required_apps`).

---

## Modules & How to Use Them

### 1. Agile Delivery (Sprints, Epics, Kanban Board)

1. Open **ProjectFlow Team** workspace.
2. Create an **Epic** (large body of work spanning multiple sprints) under a Project.
3. Create an **Agile Sprint** for the project — give it a start/end date and set it to
   **Active** (only one sprint per project can be Active at a time).
4. On each **Task**, set:
   - `Sprint` — link it to the active sprint
   - `Epic` — link it to its parent epic (optional)
   - `Story Points` — effort estimate
   - `Board Status` — Backlog / To Do / In Progress / In Review / Done / Blocked
5. Open the **ProjectFlow Task Board** Kanban board (grouped by Board Status) to drag
   tasks through your workflow.
6. Track progress with:
   - **Sprint Velocity** report — committed vs. completed story points per sprint
   - **Sprint Burndown** report — actual vs. ideal remaining points over the sprint
     (a daily scheduled job logs a burndown snapshot automatically for every active sprint)

**Task Templates:** Use the **Task Template** doctype (with checklist items) and the
`create_task_from_template` API to spin up a standard set of tasks/checklists for
recurring work.

---

### 2. Gantt & Critical Path

1. Set dependencies on a Task as usual via **Task Depends On**, and choose a
   **Dependency Type**: Finish to Start, Start to Start, Finish to Finish, or
   Start to Finish.
2. Whenever a task is saved (and once daily via a scheduled job), ProjectFlow recalculates
   the project's critical path using a forward/backward-pass CPM algorithm:
   - `Slack (Days)` is set on every task
   - `Critical Path Task` is checked for any task with zero or negative slack
3. Open the Task **Gantt view** — critical tasks are badged automatically.
4. Use the **Critical Path** report (filter by project) to see every task's slack as a
   bar chart and quickly spot your bottleneck chain.

---

### 3. Resource Planning

1. Set `Daily Capacity (Hours)` on each **Employee** (defaults to 8).
2. Go to **Resource Allocation** (ProjectFlow Manager workspace) and create an
   allocation: pick the Employee, Project, optional Task, start/end dates, and
   `Allocated Hours / Day`.
3. If an employee's combined allocated hours on any day exceed their daily capacity,
   you'll get a non-blocking over-allocation warning — useful for spotting overbooked
   staff before confirming.
4. Each Resource Allocation has a **status** workflow:
   - **Planned** → (Projects Manager clicks **Confirm**) → **Confirmed**
   - **Confirmed** → (Projects User clicks **Complete**) → **Completed**
   - **Confirmed** → (Projects Manager clicks **Reopen**) → back to **Planned**
5. Review staffing with:
   - **Resource Utilization** report — capacity vs. allocated vs. actual hours
     (from Timesheets) per employee, with allocation % and utilization %
   - **Resource Heatmap** report — a calendar heatmap of total allocated hours per day

---

### 4. Risk Management

1. Create a **Project Risk** record under a Project: give it a title, category
   (Schedule / Budget / Resource / Technical / Scope / External), and set
   **Probability** and **Impact** (Low/Medium/High).
2. ProjectFlow automatically computes a `Risk Score` (1–9, Probability × Impact) and
   rolls open risks into the project's overall `Risk Score` and `Health Score`.
3. If a risk's score is **6 or higher and its status is Open**, an automatic system
   notification ("Project Risk Escalation") is sent to the risk's owner and to anyone
   with the **Projects Manager** role.
4. Use the **Risk Register** report (filter by project/status) to see all risks sorted
   by severity, with a chart of open risk score by category.
5. Update `Status` to Mitigated / Closed / Occurred as risks are managed — this
   automatically recalculates the parent project's scores.

---

### 5. Issue & Bug Tracking

ProjectFlow extends ERPNext's existing **Issue** doctype rather than creating a new one.

1. Create an **Issue** and link it to a `Project` (and optionally a `Task` — the task
   must belong to the same project, this is validated automatically).
2. Fill in the new **Bug Details** section:
   - `Severity` — Low / Medium / High / Critical
   - `Steps to Reproduce`
   - `Environment / Version`
3. Triage and track bugs on the **ProjectFlow Bug Board** Kanban (grouped by Issue
   status: Open / Replied / On Hold / Resolved / Closed).
4. Use the **Bug Summary** report (filters: project, severity, status) to see open
   issues by severity as a bar chart.

---

### 6. Financials — Profitability & Budget Variance

No new doctypes here — ProjectFlow reuses ERPNext's existing Project costing fields
(`Total Costing Amount`, `Total Purchase Cost`, `Total Consumed Material Cost`,
`Total Billed Amount`, `Gross Margin`, etc.) and `Estimated Costing`.

1. Set `Estimated Costing` on your Project as usual.
2. ProjectFlow automatically computes `Budget Utilization %` = actual cost (timesheet +
   purchase + consumed material) ÷ estimated cost, shown on the Project under
   **ProjectFlow Insights**.
3. Use:
   - **Project Profitability** report — billed vs. costing vs. gross margin % and
     client satisfaction per project
   - **Budget Variance** report — estimated vs. actual cost, variance %, and an
     "Over Budget" flag for every project with a budget set

---

### 7. Portfolio Management

1. Create a **Project Portfolio** (name, portfolio manager, status).
2. On each **Project**, set the `Portfolio` field to group it under that portfolio.
3. Open the **Portfolio Overview** report (optionally filter by portfolio) to see, per
   portfolio: number of projects, average health/risk score, total estimated cost,
   total billed amount, and count of open risks — with a chart comparing average
   health vs. risk across portfolios.

---

### 8. Workspaces

| Workspace | Audience | Highlights |
|---|---|---|
| **ProjectFlow Team** | Delivery teams | My Tasks, Sprint/Task Kanban boards, Bug board, Agile reports |
| **ProjectFlow Manager** | PMs / leads | Active projects, Gantt, Resource Allocation, Risk Register, Critical Path, Delayed Tasks |
| **ProjectFlow Executive** | Leadership | Portfolio Overview, Project Profitability, Budget Variance, Risk Register |

---

### Project "ProjectFlow Insights" Fields (quick reference)

| Field | Type | Meaning |
|---|---|---|
| Health Score | Percent | Blended score from overdue tasks, budget overrun, and open risk severity |
| Risk Score | Percent | Blended score from overdue ratio, budget overrun, and average open risk |
| Client Satisfaction | Rating | Manually set by the project manager |
| Forecast Completion Date | Date | Projected finish date |
| Budget Utilization | Percent | Actual cost as a % of Estimated Costing |
| Portfolio | Link | Groups the project under a Project Portfolio |

All scores recalculate automatically on task/risk changes and once daily via the
scheduler — no manual refresh needed.

---

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/projectflow
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### Running Tests

```bash
bench --site your-site run-tests --app projectflow
```

### License

mit
