import frappe
from frappe import _
from frappe.model.document import Document


class AgileSprint(Document):
	def validate(self):
		self.validate_dates()
		self.validate_single_active_sprint()

	def validate_dates(self):
		if self.start_date and self.end_date and self.start_date > self.end_date:
			frappe.throw(_("Start Date cannot be after End Date"))

	def validate_single_active_sprint(self):
		if self.status != "Active":
			return

		other_active = frappe.db.exists(
			"Agile Sprint",
			{"project": self.project, "status": "Active", "name": ["!=", self.name]},
		)
		if other_active:
			frappe.throw(
				_("Project {0} already has an active sprint: {1}").format(self.project, other_active)
			)
