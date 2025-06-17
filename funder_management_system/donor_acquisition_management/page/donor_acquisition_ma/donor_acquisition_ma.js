frappe.pages['donor-acquisition-ma'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Donor Acquisition Dashboard',
		single_column: true
	});

	page.set_secondary_action('Refresh', () => {
		filterWrapper.find('#generate-dashboard-btn').click();
	});

	page.set_primary_action('Go to Leads', () => {
		frappe.set_route('List', 'Organisation Lead');
	});
	page.add_inner_button('Budget vs Utilisation Report', () => {
		frappe.set_route('query-report', 'Budget vs Utilisation Report');
	}, 'Visit Reports');
	
	page.add_inner_button('Donor vs Utilisation Report', () => {
		frappe.set_route('query-report', 'Donation vs Utilisation Report');
	}, 'Visit Reports');
	
	page.add_inner_button('Budget Plan Report', () => {
		frappe.set_route('query-report', 'Budget Plan Report');
	}, 'Visit Reports');

	// Style buttons
	setTimeout(() => {
		$('.page-actions .btn-secondary').addClass('btn-custom-refresh');
		$('.page-actions .btn-primary').addClass('btn-custom-leads');
	}, 100);

	// ⬅️ Create wrapper with left padding
	const contentWrapper = $(`<div style="padding-left: 30px;"></div>`).appendTo(page.body);

	// Filter Section
	const filterWrapper = $(`
		<div class="filter-cards-wrapper mt-1 mb-4">
			<div class="card no-border no-shadow">
				<div class="card-body">
					<div class="row align-items-end">
						<div class="col-md-4">
							<div id="financial-year-field"></div>
						</div>
						<div class="col-md-4 mb-4 text-end">
							<button class="btn btn-primary" id="generate-dashboard-btn">Generate Dashboard</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	`).appendTo(contentWrapper);

	const filterFields = {};
	let allYears = [];
	let currentYear = null;

	function render_financial_year_control() {
		const container = filterWrapper.find('#financial-year-field');
		container.empty();

		filterFields.financial_year = frappe.ui.form.make_control({
			parent: container,
			df: {
				label: 'Financial Year',
				fieldtype: 'MultiSelectPills',
				fieldname: 'financial_year',
				options: allYears,
				placeholder: 'Click here to select more Financial Years'
			},
			render_input: true
		});

		if (currentYear) {
			filterFields.financial_year.set_value([currentYear]);
			setTimeout(() => {
				filterWrapper.find('#generate-dashboard-btn').click();
			}, 300);
		}
	}

	// Load data
	frappe.db.get_list('Financial Year', { fields: ['name'] }).then(res => {
		allYears = res.map(d => d.name);

		frappe.call({
			method: 'funder_management_system.utils.get_current_financial_year',
			callback: function (r) {
				if (r.message && allYears.includes(r.message)) {
					currentYear = r.message;
				}
				render_financial_year_control();
			}
		});
	});

	// ⬅️ Append to content wrapper with padding
	const cardsWrapper = $('<div class="number-cards-wrapper mb-4"></div>').appendTo(contentWrapper);
	const chartsWrapper = $('<div id="charts-wrapper" class="row mb-4"></div>').appendTo(contentWrapper);

	filterWrapper.on('click', '#generate-dashboard-btn', function () {
		const selectedYears = filterFields.financial_year.get_value();

		if (!selectedYears || selectedYears.length === 0) {
			frappe.msgprint(__('Please select at least one Financial Year'));
			return;
		}

		cardsWrapper.empty();
		chartsWrapper.empty();

		load_cards(selectedYears);
		load_charts(selectedYears);
	});

	function load_cards(financial_years) {
		frappe.call({
			method: "funder_management_system.donor_acquisition_management.page.donor_acquisition_ma.donor_acquisition_ma.get_number_cards",
			args: { financial_years: JSON.stringify(financial_years) },
			callback: function (r) {
				if (r.message) {
					const html = frappe.render_template("donor_acquisition_ma", { cards: r.message });
					cardsWrapper.html(html);
				}
			}
		});
	}

	function load_charts(financial_years) {
		const chartConfigs = [
			{
				chartTitle: "Leads distribution by Sources of Connection",
				method: "funder_management_system.donor_acquisition_management.page.donor_acquisition_ma.donor_acquisition_ma.get_leads_by_sources_of_connection",
				chartType: "bar",
				chartColors: ['#5e64ff']
			},
			{
				chartTitle: "Leads distribution by Thematic Area",
				method: "funder_management_system.donor_acquisition_management.page.donor_acquisition_ma.donor_acquisition_ma.get_leads_by_thematic_area",
				chartType: "donut",
				chartColors: ['#ff6f61']
			},
			{
				chartTitle: "Leads distribution by Category",
				method: "funder_management_system.donor_acquisition_management.page.donor_acquisition_ma.donor_acquisition_ma.get_leads_by_category",
				chartType: "donut",
				chartColors: ['#6c757d']
			},
			{
				chartTitle: "Lead Funnel Metrics - Stage Wise",
				method: "funder_management_system.donor_acquisition_management.page.donor_acquisition_ma.donor_acquisition_ma.get_leads_by_lead_stages",
				chartType: "pie",
				chartColors: ['#28a745']
			}
		];

		chartConfigs.forEach((config, index) => {
			const chartId = `dashboard-chart-${index + 1}`;
			const chartCol = $(`
				<div class="col-md-6 mb-4">
					<div id="${chartId}" class="dashboard-chart-box">Loading chart...</div>
				</div>
			`);
			chartsWrapper.append(chartCol);

			frappe.call({
				method: config.method,
				args: { financial_years },
				callback: function (r) {
					const el = document.getElementById(chartId);
					if (r.message && r.message.labels?.length > 0) {
						new frappe.Chart(el, {
							title: config.chartTitle,
							data: {
								labels: r.message.labels,
								datasets: r.message.datasets
							},
							type: config.chartType,
							height: 300,
							colors: config.chartColors
						});
					} else {
						el.innerHTML = `<p class="text-muted">No data available.</p>`;
					}
				}
			});
		});
	}
};
