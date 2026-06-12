### ProjectFlow

ProjectFlow is a Jira/ClickUp/Asana-style project management layer built on top of ERPNext
(Frappe v15). Rather than duplicating ERPNext's Project and Task doctypes, it extends them
with the workflows modern teams expect, while reusing built-in features like assignments,
comments, tags, and costing wherever possible.

**What it adds:**

- **Agile delivery** — Sprints, Epics, story points, a Kanban task board, and sprint
  velocity/burndown reports.
- **Gantt & critical path** — Typed task dependencies (FS/SS/FF/SF) with an automatic
  forward/backward-pass critical path engine, slack calculation, and a "critical task"
  badge on the Gantt view.
- **Resource planning** — Resource Allocation records with per-employee daily capacity,
  over-allocation warnings, utilization/heatmap reports, and a Planned → Confirmed →
  Completed approval workflow.
- **Risk management** — A Project Risk register with auto-scored probability x impact,
  a risk register report, and automatic high-severity escalation notifications to risk
  owners and project managers.
- **Issue & bug tracking** — Severity, environment, and reproduction-steps fields added
  to ERPNext's Issue doctype, with a dedicated bug board and bug summary report.
- **Financials** — Budget utilization tracking, project profitability, and budget
  variance reports built directly from ERPNext's existing costing and billing fields.
- **Portfolio management** — A Project Portfolio doctype that rolls up health, risk,
  budget, and open-risk metrics across grouped projects.
- **Executive & team workspaces** — Purpose-built workspaces for project managers,
  delivery teams, and executives, each surfacing the reports and shortcuts relevant
  to that role.

Every feature is backed by automated tests and computed/maintained via Frappe's standard
hooks, scheduled jobs, and notification framework — no parallel infrastructure to maintain.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app projectflow
```

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

### License

mit
