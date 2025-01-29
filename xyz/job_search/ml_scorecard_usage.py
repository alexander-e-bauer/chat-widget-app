from ml_scorecard_manager import MerrillScorecardManager
from datetime import datetime


def run_example():
    manager = MerrillScorecardManager()
    output_file = f'Merrill_Growth_Scorecard_Example_{datetime.now().strftime("%Y%m%d")}.xlsx'
    manager.create_scorecard(output_file)

    # Sample advisors data
    advisors = {
        'LPB Private Wealth': [
            {
                'name': 'Dana Locniskar',
                'prior_year_assets': 1851987067.57,
                'current_strategic_flow': 54745725.09,
                'household_values': 11.11
            },
            {
                'name': 'Thomas Pursel',
                'prior_year_assets': 816864738.65,
                'current_strategic_flow': 24394134.24,
                'household_values': 5.99
            },
            {
                'name': 'Matthew Biddinger',
                'prior_year_assets': 398766463.96,
                'current_strategic_flow': 11661098.44,
                'household_values': 3.95
            }
        ],
        'NR Wealth Management': [
            {
                'name': 'John Rochow',
                'prior_year_assets': 213349516.21,
                'current_strategic_flow': 18047342.33,
                'household_values' : 8
            },
            {
                'name': 'Griffin Neinberg',
                'prior_year_assets': 388994896.34,
                'current_strategic_flow': 33533507.32,
                'household_values' : 7
            }
        ]
    }

    # Update basic advisor data
    for group, group_advisors in advisors.items():
        for advisor in group_advisors:
            advisor_data = {
                'name': advisor['name'],
                'group': group,
                'prior_year_assets': advisor['prior_year_assets'],
                'current_strategic_flow': advisor['current_strategic_flow'],
                'household_values': advisor['household_values']
            }
            manager.update_advisor_data(advisor_data)

    # Sample PC data for first 12 weeks
    for week in range(1, 13):
        for group, group_advisors in advisors.items():
            for advisor in group_advisors:
                # Simulate varying PC values with some randomness
                base_pc = 45000 if group == 'LPB Private Wealth' else 40000
                pc_variation = (week % 4) * 5000  # Cyclical variation
                pc_value = base_pc + pc_variation + (hash(advisor['name']) % 10000)  # Unique variation per advisor

                pc_data = {
                    'name': advisor['name'],
                    'group': group,
                    'week': week,
                    'pc_value': pc_value
                }
                manager.update_pc_data(pc_data)

    # Sample A/L data for previous and current year quarters
    current_year = datetime.now().year
    for year in [current_year - 1, current_year]:
        for quarter in range(1, 5):
            for group, group_advisors in advisors.items():
                for advisor in group_advisors:
                    # Simulate growing A/L values
                    base_al = advisor['prior_year_assets']
                    growth_factor = 1.0 + (0.02 * quarter)  # 2% growth per quarter
                    if year == current_year:
                        growth_factor += 0.05  # Additional 5% for current year

                    al_data = {
                        'name': advisor['name'],
                        'group': group,
                        'year': year,
                        'quarter': quarter,
                        'al_value': base_al * growth_factor
                    }
                    manager.update_al_data(al_data)

    manager.wb.save(output_file)
    print(f"Example scorecard created with sample data: {output_file}")


if __name__ == "__main__":
    run_example()