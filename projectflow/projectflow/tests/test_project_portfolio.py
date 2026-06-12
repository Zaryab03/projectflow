import frappe
from frappe.tests.utils import FrappeTestCase

from projectflow.projectflow.report.portfolio_overview.portfolio_overview import execute


class TestProjectPortfolio(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def make_portfolio(self):
		portfolio = frappe.get_doc(
			{"doctype": "Project Portfolio", "portfolio_name": "Portfolio " + frappe.generate_hash(length=5)}
		)
		portfolio.insert()
		return portfolio

	def make_project(self, portfolio, health_score=0, risk_score=0, estimated_costing=0):
		project = frappe.get_doc(
			{
				"doctype": "Project",
				"project_name": frappe.generate_hash(length=10),
				"custom_portfolio": portfolio.name,
				"estimated_costing": estimated_costing,
			}
		)
		project.insert()
		frappe.db.set_value(
			"Project",
			project.name,
			{"custom_health_score": health_score, "custom_risk_score": risk_score},
		)
		return project

	def test_portfolio_overview_aggregates_projects(self):
		portfolio = self.make_portfolio()
		self.make_project(portfolio, health_score=80, risk_score=20, estimated_costing=1000)
		self.make_project(portfolio, health_score=60, risk_score=40, estimated_costing=2000)

		_, data, _, _ = execute({"portfolio": portfolio.name})

		self.assertEqual(len(data), 1)
		row = data[0]
		self.assertEqual(row["project_count"], 2)
		self.assertEqual(row["avg_health_score"], 70)
		self.assertEqual(row["avg_risk_score"], 30)
		self.assertEqual(row["total_estimated_costing"], 3000)

	def test_portfolio_with_no_projects(self):
		portfolio = self.make_portfolio()

		_, data, _, _ = execute({"portfolio": portfolio.name})

		self.assertEqual(len(data), 1)
		row = data[0]
		self.assertEqual(row["project_count"], 0)
		self.assertEqual(row["avg_health_score"], 0)
