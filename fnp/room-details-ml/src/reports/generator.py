from jinja2 import Environment, FileSystemLoader
import os
import matplotlib.pyplot as plt
import json

class ReportGenerator:
    def __init__(self, report_data, output_dir):
        self.report_data = report_data
        self.output_dir = output_dir
        self.template_env = Environment(loader=FileSystemLoader('src/reports/templates'))

    def generate_visualizations(self):
        # Generate visualizations based on report data
        for room in self.report_data['rooms']:
            plt.figure()
            plt.title(f"Room Details for {room['name']}")
            plt.bar(['Area', 'Walls'], [room['area'], room['walls']])
            plt.xlabel('Details')
            plt.ylabel('Values')
            plt.savefig(os.path.join(self.output_dir, f"{room['name']}_details.png"))
            plt.close()

    def generate_report(self):
        # Load the HTML template
        template = self.template_env.get_template('report_template.html')
        
        # Generate visualizations
        self.generate_visualizations()

        # Prepare data for rendering
        report_context = {
            'title': 'Room Details Report',
            'rooms': self.report_data['rooms'],
            'images': [f"{room['name']}_details.png" for room in self.report_data['rooms']]
        }

        # Render the HTML report
        report_html = template.render(report_context)

        # Save the report to an HTML file
        with open(os.path.join(self.output_dir, 'room_details_report.html'), 'w') as f:
            f.write(report_html)

    def save_report_data(self):
        # Save report data as JSON for reference
        with open(os.path.join(self.output_dir, 'report_data.json'), 'w') as f:
            json.dump(self.report_data, f, indent=4)

    def create_report(self):
        self.generate_report()
        self.save_report_data()