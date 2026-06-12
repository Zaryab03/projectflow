// Extend ERPNext's Task list/Gantt settings with ProjectFlow's critical path info.
frappe.listview_settings["Task"] = frappe.listview_settings["Task"] || {};

(function () {
	const settings = frappe.listview_settings["Task"];

	settings.add_fields = settings.add_fields || [];
	settings.add_fields.push("custom_is_critical", "custom_total_slack");

	const original_popup = settings.gantt_custom_popup_html;
	settings.gantt_custom_popup_html = function (ganttobj, task) {
		let html = original_popup ? original_popup(ganttobj, task) : "";
		if (task.custom_is_critical) {
			html += `<p class="mb-1"><b class="text-danger">${__("Critical Path Task")}</b></p>`;
		}
		return html;
	};
})();
