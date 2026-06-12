import frappe
from frappe.model.document import Document

SCORE_MAP = {"Low": 1, "Medium": 2, "High": 3}


class ProjectRisk(Document):
	def validate(self):
		self.risk_score = SCORE_MAP.get(self.probability, 2) * SCORE_MAP.get(self.impact, 2)

	def on_update(self):
		self.recalculate_project_risk_score()

	def on_trash(self):
		self.recalculate_project_risk_score()

	def recalculate_project_risk_score(self):
		from projectflow.projectflow.events.project import recalculate_scores

		if self.project:
			recalculate_scores(self.project)
